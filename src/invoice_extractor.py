
from datetime import date
from decimal import Decimal
import json
import time

from pydantic import BaseModel, Field, ConfigDict
from google.genai import errors

from src.gemini_client import get_gemini_client


class InvoiceData(BaseModel):
    """Structured information extracted from an invoice."""

    model_config = ConfigDict(str_strip_whitespace=True)

    supplier_name: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    currency: str = "INR"

    customer_name: str | None = None

    subtotal: Decimal | None = Field(default=None, ge=0)
    tax_amount: Decimal | None = Field(default=None, ge=0)
    total_amount: Decimal | None = Field(default=None, ge=0)
    amount_paid: Decimal | None = Field(default=None, ge=0)
    balance_due: Decimal | None = Field(default=None, ge=0)


def extract_invoice_with_gemini(invoice_text: str) -> InvoiceData:
    """Extract invoice fields using Gemini, retrying temporary API errors."""

    if not invoice_text.strip():
        raise ValueError("No invoice text was provided.")

    client = get_gemini_client()

    prompt = f"""
You are an invoice data extraction assistant.

Extract the invoice details from the supplied text.
Return only valid JSON with these exact keys:
supplier_name, invoice_number, invoice_date, due_date, currency,
customer_name, subtotal, tax_amount, total_amount, amount_paid, balance_due.

Rules:
- Dates must use YYYY-MM-DD format.
- Amounts must be numbers, not currency-formatted strings.
- Use null for missing or unclear values.
- Do not invent missing information.
- Use INR if the invoice clearly uses Indian rupees.

Invoice text:
{invoice_text}
"""

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            break

        except errors.APIError as error:
            if error.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == max_attempts - 1:
                raise RuntimeError(
                    "Gemini is temporarily unavailable after 3 attempts. "
                    "Your invoice text is still available. Please try again later."
                ) from error

            time.sleep(2 ** (attempt + 1))

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    data = json.loads(response.text)
    return InvoiceData.model_validate(data)
