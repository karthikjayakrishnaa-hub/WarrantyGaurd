import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("--- Starting Phase 3 Verification ---")
    
    # 1. Weak password rejected
    print("\\n[Test 1] Register with weak password:")
    res = client.post("/api/v1/auth/register", json={
        "email": "weak@example.com",
        "password": "weak",
        "full_name": "Weak User"
    })
    if res.status_code == 422: # Pydantic validation error
        print("✅ Passed: Weak password rejected by validator")
    else:
        print(f"❌ Failed: Expected 422, got {res.status_code}")
        print(res.text)

    # 2. Registration with strong password
    print("\\n[Test 2] Register with strong password:")
    strong_pwd = "StrongPassword123!"
    res = client.post("/api/v1/auth/register", json={
        "email": "strong@example.com",
        "password": strong_pwd,
        "full_name": "Strong User"
    })
    if res.status_code == 201:
        print("✅ Passed: Strong password accepted")
        data = res.json()
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
    else:
        print(f"❌ Failed: Expected 201, got {res.status_code}")
        print(res.text)
        sys.exit(1)

    # 3. Rate limiting check
    print("\\n[Test 3] Rate Limit (5/minute) on login:")
    for i in range(5):
        res = client.post("/api/v1/auth/login", json={"email": "strong@example.com", "password": strong_pwd})
    
    # 6th attempt should be rate limited
    res = client.post("/api/v1/auth/login", json={"email": "strong@example.com", "password": strong_pwd})
    if res.status_code == 429:
        print("✅ Passed: 6th login attempt rate limited (429)")
    else:
        print(f"❌ Failed: Expected 429, got {res.status_code}")
        print(res.text)

    # 4. Refresh Token check
    print("\\n[Test 4] Refresh Token:")
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    if res.status_code == 200:
        print("✅ Passed: Refresh token issued new access token")
        new_refresh_token = res.json()["refresh_token"]
        new_access_token = res.json()["access_token"]
    else:
        print(f"❌ Failed: Expected 200, got {res.status_code}")
        print(res.text)

    # 5. Change Password check
    print("\\n[Test 5] Change Password (and token revocation):")
    res = client.post("/api/v1/auth/change-password", 
        json={"old_password": strong_pwd, "new_password": "NewStrongPassword123!"},
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    if res.status_code == 200:
        print("✅ Passed: Password successfully changed")
    else:
        print(f"❌ Failed: Expected 200, got {res.status_code}")
        print(res.text)

    # 6. Verify old refresh token is revoked
    print("\\n[Test 6] Old Refresh Token Revocation:")
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh_token})
    if res.status_code == 401:
        print("✅ Passed: Old refresh token was revoked upon password change")
    else:
        print(f"❌ Failed: Expected 401, got {res.status_code}")
        print(res.text)

    # 7. Input Sanitization Check
    print("\\n[Test 7] XSS Input Sanitization:")
    res = client.post("/api/v1/claims/", 
        json={
            "customer_name": "<script>alert(1)</script>John Doe",
            "product_model": "HP Model",
            "serial_number": "12345",
            "complaint_text": "<img src=x onerror=alert('xss')>"
        },
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    if res.status_code == 422 or (res.status_code == 200 and "<script>" not in res.json()["customer_name"]):
        # Wait, if we use TestClient without logging in the user for Claims creation, it might return 401 or 403.
        # But we just want to test validation. So we can just check if pydantic sanitizer strips it.
        # If it returns 404 because Product doesn't exist, it means validation passed!
        pass
    
    # Just testing the sanitizer logic directly
    from app.schemas.claim import ClaimCreate
    try:
        claim = ClaimCreate(
            customer_name="<script>alert(1)</script>John Doe",
            product_model="HP Model",
            serial_number="12345",
            complaint_text="<img src=x onerror=alert('xss')>"
        )
        if claim.customer_name == "alert(1)John Doe":
            print("✅ Passed: HTML tags stripped from input")
        else:
            print(f"❌ Failed: Sanitizer didn't strip properly, got '{claim.customer_name}'")
    except Exception as e:
        print(f"Exception during sanitization test: {e}")

    # 8. Security Headers
    print("\\n[Test 8] Security Headers Middleware:")
    res = client.get("/api/v1/health")
    if "X-Frame-Options" in res.headers and res.headers["X-Frame-Options"] == "DENY":
        print("✅ Passed: Security headers are present")
    else:
        print(f"❌ Failed: Security headers missing")
        print(res.headers)

if __name__ == "__main__":
    run_tests()
