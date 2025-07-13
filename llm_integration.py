import logging
from dotenv import dotenv_values
import google.generativeai as genai
from google.generativeai import GenerationConfig

config = dotenv_values(".env")
api_key = config.get(GEMINI_API_KEY)
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

logger = logging.getLogger(__name__)
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.0-flash")

gen_config = GenerationConfig(max_output_tokens=150, temperature=0.1, top_p=0.9)

def summarize_email(email_text: str) -> str:
    if not email_text.strip():
        return "Email content is empty."
    prompt = (
        "Summarize this email in a concise, bullet-point style, preserving key facts:\n\n"
        f"{email_text}\n\nSummary:"
    )
    try:
        resp = model.generate_content(prompt, generation_config=gen_config)
        return resp.text.strip()
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        return "An error occurred during summarization."

def generate_reply(email_text: str) -> str:
    if not email_text.strip():
        return "Email content is empty."
    prompt = (
        "You are an AI email assistant. Write a clear, polite reply to the following email. "
        "Avoid repeating the original message.\n\n"
        f"Email:\n{email_text}\n\nReply:"
    )
    try:
        resp = model.generate_content(prompt, generation_config=gen_config)
        reply = resp.text.strip()
        if len(reply) < 10 or any(c in reply for c in ["�", "𒨷", "¶"]):
            return "Draft generation failed; reply was too short or malformed."
        return reply
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        return "An error occurred while generating the reply."

def generate_event_title(email_text: str) -> str:
    prompt = f"From this email, generate a short and relevant calendar event title:\n\n{email_text}\n\nTitle:"
    try:
        resp = model.generate_content(prompt, generation_config=gen_config)
        return resp.text.strip().split("\n")[0]
    except Exception as e:
        logger.error(f"Error generating event title: {e}")
        return "Meeting"
