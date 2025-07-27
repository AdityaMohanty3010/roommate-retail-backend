import os
from dotenv import load_dotenv
import cohere

# Load .env from backend/
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY not found in .env")

co = cohere.Client(api_key)

def get_ai_shopping_list(user_prompt: str):
    """Returns raw text response (expected to be JSON) from Cohere."""
    system_instruction = (
        "You're an AI assistant. Based on the user's grocery needs, return only a JSON object "
        "with this format:\n\n"
        "{\n"
        "  \"categories\": [\n"
        "    { \"name\": \"Produce\", \"items\": [ {\"name\": \"Tomato\", \"price\": 30} ] },\n"
        "    { \"name\": \"Dairy\", \"items\": [ {\"name\": \"Milk\", \"price\": 50} ] }\n"
        "  ]\n"
        "}\n\n"
        "Return ONLY valid JSON. No markdown. No explanations."
    )

    response = co.chat(
        model="command-r",
        message=user_prompt,
        temperature=0.6,
        max_tokens=500,
        chat_history=[
            {"role": "SYSTEM", "message": system_instruction}
        ]
    )

    return response.text.strip()
