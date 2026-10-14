import logging
import os
import threading
import numpy as np

# Force offline mode for Hugging Face Hub if weights are cached
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

try:
    import faiss
except ImportError:
    faiss = None
    logging.warning("FAISS not installed.")

_embedder = None
_embedder_lock = threading.Lock()

def get_embedder():
    global _embedder
    if _embedder is None:
        with _embedder_lock:
            if _embedder is None:
                try:
                    from sentence_transformers import SentenceTransformer
                    try:
                        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
                    except Exception:
                        # Fallback with online mode if weights weren't downloaded yet
                        os.environ.pop("HF_HUB_OFFLINE", None)
                        os.environ.pop("TRANSFORMERS_OFFLINE", None)
                        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
                except Exception as e:
                    logging.warning(f"SentenceTransformers not loaded: {e}")
    return _embedder

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage")

brand_indices = {}
brand_docs = {}


GENERIC_POLICY = """
Limited Hardware Warranty provides coverage for defects in materials and workmanship under normal use during the specified warranty period.
The standard warranty covers hardware components and required firmware if they fail due to defects in materials or craftsmanship.
During the warranty period, the manufacturer will, at its discretion, repair or replace the faulty component or product.
Replacement parts may be new or refurbished to a performance level equivalent to new.
The warranty does not cover damage resulting from accidents, drops, or liquid spills. This requires a separate Accidental Damage Protection (ADP) plan.
The warranty applies to hardware and firmware; it does not cover software applications, programs, or non-branded products/peripherals.
Issues arising from misuse, unauthorized repairs, or physical damage caused by the user are generally excluded as Customer-Induced Damage (CID).
Standard warranties cover battery failure due to defects but do not cover the natural degradation of battery life over time.
To avoid voiding your warranty, repairs should be performed by authorized service providers.
"""

def init_index_for_brand(brand: str):
    embedder = get_embedder()
    if not embedder or not faiss:
        return
        
    brand_slug = brand.lower().replace(" ", "_")
    file_path = os.path.join(STORAGE_DIR, f"{brand_slug}_warranty.txt")
    
    # Use specific file if it exists, otherwise use generic policy
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = GENERIC_POLICY.replace("manufacturer", brand)
        
    sentences = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
    
    if sentences:
        embeddings = embedder.encode(sentences)
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        
        brand_indices[brand] = index
        brand_docs[brand] = sentences

def retrieve_policy_clauses(query: str, brand: str = "Generic") -> list:
    embedder = get_embedder()
    if not embedder or not faiss:
        return ["RAG System Unavailable. Please check dependencies or warranty document."]
        
    if brand not in brand_indices:
        init_index_for_brand(brand)
        
    index = brand_indices.get(brand)
    doc_sentences = brand_docs.get(brand)
    
    if not index or not doc_sentences:
        return ["No policy clauses found."]
        
    query_emb = embedder.encode([query])
    faiss.normalize_L2(query_emb)
    
    k = 2
    distances, indices = index.search(query_emb, k)
    
    results = []
    for idx in indices[0]:
        if idx >= 0 and idx < len(doc_sentences):
            results.append(doc_sentences[idx])
            
    return results
