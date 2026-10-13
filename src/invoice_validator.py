
from decimal import Decimal

from src.invoice_extractor import InvoiceData


def validate_invoice(invoice: InvoiceData) -> list[str]:
    """Check required invoice fields and financial calculations."""

    issues = []

    # Check for missing important invoice details.
    required_fields = {
        "Supplier name": invoice.supplier_name,
        "Invoice number": invoice.invoice_number,
        "Invoice date": invoice.invoice_date,
        "Customer name": invoice.customer_name,
        "Invoice total": invoice.total_amount,
    }

    for field_name, value in required_fields.items():
        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            issues.append(f"Missing required field: {field_name}.")

    # Check whether subtotal + tax equals total.
    if (
        invoice.subtotal is not None
        and invoice.tax_amount is not None
        and invoice.total_amount is not None
    ):
        expected_total = invoice.subtotal + invoice.tax_amount

        if abs(expected_total - invoice.total_amount) > Decimal("0.01"):
            issues.append(
                f"Total mismatch: subtotal + tax is "
                f"{expected_total}, but invoice total is "
                f"{invoice.total_amount}."
            )

    # Check whether total - paid amount equals balance due.
    if (
        invoice.total_amount is not None
        and invoice.amount_paid is not None
        and invoice.balance_due is not None
    ):
        expected_balance = invoice.total_amount - invoice.amount_paid

        if abs(expected_balance - invoice.balance_due) > Decimal("0.01"):
            issues.append(
                f"Balance mismatch: expected {expected_balance}, "
                f"but invoice balance is {invoice.balance_due}."
            )

    return issues
