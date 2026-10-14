import os
import logging
from PIL import Image

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

_ocr_engine = None
_ocr_cache = {}

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            _ocr_engine = PaddleOCR(
                ocr_version="PP-OCRv4",
                lang="en",
                enable_mkldnn=False,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
            )
        except Exception as e:
            logging.warning(f"PaddleOCR not available or failed to load: {e}")
            _ocr_engine = False
    return _ocr_engine if _ocr_engine is not False else None

def run_ocr_optimized(file_path: str):
    """Run OCR with image size normalization and memory caching for maximum speed."""
    if not file_path or not os.path.exists(file_path):
        return None

    # Check cache by file hash & mtime
    try:
        mtime = os.path.getmtime(file_path)
        cache_key = f"{file_path}_{mtime}"
        if cache_key in _ocr_cache:
            return _ocr_cache[cache_key]
    except Exception:
        cache_key = None

    ocr_engine = get_ocr_engine()
    if not ocr_engine:
        return None

    target_path = file_path
    temp_scaled_path = None
    try:
        # Pre-scale image if oversized (>1280px) to prevent deep convolution bottleneck
        with Image.open(file_path) as img:
            w, h = img.size
            max_dim = max(w, h)
            if max_dim > 1280:
                scale = 1280.0 / max_dim
                new_w, new_h = int(w * scale), int(h * scale)
                scaled_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                temp_scaled_path = f"{file_path}_scaled.jpg"
                scaled_img.convert("RGB").save(temp_scaled_path, quality=90)
                target_path = temp_scaled_path

        result = ocr_engine.ocr(target_path)
        if cache_key:
            _ocr_cache[cache_key] = result
        return result
    except Exception as e:
        logging.error(f"OCR inference failed for {file_path}: {e}")
        return None
    finally:
        if temp_scaled_path and os.path.exists(temp_scaled_path):
            try:
                os.remove(temp_scaled_path)
            except Exception:
                pass

