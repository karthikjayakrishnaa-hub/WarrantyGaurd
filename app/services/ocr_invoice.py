import re
import logging

import os
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

try:
    from paddleocr import PaddleOCR
    ocr_engine = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=False)
except ImportError:
    ocr_engine = None
    logging.warning("PaddleOCR not installed.")

def extract_invoice_fields(file_path: str) -> dict:
    if not ocr_engine:
        return {}
        
    try:
        result = ocr_engine.ocr(file_path)
        raw_text = []
        if result:
            for item in result:
                if hasattr(item, 'rec_texts'):
                    raw_text.extend(item.rec_texts)
                elif isinstance(item, dict) and 'rec_texts' in item:
                    raw_text.extend(item['rec_texts'])
                elif isinstance(item, list):
                    for line in item:
                        if isinstance(line, (list, tuple)) and len(line) >= 2:
                            raw_text.append(line[1][0] if isinstance(line[1], (list, tuple)) else str(line[1]))
                
        full_text = " ".join(raw_text)
        
        # Very basic regex extractions for demo
        # Looking for YYYY-MM-DD
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', full_text)
        purchase_date = date_match.group(0) if date_match else None
        
        # Looking for a dollar amount
        price_match = re.search(r'\$\d+(?:\.\d{2})?', full_text)
        price_str = price_match.group(0) if price_match else None
        
        # Look for Model: XYZ
        model_match = re.search(r'Model\s*[:\-]?\s*([A-Za-z0-9\-]+)', full_text, re.IGNORECASE)
        model = model_match.group(1) if model_match else None
        
        return {
            "model": model,
            "purchase_date": purchase_date,
            "price": price_str
        }
    except Exception as e:
        logging.error(f"Failed to run invoice OCR: {e}")
        return {}
