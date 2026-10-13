import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("--- Starting Phase 5 Verification (Backend APIs) ---")
    
    # Login as admin to ensure we have permissions
    res = client.post("/api/v1/auth/login", data={
        "username": "admin@warrantyguard.ai",
        "password": "StrongPassword123!"
    })
    if res.status_code != 200:
        print(f"[FAIL] Failed to login as admin: {res.text}")
        sys.exit(1)
    
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Setup: Create some claims
    print("\n[Setup] Creating dummy claims for bulk ops and search...")
    claims = []
    for i in range(3):
        res = client.post("/api/v1/claims/", json={
            "customer_name": f"Bulk Tester {i}",
            "product_model": "HP Spectre",
            "serial_number": f"SN-BLK-{i}",
            "complaint_text": "Battery drains fast and screen flickering"
        }, headers=headers)
        claims.append(res.json()["id"])
        
    print("\n[Test 1] Organization Settings (PATCH /organizations/me):")
    res = client.patch("/api/v1/organizations/me", json={"name": "WarrantyGuard Alpha"}, headers=headers)
    if res.status_code == 200 and res.json()["name"] == "WarrantyGuard Alpha":
        print("[PASS] Successfully updated organization name.")
    else:
        print(f"[FAIL] Expected 200 and name change, got {res.status_code}: {res.text}")

    print("\n[Test 2] Analytics Stats Endpoint (GET /stats):")
    res = client.get("/api/v1/stats", headers=headers)
    if res.status_code == 200:
        stats = res.json()
        if "overview" in stats and "total" in stats["overview"]:
            print(f"[PASS] Successfully retrieved stats. Total claims: {stats['overview']['total']}")
        else:
            print("[FAIL] Stats missing overview.")
    else:
        print(f"[FAIL] Expected 200, got {res.status_code}: {res.text}")

    print("\n[Test 3] Bulk Operations (POST /claims/bulk-update):")
    res = client.post("/api/v1/claims/bulk-update", json={
        "claim_ids": claims,
        "status": "approved"
    }, headers=headers)
    if res.status_code == 200 and len(res.json().get("updated_ids", [])) == 3:
        print(f"[PASS] Successfully bulk-approved {len(claims)} claims.")
    else:
        print(f"[FAIL] Expected 200, got {res.status_code}: {res.text}")

    print("\n[Test 4] Full-Text Search (GET /claims?search=flickering):")
    res = client.get("/api/v1/claims/?search=flickering", headers=headers)
    if res.status_code == 200:
        found_claims = res.json().get("claims", [])
        if len(found_claims) >= 3:
            print(f"[PASS] Successfully searched claims by complaint text. Found {len(found_claims)} matches.")
        else:
            print(f"[FAIL] Search didn't return expected matches. Got {len(found_claims)}")
    else:
        print(f"[FAIL] Expected 200, got {res.status_code}: {res.text}")

if __name__ == "__main__":
    run_tests()
