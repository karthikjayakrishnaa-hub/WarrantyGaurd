import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Removed drop_all so it doesn't wipe your dev database when tests finish

def test_full_claim_pipeline():
    # 1. Create a claim
    response = client.post(
        "/api/v1/claims/",
        json={
            "customer_name": "Test User",
            "product_model": "Laptop Pro 15",
            "serial_number": "SN123456789",
            "complaint_text": "The screen is flickering constantly."
        }
    )
    assert response.status_code == 201
    claim = response.json()
    assert claim["customer_name"] == "Test User"
    assert claim["status"] == "submitted"
    claim_id = claim["id"]

    # 2. Upload evidence (invoice)
    with open("test_invoice.txt", "wb") as f:
        f.write(b"Mock invoice data")
    
    with open("test_invoice.txt", "rb") as f:
        response = client.post(
            f"/api/v1/claims/{claim_id}/evidence?type=invoice",
            files={"file": ("test_invoice.txt", f, "text/plain")}
        )
    assert response.status_code == 201
    evidence = response.json()
    assert evidence["type"] == "invoice"
    assert evidence["claim_id"] == claim_id
    assert "file_hash" in evidence

    import os
    os.remove("test_invoice.txt")

    # 3. Run Pipeline
    response = client.post(f"/api/v1/claims/{claim_id}/pipeline/run")
    assert response.status_code == 200
    updated_claim = response.json()
    
    assert updated_claim["status"] == "triaged"
    assert updated_claim["triage_result"] is not None
    assert updated_claim["triage_result"]["category"] == "needs_manual_review"
    assert "GEMINI_API_KEY missing" in updated_claim["triage_result"]["reasoning_summary"]


def test_duplicate_detection():
    from PIL import Image
    import io

    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    # Claim 1
    resp1 = client.post("/api/v1/claims/", json={"customer_name": "User 1", "product_model": "A", "serial_number": "1", "complaint_text": "text"})
    claim1_id = resp1.json()["id"]

    # Upload image for Claim 1
    client.post(
        f"/api/v1/claims/{claim1_id}/evidence?type=product_photo",
        files={"file": ("test.png", img_bytes, "image/png")}
    )
    
    # Run pipeline for Claim 1
    client.post(f"/api/v1/claims/{claim1_id}/pipeline/run")

    # Claim 2
    resp2 = client.post("/api/v1/claims/", json={"customer_name": "User 2", "product_model": "B", "serial_number": "2", "complaint_text": "text"})
    claim2_id = resp2.json()["id"]

    # Upload SAME image for Claim 2
    client.post(
        f"/api/v1/claims/{claim2_id}/evidence?type=product_photo",
        files={"file": ("test.png", img_bytes, "image/png")}
    )

    # Run pipeline for Claim 2
    resp3 = client.post(f"/api/v1/claims/{claim2_id}/pipeline/run")
    updated_claim2 = resp3.json()
    
    assert updated_claim2["triage_result"]["category"] == "duplicate_evidence"
    assert "Visually identical evidence found" in updated_claim2["triage_result"]["reasoning_summary"]
