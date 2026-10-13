
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors


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
    """Send a small test request to Gemini with limited retries."""

    client = get_gemini_client()
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=(
                    "Reply with exactly: "
                    "InvoiceFlow AI connection successful."
                ),
            )

            return response.text or "Gemini returned an empty response."

        except errors.APIError as error:
            if error.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_attempts - 1:
                raise RuntimeError(
                    "Gemini is temporarily unavailable after 3 attempts. "
                    "Please try again later."
                ) from error

            time.sleep(2 ** (attempt + 1))
