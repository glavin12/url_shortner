from fastapi import HTTPException, BackgroundTasks,Request,Query    
from auth.auth_jwt import verify_access_token
from fastapi import APIRouter,Depends
from fastapi.responses import RedirectResponse, FileResponse
from datetime import datetime
from user_agents import parse
from pathlib import Path
router = APIRouter()
import shortuuid
import re

# pyrefly: ignore [missing-import]
from database.database_models import UrlShortner, users,clickanalytic
from database.database import get_db, SessionLocal
from database.schemas import post_url, AnalyticsClick, AnalyticsSummary
from database.redis_1 import r
from limiter import limiter


# Reserved aliases that conflict with existing API route segments.
# Users cannot use these as custom aliases to prevent routing collisions.
RESERVED_ALIASES = {
    "register", "login", "logout", "token", "refresh_token",
    "shortner", "delete", "get_all_urls", "delete_all_urls", "analytics",
    "docs", "redoc", "openapi.json", "api", "admin", "health", "status",
    "qr",
}

@router.post("/shortner")
@limiter.limit("5/minute")
async def shortner(
    url: post_url,request:Request,
    db = Depends(get_db),current_user = Depends(verify_access_token)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    # Determine the short URL: use custom alias if provided, otherwise generate random
    if url.custom_alias:
        alias = url.custom_alias.strip().lower()
        # Block reserved route names
        if alias in RESERVED_ALIASES:
            raise HTTPException(
                status_code=400,
                detail=f"'{alias}' is a reserved word and cannot be used as a custom alias"
            )
        # Check if this alias is already taken by anyone
        existing_alias = db.query(UrlShortner).filter(UrlShortner.short_url == alias).first()
        if existing_alias:
            raise HTTPException(
                status_code=409,
                detail=f"The alias '{alias}' is already taken. Please choose a different one."
            )
        shorturl = alias
    else:
        shorturl = shortuuid.uuid()[:6]
    
    # Check if this user has already shortened this exact URL before
    # Only do this if they didn't provide a custom alias, because if they want a custom alias,
    # they want a NEW link for the same destination.
    if not url.custom_alias:
        existing_url = db.query(UrlShortner).filter(
            UrlShortner.url == url.url, 
            UrlShortner.user_id == user_id
        ).first()
        if existing_url:
            return existing_url
    url_obj = UrlShortner(
        url=url.url, 
        short_url=shorturl, 
        user_id=user_id,
        expires_at=url.expires_at
    )
    db.add(url_obj)
    db.commit()
    db.refresh(url_obj)
    
    return url_obj

def record_click(short_url: str, user_agent: str = None, referrer: str = None):
    db = SessionLocal()
    try:
        url_obj = db.query(UrlShortner).filter(UrlShortner.short_url == short_url).first()
        if url_obj:
            url_obj.clicks += 1
            
            # Parse user agent
            browser = None
            os = None
            if user_agent:
                ua = parse(user_agent)
                browser = f"{ua.browser.family} {ua.browser.version_string}" if ua.browser.family else None
                os = f"{ua.os.family} {ua.os.version_string}" if ua.os.family else None
            
            click_event = clickanalytic(
                url_id=url_obj.id,
                browser=browser,
                os=os,
                referrer=referrer
            )
            db.add(click_event)
            db.commit()
    finally:
        db.close()

@router.get("/{short_url}")
@limiter.limit("10/minute")
def get_short_url(short_url:str, request:Request,background_tasks: BackgroundTasks, db=Depends(get_db)):
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")
    
    cached_url=r.get(short_url)
    if cached_url:
        target_url = cached_url
        if not (target_url.startswith("http://") or target_url.startswith("https://") or target_url.startswith("//")):
            target_url = "https://" + target_url
        
        # Increment clicks and record analytics asynchronously in a background task
        # so the user is redirected immediately without waiting for DB writes!
        background_tasks.add_task(record_click, short_url, user_agent, referrer)
        
        response = RedirectResponse(url=target_url,status_code=302)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
        
    url_obj=db.query(UrlShortner).filter(UrlShortner.short_url==short_url).first()
    
    if not url_obj:
        return {"message":"url not found"}
    
    # Check if link has expired
    if url_obj.expires_at and url_obj.expires_at < datetime.utcnow():
        return {"message":"This link has expired","expired_at":url_obj.expires_at}
    
    r.set(short_url,url_obj.url,ex=3600)
    # 1. Increment total click count
    url_obj.clicks += 1
    
    # 2. Record detailed click analytic event with browser, OS, referrer
    ua = parse(user_agent) if user_agent else None
    browser = f"{ua.browser.family} {ua.browser.version_string}" if ua and ua.browser.family else None
    os = f"{ua.os.family} {ua.os.version_string}" if ua and ua.os.family else None
    
    click_event = clickanalytic(
        url_id=url_obj.id,
        browser=browser,
        os=os,
        referrer=referrer
    )
    db.add(click_event)
    
    db.commit()
    
    target_url = url_obj.url
    if not (target_url.startswith("http://") or target_url.startswith("https://") or target_url.startswith("//")):
        target_url = "https://" + target_url
        
    response = RedirectResponse(url=target_url,status_code=302)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@router.delete("/delete/{short_url}")
@limiter.limit("5/minute")
def delete_url(short_url:str,request:Request,db=Depends(get_db),current_user=Depends(verify_access_token)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    url_obj=db.query(UrlShortner).filter(UrlShortner.short_url==short_url).first()
    if not url_obj:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    if url_obj.user_id != user_id:
        raise HTTPException(
            status_code=401,
            detail="unauthorised"
        )
    temp=url_obj.url
    # Delete associated analytics records first to prevent foreign key constraint violations
    db.query(clickanalytic).filter(clickanalytic.url_id == url_obj.id).delete()
    db.delete(url_obj)
    db.commit()
   
    # Evict the deleted URL from Redis cache
    r.delete(short_url)
   

    return temp

@router.delete("/{user_email}/delete_all_urls")
@limiter.limit("3/minute")
def delete_all_urls(user_email:str,request:Request,db=Depends(get_db),current_user=Depends(verify_access_token)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    if current_user["sub"] != user_email:
        raise HTTPException(
            status_code=401,
            detail="unauthorised"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
        
    url_objs = db.query(UrlShortner).filter(UrlShortner.user_id == user_id).all()
    if not url_objs:
        raise HTTPException(
            status_code=404,
            detail="No URLs found to delete"
        )
    
    # 1. Fetch all URL IDs and short_urls belonging to this user
    url_ids = [item.id for item in url_objs]
    short_urls = [item.short_url for item in url_objs]
    
    # 2. Delete all analytics records associated with these URLs first (preventing FK violation)
    db.query(clickanalytic).filter(clickanalytic.url_id.in_(url_ids)).delete(synchronize_session=False)
    
    # 3. Delete all the URLs for this user in one batch
    db.query(UrlShortner).filter(UrlShortner.user_id == user_id).delete(synchronize_session=False)
    
    db.commit()

    # Evict all the user's deleted URLs from Redis cache using pre-fetched strings
    for short_url in short_urls:
        r.delete(short_url)

    return {"message": "all urls deleted successfully"}
@router.get("/{user_email}/get_all_urls")
@limiter.limit("5/minute")
def get_user_url(
    user_email:str,
    request:Request,
    page:int=Query(1,ge=1),
    size:int=Query(10,ge=1,le=100),
    search:str=Query(None,description="Search in URL or short_url"),
    min_clicks:int=Query(None,ge=0,description="Filter by minimum clicks"),
    max_clicks:int=Query(None,ge=0,description="Filter by maximum clicks"),
    created_after:datetime=Query(None,description="Filter by created after date"),
    created_before:datetime=Query(None,description="Filter by created before date"),
    expired:bool=Query(None,description="Filter by expiration status (true=expired, false=active)"),
    db=Depends(get_db),
    current_user=Depends(verify_access_token)
):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    if current_user["sub"] != user_email:
        raise HTTPException(
            status_code=401,
            detail="unauthorised"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    # Build query with filters
    query = db.query(UrlShortner).filter(UrlShortner.user_id == user_id)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (UrlShortner.url.ilike(search_pattern)) | 
            (UrlShortner.short_url.ilike(search_pattern))
        )
    
    if min_clicks is not None:
        query = query.filter(UrlShortner.clicks >= min_clicks)
    
    if max_clicks is not None:
        query = query.filter(UrlShortner.clicks <= max_clicks)
    
    if created_after:
        query = query.filter(UrlShortner.created_at >= created_after)
    
    if created_before:
        query = query.filter(UrlShortner.created_at <= created_before)
    
    if expired is not None:
        now = datetime.utcnow()
        if expired:
            # Show only expired links
            query = query.filter(UrlShortner.expires_at.isnot(None), UrlShortner.expires_at < now)
        else:
            # Show only active links (no expiration or not yet expired)
            query = query.filter(
                (UrlShortner.expires_at.is_(None)) | (UrlShortner.expires_at >= now)
            )
    
    # Apply pagination using .offset() and .limit()
    url_obj = query.offset((page - 1) * size).limit(size).all()
    final_obj = {}
    for item in url_obj:
        final_obj[item.id] = {
            "url": item.url, 
            "short_url": item.short_url, 
            "clicks": item.clicks,
            "created_at": item.created_at,
            "expires_at": item.expires_at,
            "qr_code_path": item.qr_code_path
        }

    return final_obj


@router.get("/analytics/{short_url}", response_model=list[AnalyticsClick])
@limiter.limit("5/minute")
def get_analytics(short_url:str,request:Request,page:int=Query(1,ge=1),size:int=Query(10,ge=1,le=100),db=Depends(get_db),current_user=Depends(verify_access_token)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    url_obj = db.query(UrlShortner).filter(UrlShortner.short_url == short_url).first()
    if not url_obj:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    if url_obj.user_id != user_id:
        raise HTTPException(
            status_code=401,
            detail="unauthorised"
        )
    # Apply pagination using .offset() and .limit() on the clickanalytic events
    analytic_obj = db.query(clickanalytic).filter(clickanalytic.url_id == url_obj.id).offset((page - 1) * size).limit(size).all()
    # It is standard to return an empty list [] if there are no clicks yet, rather than raising a 404 error
    return analytic_obj

@router.get("/analytics/{short_url}/summary", response_model=AnalyticsSummary)
@limiter.limit("5/minute")
def get_analytics_summary(short_url:str,request:Request,db=Depends(get_db),current_user=Depends(verify_access_token)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    url_obj = db.query(UrlShortner).filter(UrlShortner.short_url == short_url).first()
    if not url_obj:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    if url_obj.user_id != user_id:
        raise HTTPException(
            status_code=401,
            detail="unauthorised"
        )
    
    # Get recent 10 clicks with details
    recent_clicks = db.query(clickanalytic).filter(
        clickanalytic.url_id == url_obj.id
    ).order_by(clickanalytic.clicked_at.desc()).limit(10).all()
    
    return {
        "total_clicks": url_obj.clicks,
        "recent_clicks": recent_clicks
    }

@router.get("/qr/{short_url}")
@limiter.limit("10/minute")
def get_qr_code(short_url:str,request:Request,db=Depends(get_db)):
    url_obj = db.query(UrlShortner).filter(UrlShortner.short_url == short_url).first()
    if not url_obj:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    if not url_obj.qr_code_path or not os.path.exists(url_obj.qr_code_path):
        raise HTTPException(
            status_code=404,
            detail="QR code not found"
        )
    return FileResponse(url_obj.qr_code_path, media_type="image/png")