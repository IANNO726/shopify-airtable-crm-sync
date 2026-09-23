import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
load_dotenv()

# Instantiating the official Google GenAI Client
# Automatically looks for GEMINI_API_KEY environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def score_inbound_lead(lead_form_payload):
    """
    Evaluates customer raw text and meta information using Gemini 2.5 Flash 
    to automatically assign priority scoring for client routing.
    """
    company_name = lead_form_payload.get("company_name", "Unknown")
    company_size = lead_form_payload.get("company_size", "1-10")
    message_text = lead_form_payload.get("message", "")

    logging.info(f"Analyzing inbound business lead query from corporate entity: {company_name}...")

    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY variable is absent. Printing raw execution block for dry-run verification:")
        logging.info(f"Lead details extracted: Size={company_size}, Msg length={len(message_text)} characters.")
        return {"priority": "DRY_RUN", "reasoning": "Missing Gemini environment variable configuration."}

    client = genai.Client()

    system_instruction = (
        "You are an elite corporate Sales Development Representative bot. Your single job is to analyze inbound website contact forms "
        "and return a strict priority classification: HIGH, MEDIUM, or LOW. "
        "CRITERIA:\n"
        "- HIGH: Large company sizes (50+ employees) OR immediate buyer urgency mentioned in text.\n"
        "- MEDIUM: Mid-market companies (11-49 employees) with general project inquiries.\n"
        "- LOW: Freelancers, single-person entities, or highly ambiguous/vague requests.\n"
        "OUTPUT FORMAT: Return only the priority word followed by a single-sentence tactical justification."
    )

    prompt = f"Company: {company_name}\nCompany Size: {company_size}\nMessage Details: {message_text}"

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1  # Keep categorization deterministic and reliable
            )
        )
        ai_analysis = response.text.strip()
        logging.info(f"Lead Analysis Complete. Output: {ai_analysis}")
        return {"status": "success", "analysis": ai_analysis}
    except Exception as e:
        logging.error(f"AI Content Generation engine failed: {e}")
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    print("--- Running Inbound AI Lead Scorer Mock Test ---")
    mock_high_value_lead = {
        "company_name": "Wayne Enterprises Logistics",
        "company_size": "500+",
        "message": "We need an engineer to immediately automate our entire order delivery infrastructure pipeline. Budget is flexible, looking to sign a contract this Friday."
    }
    score_inbound_lead(mock_high_value_lead)
