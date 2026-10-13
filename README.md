# WarrantyGuard AI - Phase 1

This is the Phase 1 backend setup for WarrantyGuard AI. It provides a foundational FastAPI service with SQLite, SQLAlchemy models, Alembic migrations, and stub endpoints for the claim processing pipeline.

## Setup Instructions

1.  **Clone / Navigate to the repository**
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\activate   # Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    Copy `.env.example` to `.env` and adjust as needed.
    ```bash
    cp .env.example .env
    ```
5.  **Run Database Migrations:**
    ```bash
    alembic upgrade head
    ```
6.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
7.  **Access API Docs:**
    Navigate to `http://localhost:8000/docs` in your browser.

## Run Tests
To run the test suite:
```bash
pytest tests/
```

## Pipeline Architecture (Phase 1 vs Future Phases)

The backend follows an 8-module pipeline order for processing claims:

1.  **Claim Submission** (Phase 1: Basic endpoint)
2.  **Invoice OCR** (Phase 1: Stub, Future: EasyOCR/PaddleOCR)
3.  **Product Label OCR** (Phase 1: Stub, Future: EasyOCR/PaddleOCR)
4.  **Complaint NLP** (Phase 1: Stub, Future: spaCy/GenAI)
5.  **Warranty Rule Engine** (Phase 1: Stub, Future: Logic implementation)
6.  **Duplicate Detection** (Phase 1: Stub, Future: ImageHash)
7.  **Policy RAG** (Phase 1: Stub, Future: Sentence Transformers + FAISS)
8.  **GenAI Report** (Phase 1: Stub, Future: Gemini API)

In this phase, the pipeline endpoint (`POST /api/v1/claims/{id}/pipeline/run`) walks through these stubs and marks the claim as `triaged` with placeholder data.
