import pdfplumber
import pandas as pd
import re
import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, Border, Side

def contains_999_transaction(pdf_file):
    """Checks if the PDF contains any $9.99 transactions."""
    pattern = r"\$9\.99"
    pdf_file.seek(0)  # Reset file pointer
    with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and re.search(pattern, text):
                return True
    return False

def extract_text_and_parse_to_df(pdf_file):
    """Extracts text from an in-memory PDF and converts it to a DataFrame."""
    transactions = []
    pdf_file.seek(0)
    with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for line in text.split('\n'):
                    match = re.match(r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(-?\$?\d{1,3}(?:,\d{3})*\.\d{2})', line)
                    if match:
                        date, transaction, amount = match.groups()
                        transactions.append([date, transaction, float(amount.replace("$", "").replace(",", ""))])

    df = pd.DataFrame(transactions, columns=['Date', 'Transaction', 'Amount'])

    # Remove transactions with a value of $9.99
    df = df[df["Amount"] != 9.99]

    return df

def convert_pdf_to_excel(pdf_file, file_name, date_suffix):
    """Converts transactions from a PDF into an Excel file while formatting headers, date, and totals."""
    df = extract_text_and_parse_to_df(pdf_file)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, startrow=2, sheet_name="Transactions")

        workbook = writer.book
        worksheet = writer.sheets["Transactions"]

        worksheet["A1"] = "Elemental Scientific Inc"
        worksheet["B1"] = date_suffix

        worksheet[f"B{len(df)+4}"] = "Total"
        worksheet[f"C{len(df)+4}"] = df["Amount"].sum()

    output.seek(0)
    return output
