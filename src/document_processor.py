
import pymupdf


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from a text-based PDF invoice.

    Args:
        pdf_bytes: PDF file contents as bytes.

    Returns:
        Extracted text from all pages.
    """
    extracted_pages = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text").strip()

            if page_text:
                extracted_pages.append(
                    f"--- Page {page_number} ---\n{page_text}"
                )

    return "\n\n".join(extracted_pages)
