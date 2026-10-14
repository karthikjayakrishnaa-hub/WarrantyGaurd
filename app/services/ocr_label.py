import re
import logging

import os
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

from app.services.ocr_shared import get_ocr_engine, run_ocr_optimized

def __getattr__(name):
    if name == "ocr_engine":
        return get_ocr_engine()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def extract_label_info(file_path: str) -> dict:
    try:
        result = run_ocr_optimized(file_path)

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
        
        # Look for S/N or Serial No
        sn_match = re.search(r'(?:S/N|Serial(?: No)?\s*[:\-]?\s*)([A-Z0-9]+)', full_text, re.IGNORECASE)
        serial_number = sn_match.group(1) if sn_match else None
        
        # Look for Model
        model_match = re.search(r'Model\s*[:\-]?\s*([A-Za-z0-9\-]+)', full_text, re.IGNORECASE)
        model = model_match.group(1) if model_match else None
        
        return {
            "serial_number": serial_number,
            "model": model
        }
    except Exception as e:
        logging.error(f"Failed to run label OCR: {e}")
        return {}
