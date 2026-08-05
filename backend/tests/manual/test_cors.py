import requests

# Test OPTIONS preflight request
url = "http://localhost:8000/api/v1/auth/forgot-password"
headers = {
    "Origin": "http://localhost:5137",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type"
}

print("Testing CORS preflight (OPTIONS) request...")
print(f"URL: {url}")
print(f"Origin: {headers['Origin']}")
print()

response = requests.options(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Status: {'✓ SUCCESS' if response.status_code == 200 else '✗ FAILED'}")
print()
print("Response Headers:")
for key, value in response.headers.items():
    if 'access-control' in key.lower() or 'allow' in key.lower():
        print(f"  {key}: {value}")