
import streamlit as st
import io
import pandas as pd
from src.document_processor import extract_text_from_pdf
from src.invoice_extractor import (
    InvoiceData,
    extract_invoice_with_gemini,
)
from src.invoice_validator import validate_invoice
from database import (
    initialize_database,
    save_invoice,
    get_all_invoices,
)

st.set_page_config(
    page_title="InvoiceFlow AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b1020;
    --panel: #121a2d;
    --border: #26334d;
    --muted: #9aa8c3;
    --blue: #62a8ff;
    --purple: #a78bfa;
}

.stApp {
    background:
        radial-gradient(ellipse at 5% 0%, #172449 0%, transparent 38%),
        var(--bg);
    color: #edf3ff;
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3, p, label, span, div {
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0e1628;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
}

.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #72b7ff, #b6a0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.eyebrow {
    color: #88baff;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero {
    padding: 1.8rem 2rem;
    border: 1px solid #304467;
    border-radius: 20px;
    background: linear-gradient(115deg, #172b4d, #1a2040 58%, #29204a);
    margin-bottom: 1.5rem;
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.25rem;
    line-height: 1.2;
    margin: 0.6rem 0;
    color: #f4f7ff;
}

.hero p {
    color: #c3cfe6;
    margin-bottom: 0;
}

.metric-card {
    background: linear-gradient(145deg, #172239, #111a2c);
    border: 1px solid #2a3a57;
    border-radius: 16px;
    padding: 1.2rem;
    min-height: 135px;
}

.metric-label {
    color: #a5b4ce;
    font-size: 0.85rem;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    margin: 0.55rem 0 0.25rem;
    color: #f5f8ff;
}

.metric-note {
    font-size: 0.78rem;
    color: #83d9bb;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 1.6rem 0 0.8rem;
}


/* Fix extracted text visibility */
div[data-testid="stTextArea"] label {
    color: #cbd5e1 !important;
}

div[data-testid="stTextArea"] textarea {
    background-color: #111827 !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    border: 1px solid #475569 !important;
    border-radius: 10px !important;
    caret-color: #60a5fa !important;
}

div[data-testid="stTextArea"] textarea::placeholder {
    color: #94a3b8 !important;
}


.stButton > button {
    border-radius: 10px;
    border: 1px solid #456ca7;
    background: linear-gradient(100deg, #2563eb, #7357d9);
    color: white;
    font-weight: 600;
    min-height: 2.7rem;
}

.stButton > button:hover {
    border-color: #a5caff;
    color: white;
    filter: brightness(1.12);
}

div[data-testid="stDataFrame"] {
    border: 1px solid #2a3a57;
    border-radius: 12px;
    overflow: hidden;
}

hr {
    border-color: #26334d;
}

.small-muted {
    color: #9aa8c3;
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)

# ---------- SAMPLE DATA ----------
invoices = pd.DataFrame([
    {
        "Invoice ID": "INV-2026-001",
        "Supplier": "Nova Technologies",
        "Date": "2026-10-10",
        "Amount": 24500.00,
        "Status": "Verified",
    },
    {
        "Invoice ID": "INV-2026-002",
        "Supplier": "Vertex Supplies",
        "Date": "2026-10-11",
        "Amount": 18750.00,
        "Status": "Review Required",
    },
    {
        "Invoice ID": "INV-2026-003",
        "Supplier": "BluePeak Systems",
        "Date": "2026-10-12",
        "Amount": 32100.00,
        "Status": "Processing",
    },
])

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown('<div class="brand">⚡ InvoiceFlow AI</div>',
                unsafe_allow_html=True)
    st.caption("INTELLIGENT DOCUMENT OPERATIONS")
    st.divider()

    page = st.radio(
        "WORKSPACE",
        ["Overview", "Process Invoice", "Invoice History", "AI Insights"],
        label_visibility="visible",
    )

    st.divider()
    st.markdown("**SYSTEM STATUS**")
    st.markdown("🟢 Application online")
    st.markdown("🔵 Demo environment")
    st.caption("AI extraction will be connected in a later section.")

# ---------- HEADER ----------
st.markdown(
    '<div class="eyebrow">YOUR INTELLIGENT FINANCE WORKSPACE</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="hero">
    <div class="eyebrow">✦ DOCUMENT INTELLIGENCE PLATFORM</div>
    <h1>Invoices, understood.</h1>
    <p>Extract information, validate financial details, and keep your
    invoice workflow under control — all in one workspace.</p>
</div>
""", unsafe_allow_html=True)

# ---------- PAGE CONTENT ----------

if page == "Overview":
    st.markdown("### Workspace overview")
    st.caption("Live statistics from your saved invoices.")

    saved_invoices = get_all_invoices()

    total_invoices = len(saved_invoices)
    verified_invoices = sum(
        1 for invoice in saved_invoices
        if invoice.get("status") == "Verified"
    )
    review_invoices = sum(
        1 for invoice in saved_invoices
        if invoice.get("status") == "Review Required"
    )
    total_value = sum(
        float(invoice.get("total_amount") or 0)
        for invoice in saved_invoices
    )

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        (col1, "TOTAL INVOICES", str(total_invoices), "Saved invoice records"),
        (col2, "VERIFIED", str(verified_invoices), "Passed validation"),
        (col3, "NEEDS REVIEW", str(review_invoices), "Requires attention"),
        (col4, "TOTAL VALUE", f"₹{total_value:,.2f}", "Combined invoice value"),
    ]

    for col, label, value, note in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Recent invoices</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        invoices,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(
                "Amount (INR)", format="₹%.2f"
            ),
        },
    )

    st.markdown(
        '<div class="section-title">Quick actions</div>',
        unsafe_allow_html=True,
    )

    action1, action2 = st.columns(2)

    with action1:
        st.info("**Process a new invoice**\n\nUpload a PDF or image to begin.")
        if st.button(
            "Open invoice processor",
            use_container_width=True,
            key="overview_open_processor",
        ):
            st.session_state["requested_page"] = "Process Invoice"
            st.rerun()

    with action2:
        st.info("**Review invoice history**\n\nExplore your saved invoice records.")
        if st.button(
            "View invoice history",
            use_container_width=True,
            key="overview_view_history",
        ):
            st.session_state["requested_page"] = "Invoice History"
            st.rerun()


elif page == "Process Invoice":
    st.markdown("### Process an invoice")
    st.caption(
        "Upload a PDF invoice to extract its text for AI processing."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF invoice",
        type=["pdf"],
        help="For now, text-based PDFs are supported.",
        key="invoice_pdf",
    )

    if uploaded_file is not None:
        st.success(f"File selected: {uploaded_file.name}")

        if st.button("Extract invoice text", use_container_width=True):
            try:
                with st.spinner("Reading invoice document..."):
                    pdf_bytes = uploaded_file.getvalue()
                    extracted_text = extract_text_from_pdf(pdf_bytes)

                if extracted_text:
                    st.session_state["extracted_invoice_text"] = extracted_text
                    st.success("Text extraction completed!")
                else:
                    st.warning(
                        "No selectable text was found. "
                        "This may be a scanned PDF; OCR will be added later."
                    )

            except Exception as error:
                st.error(f"Could not read this PDF: {error}")

    if st.session_state.get("extracted_invoice_text"):

        st.markdown("#### Extracted document text")
        st.text_area(
            "Review extracted text",
            value=st.session_state["extracted_invoice_text"],
            height=300,
        )

        st.markdown("#### AI Invoice Extraction")

        if st.button("✨ Extract Invoice Details with AI", use_container_width=True):
            try:
                with st.spinner("Gemini is analyzing your invoice..."):
                    ai_invoice = extract_invoice_with_gemini(
                        st.session_state["extracted_invoice_text"]
                    )
                    st.session_state["ai_invoice_data"] = ai_invoice

                st.success("AI extraction completed!")

            except Exception as error:
                st.error(f"AI extraction failed: {error}")

        ai_invoice = st.session_state.get("ai_invoice_data")

        if ai_invoice is not None:
            st.markdown("**Extracted invoice details**")
            st.write("Supplier:", ai_invoice.supplier_name or "Not found")
            st.write("Invoice number:", ai_invoice.invoice_number or "Not found")
            st.write("Invoice date:", ai_invoice.invoice_date or "Not found")
            st.write("Customer:", ai_invoice.customer_name or "Not found")
            st.write("Subtotal:", ai_invoice.subtotal if ai_invoice.subtotal is not None else "Not found")
            st.write("Tax amount:", ai_invoice.tax_amount if ai_invoice.tax_amount is not None else "Not found")
            st.write("Invoice total:", ai_invoice.total_amount if ai_invoice.total_amount is not None else "Not found")
            st.write("Amount paid:", ai_invoice.amount_paid if ai_invoice.amount_paid is not None else "Not found")
            st.write("Balance due:", ai_invoice.balance_due if ai_invoice.balance_due is not None else "Not found")
        
        ai_invoice = st.session_state.get("ai_invoice_data")

        if ai_invoice is not None:
            st.markdown("#### Review & Edit Invoice Details")

            with st.form("invoice_details_form"):
                edited_supplier = st.text_input(
                    "Supplier name",
                    value=ai_invoice.supplier_name or "",
                )
                edited_invoice_number = st.text_input(
                    "Invoice number",
                    value=ai_invoice.invoice_number or "",
                )
                edited_invoice_date = st.date_input(
                    "Invoice date",
                    value=ai_invoice.invoice_date,
                )
                edited_due_date = st.date_input(
                    "Due date",
                    value=ai_invoice.due_date,
                )
                edited_customer = st.text_input(
                    "Customer name",
                    value=ai_invoice.customer_name or "",
                )

                details_saved = st.form_submit_button(
                    "Save Edited Details",
                    width="stretch",
                )

            if details_saved:
                
                
                st.session_state["ai_invoice_data"] = ai_invoice.model_copy(
                    update={
                        "supplier_name": edited_supplier or None,
                        "invoice_number": edited_invoice_number or None,
                        "invoice_date": edited_invoice_date,
                        "due_date": edited_due_date,
                        "customer_name": edited_customer or None,
                    }
                )
                st.success("Edited invoice details updated!")


        st.markdown("#### Invoice Validation")

        st.caption(
            "Enter the amounts from the invoice to check their calculations."
        )

        with st.form("invoice_validation_form"):
            subtotal = st.number_input(
                "Subtotal (₹)",
                min_value=0.0,
                value=float(
                    st.session_state["ai_invoice_data"].subtotal
                    if st.session_state.get("ai_invoice_data")
                    and st.session_state["ai_invoice_data"].subtotal is not None
                    else 9400.0
                ),
                step=100.0,
            )

            tax_amount = st.number_input(
                "Tax amount (₹)",
                min_value=0.0,
                value=float(st.session_state["ai_invoice_data"].tax_amount) if st.session_state.get("ai_invoice_data") and st.session_state["ai_invoice_data"].tax_amount is not None else 1692.0,
                step=100.0,
            )

            total_amount = st.number_input(
                "Invoice total (₹)",
                min_value=0.0,
                value=float(st.session_state["ai_invoice_data"].total_amount) if st.session_state.get("ai_invoice_data") and st.session_state["ai_invoice_data"].total_amount is not None else 11092.0,
                step=100.0,
            )

            amount_paid = st.number_input(
                "Amount paid (₹)",
                min_value=0.0,
                value=float(st.session_state["ai_invoice_data"].amount_paid) if st.session_state.get("ai_invoice_data") and st.session_state["ai_invoice_data"].amount_paid is not None else 0.0,
                step=100.0,
            )

            balance_due = st.number_input(
                "Balance due (₹)",
                min_value=0.0,
                value=float(st.session_state["ai_invoice_data"].balance_due) if st.session_state.get("ai_invoice_data") and st.session_state["ai_invoice_data"].balance_due is not None else 11092.0,
                step=100.0,
            )

            validate_clicked = st.form_submit_button(
                "Validate Invoice",
                width="stretch",
            )

        
       
        if validate_clicked:
            ai_invoice = st.session_state.get("ai_invoice_data")

            if ai_invoice is None:
                st.error(
                    "Please extract invoice details with AI before validating."
                )
                st.stop()

            if (
                not ai_invoice.supplier_name
                or not ai_invoice.invoice_number
                or not ai_invoice.invoice_date
                or not ai_invoice.customer_name
            ):
                st.error(
                    "Please ensure supplier name, invoice number, "
                    "invoice date, and customer name are available "
                    "before validating."
                )
                st.stop()

            try:
                invoice = InvoiceData(
                    supplier_name=ai_invoice.supplier_name,
                    invoice_number=ai_invoice.invoice_number,
                    invoice_date=ai_invoice.invoice_date,
                    due_date=ai_invoice.due_date,
                    currency=ai_invoice.currency or "INR",
                    customer_name=ai_invoice.customer_name,
                    subtotal=str(subtotal),
                    tax_amount=str(tax_amount),
                    total_amount=str(total_amount),
                    amount_paid=str(amount_paid),
                    balance_due=str(balance_due),
                )

                issues = validate_invoice(invoice)
                status = "Review Required" if issues else "Verified"

                saved_id = save_invoice(invoice, status, issues)
                st.session_state["last_saved_invoice_id"] = saved_id
                st.success(
                    f"Invoice saved successfully! Record ID: {saved_id}"
                )

                if issues:
                    st.error("Status: Review Required")
                    for issue in issues:
                        st.warning(issue)
                else:
                    st.success("Status: Verified")
                    st.success(
                        "Invoice calculations passed validation!"
                    )

            except Exception as error:
                st.error(f"Validation or save error: {error}")

elif page == "Invoice History":
        st.markdown("### Invoice history")
        st.caption("Invoices saved after processing and validation.")

saved_invoices = get_all_invoices()

status_filter = st.selectbox(
        "Filter by Status",
        ["All Invoices", "Verified", "Review Required"]
    )

if status_filter != "All Invoices":
        saved_invoices = [
            invoice for invoice in saved_invoices
            if invoice.get("status") == status_filter
        ]

    
if not saved_invoices:
        if status_filter == "Review Required":
            st.info("No invoices require review. All caught up!")
        elif status_filter == "Verified":
            st.info("No verified invoices found.")
        else:
            st.info("No saved invoices yet. Process and validate an invoice to see it here.")

else:
        history_df = pd.DataFrame(saved_invoices)

        search_query = st.text_input(
            "Search invoices",
            placeholder="Enter supplier name or invoice number..."
        )

        if search_query:
            search_query = search_query.strip().lower()

            history_df = history_df[
                history_df["supplier_name"].astype(str).str.lower().str.contains(
                    search_query, na=False
                )
                | history_df["invoice_number"].astype(str).str.lower().str.contains(
                    search_query, na=False
                )
            ]


        history_df = history_df.rename(
            columns={
                "id": "Record ID",
                "supplier_name": "Supplier",
                "invoice_number": "Invoice Number",
                "invoice_date": "Invoice Date",
                "due_date": "Due Date",
                "customer_name": "Customer",
                "currency": "Currency",
                "subtotal": "Subtotal",
                "tax_amount": "Tax",
                "total_amount": "Total Amount",
                "amount_paid": "Amount Paid",
                "balance_due": "Balance Due",
                "status": "Status",
                "validation_issues": "Validation Issues",
                "created_at": "Saved At",
            }
        )

        filtered_df = history_df
        st.caption(f"Matching invoices: {len(filtered_df)}")
        if filtered_df.empty:
           st.info("No invoices match your search and selected filters.")
        st.metric("Matching invoices", len(filtered_df))

        csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Download Invoice History (CSV)",
            data=csv_data,
            file_name="invoice_history.csv",
            mime="text/csv",
        )

        
        display_columns = [
            "Record ID",
            "Supplier",
            "Invoice Number",
            "Invoice Date",
            "Customer",
            "Total Amount",
            "Status",
        ]

        visible_df = filtered_df[
            [column for column in display_columns if column in filtered_df.columns]
        ].copy()

        if "Total Amount" in visible_df.columns:
            visible_df["Total Amount"] = visible_df["Total Amount"].apply(
                lambda amount: f"₹{amount:,.2f}" if pd.notna(amount) else "—"
            )

        
        if not filtered_df.empty:
            st.dataframe(
                visible_df,
                use_container_width=True,
                hide_index=True
            )
        

        if not filtered_df.empty:
            st.markdown("### Invoice Details")
            st.caption("Select a saved invoice to view its complete information.")


        if saved_invoices:
            invoice_options = {
                f"#{row['id']} — {row.get('supplier_name') or 'Unknown supplier'} — "
                f"{row.get('invoice_number') or 'No invoice number'}": row
                for row in saved_invoices
            }

            selected_label = st.selectbox(
                "Choose an invoice",
                options=list(invoice_options.keys()),
                key="invoice_details_select",
            )

            selected_invoice = invoice_options[selected_label]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Supplier & Customer")
                st.write("**Supplier:**", selected_invoice.get("supplier_name") or "Not available")
                st.write("**Invoice number:**", selected_invoice.get("invoice_number") or "Not available")
                st.write("**Customer:**", selected_invoice.get("customer_name") or "Not available")
                st.write("**Invoice date:**", selected_invoice.get("invoice_date") or "Not available")
                st.write("**Due date:**", selected_invoice.get("due_date") or "Not available")

            with col2:
                st.markdown("#### Financial Summary")
                currency = selected_invoice.get("currency") or "INR"
                symbol = "₹" if currency == "INR" else f"{currency} "

                for label, field in [
                    ("Subtotal", "subtotal"),
                    ("Tax amount", "tax_amount"),
                    ("Total amount", "total_amount"),
                    ("Amount paid", "amount_paid"),
                    ("Balance due", "balance_due"),
                ]:
                    amount = selected_invoice.get(field)
                    formatted_amount = (
                        f"{symbol}{amount:,.2f}"
                        if amount is not None
                        else "Not available"
                    )
                    st.write(f"**{label}:**", formatted_amount)

            st.markdown("#### Validation Result")

            if selected_invoice.get("status") == "Verified":
                st.success("Status: Verified")
            else:
                st.warning("Status: Review Required")

            validation_issues = selected_invoice.get("validation_issues") or ""
            if validation_issues.strip():
                for issue in validation_issues.splitlines():
                    st.warning(issue)
            elif selected_invoice.get("status") == "Verified":
                st.info("No validation issues were recorded for this invoice.")




            elif page == "AI Insights":
                st.markdown("### AI insights")
                st.caption("Analytics will use real processed invoices in a later phase.")
                st.info(
                    "The AI insights panel is a placeholder. No predictions or "
                    "financial analysis have been run yet."
                )

st.divider()
st.markdown(
    '<p class="small-muted">InvoiceFlow AI · Development prototype · '
    'Demo data only</p>',
    unsafe_allow_html=True,
)
