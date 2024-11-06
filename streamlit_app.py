import streamlit as st
import pdfplumber
import re
import tempfile
from PIL import Image
import pdf2image
import io

st.set_page_config(layout="wide")
st.title("PDF Review and Data Extraction")

def extract_information(pdf_file):
    extracted_info = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                
                # Pattern matching for various information
                patterns = {
                    'Patient Name': r'(?i)name:?\s*([A-Za-z\s]+)',
                    'DOB': r'(?i)(?:DOB|Date of Birth):?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                    'Address': r'(?i)address:?\s*([A-Za-z0-9\s\.,]+)',
                    'Primary Insurance': r'(?i)primary\s+insurance:?\s*([A-Za-z0-9\s]+)',
                    'Secondary Insurance': r'(?i)secondary\s+insurance:?\s*([A-Za-z0-9\s]+)'
                }

                for field, pattern in patterns.items():
                    matches = re.findall(pattern, text)
                    if matches:
                        extracted_info.append(f"{field}: {matches[0].strip()}")
                        extracted_info.append(f"Found on page {page_num}")
                        extracted_info.append("-" * 50)
                        
        return extracted_info
    
    except Exception as e:
        return [f"Error processing PDF: {str(e)}"]

def main():
    # Create two columns
    col1, col2 = st.columns([6, 4])
    
    with col1:
        st.subheader("PDF Viewer")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            # Display PDF
            try:
                # Convert PDF to images
                images = pdf2image.convert_from_bytes(uploaded_file.read())
                
                # Display first page (you can add pagination if needed)
                st.image(images[0], use_column_width=True)
                
            except Exception as e:
                st.error(f"Error displaying PDF: {str(e)}")
    
    with col2:
        st.subheader("Extracted Information")
        if uploaded_file is not None:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            
            # Extract and display information
            info = extract_information(uploaded_file)
            for line in info:
                st.write(line)

if __name__ == "__main__":
    main()
