import urllib.request
import urllib.parse
import json

BASE_URL = "https://pretty-laughter-production.up.railway.app"

def request(method, path, data=None, headers={}):
    url = f"{BASE_URL}{path}"
    req_headers = {"Content-Type": "application/json"}
    req_headers.update(headers)
    req_data = json.dumps(data).encode("utf-8") if data else None
    
    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            try:
                return response.status, json.loads(response.read().decode())
            except:
                return response.status, response.read().decode()
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, e.read().decode()

email = "test_analytics_agent_new@example.com"
password = "password123"
print("Registering...")
status, body = request("POST", "/register", {"email": email, "password": password})
print(status, body)

print("Logging in...")
status, body = request("POST", "/login", {"email": email, "password": password})
print("Login status:", status)
token = body.get("access_token") if isinstance(body, dict) else None

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Shorten URL
    print("Shortening...")
    status, body = request("POST", "/shortner", {"url": "https://example.com"}, headers)
    print("Shortener status:", status)
    
    if status == 200:
        short_url = body.get("short_url")
        print("Got short_url:", short_url)
        
        # 4. Click URL
        print("Clicking...")
        try:
            # We don't want it to actually follow redirects and print a massive html page,
            # we just want to hit it once. urllib follows redirects by default.
            urllib.request.urlopen(f"{BASE_URL}/{short_url}")
        except urllib.error.HTTPError as e:
            print("Click HTTP error:", e.code)
        except Exception as e:
            print("Click success (or other error):", e)
            
        # 5. Get all urls to check clicks
        print("Getting urls...")
        status, body2 = request("GET", f"/{email}/get_all_urls?page=1&size=10", headers=headers)
        print("Get all urls status:", status)
        if isinstance(body2, dict) and body2:
            first_key = list(body2.keys())[0]
            clicks = body2[first_key]["clicks"]
            print(f"Clicks for {short_url}: {clicks}")
        else:
            print("No URLs returned.")
