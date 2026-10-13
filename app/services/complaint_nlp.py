import logging

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    nlp = None
    logging.warning("spaCy or en_core_web_sm not installed.")

def parse_complaint(text: str) -> dict:
    if not nlp or not text:
        return {
            "intent": "unknown",
            "severity": "unknown"
        }

    doc = nlp(text.lower())
    
    intent = "repair"
    severity = "low"
    
    # Simple heuristics based on lemma/tokens
    high_severity_keywords = {"dead", "crash", "smoke", "fire", "broken", "critical", "always", "constant", "flicker"}
    replace_keywords = {"refund", "replace", "return"}
    
    for token in doc:
        if token.lemma_ in high_severity_keywords or token.text in high_severity_keywords:
            severity = "high"
        if token.lemma_ in replace_keywords or token.text in replace_keywords:
            intent = "replace"
            
    return {
        "intent": intent,
        "severity": severity
    }
