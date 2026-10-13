import os
import logging

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        try:
            from paddleocr import PaddleOCR
            _ocr_engine = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=False)
        except Exception as e:
            logging.warning(f"PaddleOCR not available or failed to load: {e}")
            _ocr_engine = False
    return _ocr_engine if _ocr_engine is not False else None
