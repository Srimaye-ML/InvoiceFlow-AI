
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "invoices.db"


def get_connection():
    """Open a connection to the invoice database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the invoice table if it doesn't already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT,
                invoice_number TEXT,
                invoice_date TEXT,
                due_date TEXT,
                customer_name TEXT,
                currency TEXT DEFAULT 'INR',
                subtotal REAL,
                tax_amount REAL,
                total_amount REAL,
                amount_paid REAL,
                balance_due REAL,
                status TEXT NOT NULL,
                validation_issues TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )



def save_invoice(invoice, status, issues=None, invoice_id=None):
    """Save an invoice or update an existing matching invoice."""
    issues_text = "\n".join(issues or [])

    invoice_date = (
        invoice.invoice_date.isoformat()
        if invoice.invoice_date else None
    )
    due_date = (
        invoice.due_date.isoformat()
        if invoice.due_date else None
    )

    values = (
        invoice.supplier_name,
        invoice.invoice_number,
        invoice_date,
        due_date,
        invoice.customer_name,
        invoice.currency,
        float(invoice.subtotal) if invoice.subtotal is not None else None,
        float(invoice.tax_amount) if invoice.tax_amount is not None else None,
        float(invoice.total_amount) if invoice.total_amount is not None else None,
        float(invoice.amount_paid) if invoice.amount_paid is not None else None,
        float(invoice.balance_due) if invoice.balance_due is not None else None,
        status,
        issues_text,
    )

    with get_connection() as connection:
        existing = None

        if invoice_id is not None:
            existing = connection.execute(
                "SELECT id FROM invoices WHERE id = ?",
                (invoice_id,),
            ).fetchone()


        if existing is None and invoice.supplier_name and invoice.invoice_number:
            existing = connection.execute(
                """
                SELECT id FROM invoices
                WHERE LOWER(TRIM(supplier_name)) = LOWER(TRIM(?))
                  AND LOWER(TRIM(invoice_number)) = LOWER(TRIM(?))
                ORDER BY id DESC
                LIMIT 1
                """,
                (invoice.supplier_name, invoice.invoice_number),
            ).fetchone()

        if existing:
            connection.execute(
                """
                UPDATE invoices SET
                    supplier_name = ?,
                    invoice_number = ?,
                    invoice_date = ?,
                    due_date = ?,
                    customer_name = ?,
                    currency = ?,
                    subtotal = ?,
                    tax_amount = ?,
                    total_amount = ?,
                    amount_paid = ?,
                    balance_due = ?,
                    status = ?,
                    validation_issues = ?
                WHERE id = ?
                """,
                values + (existing["id"],),
            )
            return existing["id"]

        cursor = connection.execute(
            """
            INSERT INTO invoices (
                supplier_name, invoice_number, invoice_date, due_date,
                customer_name, currency, subtotal, tax_amount,
                total_amount, amount_paid, balance_due, status,
                validation_issues
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        return cursor.lastrowid



def get_all_invoices():
    """Return saved invoices, newest first."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM invoices ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]

def cleanup_test_duplicates():
    """Keep the newest complete record for each supplier and invoice number."""
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM invoices
            WHERE supplier_name IS NULL
               OR TRIM(supplier_name) = ''
               OR invoice_number IS NULL
               OR TRIM(invoice_number) = ''
            """
        )

        connection.execute(
            """
            DELETE FROM invoices
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM invoices
                WHERE supplier_name IS NOT NULL
                  AND TRIM(supplier_name) != ''
                  AND invoice_number IS NOT NULL
                  AND TRIM(invoice_number) != ''
                GROUP BY LOWER(TRIM(supplier_name)),
                         LOWER(TRIM(invoice_number))
            )
            """
        )

