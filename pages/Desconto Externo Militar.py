import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import tempfile
import time

# Function to extract tables from a PDF using PyMuPDF
def extract_tables_from_pdf(pdf_file):
    tables = []

    # Open the PDF file
    pdf_document = fitz.open(pdf_file)
    total_pages = pdf_document.page_count

    for page_num in range(total_pages):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text("blocks")

        # Convert extracted blocks to DataFrame format
        for block in page_text:
            tables.append(block)

    pdf_document.close()
    return pd.DataFrame(tables, columns=["x0", "y0", "x1", "y1", "text", "block_no", "block_type", "block_flags"])

# Function to display progress bar during table extraction
def extract_with_progress_bar(pdf_file):
    pdf_document = fitz.open(pdf_file)
    total_pages = pdf_document.page_count

    progress_bar = st.progress(0)
    tables = []

    for page_num in range(total_pages):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text("blocks")

        for block in page_text:
            tables.append(block)

        progress_bar.progress((page_num + 1) / total_pages)
        time.sleep(0.1)  # Simulate processing time

    pdf_document.close()
    return pd.DataFrame(tables, columns=["x0", "y0", "x1", "y1", "text", "block_no", "block_type", "block_flags"])

# Function to download the processed DataFrame as CSV
def download_csv(df):
    csv_data = df.to_csv(index=False)
    return csv_data

# Streamlit app interface
st.title("PDF Table Extraction Tool")
st.markdown("Upload a PDF file to extract tabular data.")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    try:
        # Temporary file for PyMuPDF compatibility
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.read())
            temp_pdf_path = temp_pdf.name

        # Table extraction with progress bar
        st.subheader("Extracting tables...")
        extracted_tables = extract_with_progress_bar(temp_pdf_path)

        # Display extracted data
        st.subheader("Extracted Data")
        st.dataframe(extracted_tables)

        # Option to download CSV
        st.subheader("Download Extracted Data")
        csv_data = download_csv(extracted_tables)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="extracted_data.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")