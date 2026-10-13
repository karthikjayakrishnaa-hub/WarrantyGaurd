import sys
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("--- Starting Phase 4 Verification ---")
    
    # Login as admin to ensure we have permissions
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@warrantyguard.ai",
        "password": "StrongPassword123!"
    })
    if res.status_code != 200:
        print(f"[FAIL] Failed to login as admin: {res.text}")
        sys.exit(1)
    
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if we have a claim to test. We'll fetch claim #1. If not exists, we'll create one.
    res = client.get("/api/v1/claims/", headers=headers)
    claims = res.json()
    if isinstance(claims, dict) and "claims" in claims:
        claims = claims["claims"]
        
    if not claims:
        print("[Setup] Creating a dummy claim for testing...")
        res = client.post("/api/v1/claims/", json={
            "customer_name": "Phase 4 Tester",
            "product_model": "HP Spectre",
            "serial_number": "SN-P4-123",
            "complaint_text": "Battery drains fast"
        }, headers=headers)
        claim_id = res.json()["id"]
    else:
        claim_id = claims[0]["id"]
        
    print(f"\\n[Test 1] Trigger Async Pipeline (Claim #{claim_id}):")
    # Record start time to ensure it returns instantly (not blocked by ML)
    start_time = time.time()
    res = client.post(f"/api/v1/claims/{claim_id}/pipeline/run", headers=headers)
    end_time = time.time()
    
    if res.status_code == 202:
        print(f"[PASS] Pipeline triggered async. (Returned in {end_time - start_time:.4f} seconds)")
    else:
        print(f"[FAIL] Failed: Expected 202, got {res.status_code}")
        print(res.text)

    print("\\n[Test 2] Pipeline Status Endpoint:")
    res = client.get(f"/api/v1/claims/{claim_id}/pipeline/status", headers=headers)
    if res.status_code == 200:
        status_data = res.json()
        print(f"[PASS] Status retrieved successfully. (Current Status: {status_data['status']})")
    else:
        print(f"[FAIL] Failed: Expected 200, got {res.status_code}")
        print(res.text)
        
    print("\\n[Test 3] SSE Streaming Endpoint:")
    # SSE stream blocks, so we'll just read one or two lines to prove it works
    try:
        with client.stream("GET", f"/api/v1/sse/{claim_id}/progress", headers=headers) as response:
            if response.status_code == 200:
                print("[PASS] Connected to SSE stream successfully")
                lines_read = 0
                for line in response.iter_lines():
                    if line.strip():
                        print(f"   [SSE Event]: {line}")
                        lines_read += 1
                        if lines_read >= 2:
                            break
            else:
                print(f"[FAIL] Failed: SSE stream returned {response.status_code}")
    except BaseException as e:
        print(f"[FAIL] Failed: SSE stream threw exception: {e}")

    print("\\n[Test 4] SLA Overdue Endpoint:")
    res = client.get("/api/v1/sla/overdue", headers=headers)
    if res.status_code == 200:
        overdue_claims = res.json()
        print(f"[PASS] Retrieved overdue claims array. (Found {len(overdue_claims)} overdue claims)")
    else:
        print(f"[FAIL] Failed: Expected 200, got {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    run_tests()
