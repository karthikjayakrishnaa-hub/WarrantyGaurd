import os
import json
import logging
import base64

try:
    from groq import Groq
except ImportError:
    Groq = None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_review_summary(claim_data: dict, image_paths: list = None) -> dict:
    # 1. Early exit for duplicates
    if claim_data.get("is_duplicate"):
        return {
            "category": "duplicate_evidence",
            "reasoning_summary": "Visually identical evidence found in another claim.",
            "recommended_action": "Reject claim and investigate for fraud."
        }
        
    # 2. Check for API key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or not Groq:
        logging.warning("GROQ_API_KEY not found or groq not installed. Using fallback.")
        return {
            "category": "needs_manual_review",
            "reasoning_summary": "GROQ_API_KEY missing. Please review manually.",
            "recommended_action": "Review manually"
        }

    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""
        You are an AI Warranty Triage Assistant. Analyze the following warranty claim data and provide a decision.
        
        CRITICAL INSTRUCTION: Rely on the provided OCR data to understand what the images contained.
        
        Claim Data:
        {json.dumps(claim_data, indent=2)}
        
        Output valid JSON with the following keys:
        - "category": one of ["approved", "rejected", "needs_manual_review", "duplicate_evidence"]
        - "reasoning_summary": a 2-3 sentence explanation
        - "recommended_action": a short string of what to do next
        
        CRITICAL: Output ONLY raw valid JSON, no markdown formatting, no backticks.
        """
        
        content = [{"type": "text", "text": prompt}]
        # Using a text-only model from available list since Vision was decommissioned
        
        response = client.chat.completions.create(
            model='openai/gpt-oss-120b',
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content
        # Strip potential markdown formatting that Llama might add despite instructions
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        result = json.loads(response_text)
        
        return result
    except Exception as e:
        logging.error(f"GenAI generation failed: {e}")
        return {
            "category": "needs_manual_review",
            "reasoning_summary": f"GenAI generation failed: {e}. Please review manually.",
            "recommended_action": "Review manually"
        }
