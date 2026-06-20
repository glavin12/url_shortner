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

email = "bhagyalaxmient10@gmail.com" # The user's actual email is probably bhagyalaxmient10@gmail.com from appDataDir path? Wait, path is C:\Users\bhagy.
# Let's just create a completely valid url manually.

status, body = request("POST", "/login", {"email": "test_jwt@example.com", "password": "password123"})
print("login", status, body)
token = body.get("access_token") if isinstance(body, dict) else None
if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Let's get the urls for test_jwt@example.com
    status, body = request("GET", "/test_jwt@example.com/get_all_urls", headers=headers)
    print("get_all_urls", status, body)
    if isinstance(body, dict) and body:
        # Get the first URL id
        first_key = list(body.keys())[0]
        short_url = body[first_key]["short_url"]
        print("Got short_url:", short_url)
        
        status, body2 = request("GET", f"/analytics/{short_url}", headers=headers)
        print("analytics status:", status)
        print("analytics body:", body2)
