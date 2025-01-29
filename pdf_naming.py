import pdfplumber
import io

def rename_pdf(pdf_file, date_suffix):
    """Renames a PDF based on the company name found in the document."""
    pdf_file.seek(0)  # Ensure reading from the start
    with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith("TO:"):
                        company_name = lines[i + 1].strip()
                        sanitized_name = "".join([c if c.isalnum() or c in " -_" else "_" for c in company_name])
                        return f"{sanitized_name}_{date_suffix}.pdf"
    return f"Unnamed_{date_suffix}.pdf"
