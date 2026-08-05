"""Simple script to test authentication endpoints."""
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_BASE = "http://localhost:8000/api/v1"

def test_signup():
    """Test signup endpoint."""
    print("\n=== Testing Signup ===")
    data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpass123"
    }
    
    try:
        req = Request(
            f"{API_BASE}/auth/signup",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Signup successful!")
            print(f"  User ID: {result['user']['id']}")
            print(f"  Email: {result['user']['email']}")
            print(f"  Name: {result['user']['name']}")
            print(f"  Token: {result['token'][:20]}...")
            return result['token']
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"✗ Signup failed: {e.code}")
        print(f"  Error: {error_body}")
        return None

def test_login(email, password):
    """Test login endpoint."""
    print("\n=== Testing Login ===")
    data = {
        "email": email,
        "password": password
    }
    
    try:
        req = Request(
            f"{API_BASE}/auth/login",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Login successful!")
            print(f"  User ID: {result['user']['id']}")
            print(f"  Token: {result['token'][:20]}...")
            return result['token']
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"✗ Login failed: {e.code}")
        print(f"  Error: {error_body}")
        return None

def test_me(token):
    """Test /auth/me endpoint."""
    print("\n=== Testing /auth/me ===")
    
    try:
        req = Request(
            f"{API_BASE}/auth/me",
            headers={'Authorization': f'Bearer {token}'},
            method='GET'
        )
        
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Get current user successful!")
            print(f"  User ID: {result['id']}")
            print(f"  Email: {result['email']}")
            print(f"  Name: {result['name']}")
            return True
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"✗ Get current user failed: {e.code}")
        print(f"  Error: {error_body}")
        return False

def test_logout(token):
    """Test logout endpoint."""
    print("\n=== Testing Logout ===")
    
    try:
        req = Request(
            f"{API_BASE}/auth/logout",
            headers={'Authorization': f'Bearer {token}'},
            method='POST'
        )
        
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Logout successful!")
            print(f"  Message: {result['message']}")
            return True
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"✗ Logout failed: {e.code}")
        print(f"  Error: {error_body}")
        return False

if __name__ == "__main__":
    print("Starting authentication endpoint tests...")
    
    # Test signup
    token = test_signup()
    
    if token:
        # Test /auth/me
        test_me(token)
        
        # Test logout
        test_logout(token)
        
        # Test login with the created user
        test_login("test@example.com", "testpass123")
    
    print("\n=== Tests Complete ===")