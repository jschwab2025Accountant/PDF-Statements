import streamlit as st
import io
import zipfile
from pdf_processing import contains_999_transaction, convert_pdf_to_excel
from pdf_naming import rename_pdf

st.title("PDF Sorting & Excel Conversion Tool")

# Initialize session state for ZIP storage
if "renamed_pdfs_zip" not in st.session_state:
    st.session_state.renamed_pdfs_zip = None

if "excel_files_zip" not in st.session_state:
    st.session_state.excel_files_zip = None

# User input for date suffix
date_suffix = st.text_input("Enter Date for File Names (YYYY-MM-DD)", "")

# File Upload Section
uploaded_files = st.file_uploader(
    "Upload PDF files", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")

if st.button("Process PDFs"):
    if not date_suffix:
        st.error("Please enter a date to include in file names.")
    else:
        renamed_pdfs = []
        excel_files = []

        for uploaded_file in uploaded_files:
            pdf_stream = io.BytesIO(uploaded_file.read())

            # Rename file based on extracted company name & user-entered date
            new_name = rename_pdf(pdf_stream, date_suffix)

            # Check if the file contains a $9.99 transaction
            contains_999 = contains_999_transaction(pdf_stream)

            pdf_stream.seek(0)  # Reset stream position

            if contains_999:
                # Convert PDF to Excel
                excel_data = convert_pdf_to_excel(pdf_stream, new_name, date_suffix)
                excel_files.append((f"{new_name}.xlsx", excel_data))
            else:
                renamed_pdfs.append((new_name, pdf_stream))

        # Create ZIP for renamed PDFs without $9.99 transactions
        if renamed_pdfs:
            renamed_pdfs_zip = io.BytesIO()
            with zipfile.ZipFile(renamed_pdfs_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_name, file_data in renamed_pdfs:
                    file_data.seek(0)
                    zipf.writestr(file_name, file_data.read())
            renamed_pdfs_zip.seek(0)
            st.session_state.renamed_pdfs_zip = renamed_pdfs_zip

        # Create ZIP for Excel files converted from PDFs with $9.99 transactions
        if excel_files:
            excel_files_zip = io.BytesIO()
            with zipfile.ZipFile(excel_files_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_name, file_data in excel_files:
                    zipf.writestr(file_name, file_data.read())
            excel_files_zip.seek(0)
            st.session_state.excel_files_zip = excel_files_zip

        st.success("Processing complete! You can now download the files.")

# Display download buttons only if the ZIPs are available
if st.session_state.renamed_pdfs_zip:
    st.download_button(
        label="Download ZIP (Renamed PDFs without $9.99)",
        data=st.session_state.renamed_pdfs_zip,
        file_name="Renamed_PDFs.zip",
        mime="application/zip"
    )

if st.session_state.excel_files_zip:
    st.download_button(
        label="Download ZIP (Converted Excel Files)",
        data=st.session_state.excel_files_zip,
        file_name="Converted_Excel_Files.zip",
        mime="application/zip"
    )
