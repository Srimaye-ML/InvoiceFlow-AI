
import os

from dotenv import load_dotenv
from google import genai


# Load API settings from the project's .env file.
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def get_gemini_client():
    """Create a Gemini API client using the configured API key."""

    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY was not found. "
            "Check that your .env file is in the project root."
        )

    return genai.Client(api_key=API_KEY)


def test_gemini_connection() -> str:
    """Send a small test request to Gemini."""

    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Reply with exactly: InvoiceFlow AI connection successful."
    )

    return response.text or "Gemini returned an empty response."
