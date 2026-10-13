
# InvoiceFlow AI

InvoiceFlow AI is a GenAI-powered invoice processing application that extracts invoice information, validates financial calculations, and stores invoice records for review.

## Features

- PDF invoice text extraction
- AI-powered invoice data extraction using Google Gemini
- Review and edit extracted invoice details
- Financial validation and status reporting
- Duplicate invoice prevention
- SQLite database storage
- Invoice history with status filters and search
- CSV export
- Dashboard with invoice statistics

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- SQLite
- Pandas
- Pydantic

## Project Structure

```text
InvoiceFlow-AI/
├── app.py
├── database.py
├── invoices.db
├── requirements.txt
├── .env
└── src/
    ├── document_processor.py
    ├── gemini_client.py
    ├── invoice_extractor.py
    └── invoice_validator.py
```

## Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your Gemini API key using a local `.env` file, following the variable name expected by the application.
5. Start the application:

   ```bash
   streamlit run app.py
   ```

## Security

Do not commit API keys, passwords, or other secrets to GitHub.

## Project Status

The core invoice processing workflow is implemented. Testing, documentation, and deployment preparation are ongoing.
