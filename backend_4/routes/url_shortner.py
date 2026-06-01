from fastapi import HTTPException, BackgroundTasks,Request
from auth.auth_jwt import verify_access_token
from fastapi import APIRouter,Depends
from fastapi.responses import RedirectResponse
router = APIRouter()
import shortuuid

# pyrefly: ignore [missing-import]
from database.database_models import UrlShortner, users,clickanalytic
from database.database import get_db, SessionLocal
from database.schemas import post_url
from database.redis_1 import r
from limiter import limiter
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
    shorturl = shortuuid.uuid()[:6]
    # Check if this user has already shortened this exact URL before
    existing_url = db.query(UrlShortner).filter(
        UrlShortner.url == url.url, 
        UrlShortner.user_id == user_id
    ).first()
    if existing_url:
        return existing_url
    url_obj = UrlShortner(url=url.url, short_url=shorturl, user_id=user_id)
    db.add(url_obj)
    db.commit()
    db.refresh(url_obj)
    return url_obj

def record_click(short_url: str):
    db = SessionLocal()
    try:
        url_obj = db.query(UrlShortner).filter(UrlShortner.short_url == short_url).first()
        if url_obj:
            url_obj.clicks += 1
            click_event = clickanalytic(url_id=url_obj.id)
            db.add(click_event)
            db.commit()
    finally:
        db.close()

@router.get("/{short_url}")
@limiter.limit("10/minute")
def get_short_url(short_url:str, request:Request,background_tasks: BackgroundTasks, db=Depends(get_db)):
    cached_url=r.get(short_url)
    if cached_url:
        target_url = cached_url
        if not (target_url.startswith("http://") or target_url.startswith("https://") or target_url.startswith("//")):
            target_url = "https://" + target_url
        
        # Increment clicks and record analytics asynchronously in a background task
        # so the user is redirected immediately without waiting for DB writes!
        background_tasks.add_task(record_click, short_url)
        
        return RedirectResponse(url=target_url,status_code=302)
        
    url_obj=db.query(UrlShortner).filter(UrlShortner.short_url==short_url).first()
    
    if not url_obj:
        return {"message":"url not found"}
    r.set(short_url,url_obj.url,ex=3600)
    # 1. Increment total click count
    url_obj.clicks += 1
    
    # 2. Record detailed click analytic event
    click_event = clickanalytic(url_id=url_obj.id)
    db.add(click_event)
    
    db.commit()
    
    target_url = url_obj.url
    if not (target_url.startswith("http://") or target_url.startswith("https://") or target_url.startswith("//")):
        target_url = "https://" + target_url
    return RedirectResponse(url=target_url,status_code=302)


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
    
    # 1. Fetch all URL IDs belonging to this user
    url_ids = [item.id for item in url_objs]
    
    # 2. Delete all analytics records associated with these URLs first (preventing FK violation)
    db.query(clickanalytic).filter(clickanalytic.url_id.in_(url_ids)).delete(synchronize_session=False)
    
    # 3. Delete all the URLs for this user in one batch
    db.query(UrlShortner).filter(UrlShortner.user_id == user_id).delete(synchronize_session=False)
    
    db.commit()

    # Evict all the user's deleted URLs from Redis cache
    for item in url_objs:
        r.delete(item.short_url)

    return {"message": "all urls deleted successfully"}
@router.get("/{user_email}/get_all_urls")
@limiter.limit("5/minute")
def get_user_url(user_email:str,request:Request,db=Depends(get_db),current_user=Depends(verify_access_token)):
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
    url_obj = db.query(UrlShortner).filter(UrlShortner.user_id == user_id).all()
    final_obj = {}
    for item in url_obj:
        final_obj[item.id] = {
            "url": item.url, 
            "short_url": item.short_url, 
            "clicks": item.clicks,
            "created_at": item.created_at
        }

    return final_obj


@router.get("/analytics/{short_url}")
@limiter.limit("5/minute")
def get_analytics(short_url:str,request:Request,db=Depends(get_db),current_user=Depends(verify_access_token)):
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
    analytic_obj=db.query(clickanalytic).filter(clickanalytic.url_id==url_obj.id).all()
    # It is standard to return an empty list [] if there are no clicks yet, rather than raising a 404 error
    return analytic_obj