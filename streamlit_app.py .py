import streamlit as st
import pdfplumber
import pandas as pd
from PIL import Image
import re
import io

def extract_information(pdf_file):
    extracted_data = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            
            # Define patterns for common data types
            patterns = {
                'Dates': r'\d{2}[/-]\d{2}[/-]\d{4}',
                'Emails': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'Phone Numbers': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'Dollar Amounts': r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
            }
            
            # Extract data using patterns
            for data_type, pattern in patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    extracted_data.append({
                        'Page': page_num,
                        'Type': data_type,
                        'Value': match.group(),
                        'Position': match.span()
                    })
    
    return pd.DataFrame(extracted_data)

def main():
    st.title("PDF Review and Data Extraction Tool")
    
    # File upload
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file is not None:
        # Create two columns for layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("PDF Viewer")
            # Display PDF pages as images
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    img = page.to_image()
                    st.image(img.original, use_column_width=True)
        
        with col2:
            st.subheader("Extracted Information")
            # Extract and display information
            df = extract_information(uploaded_file)
            st.dataframe(df)
            
            # Download extracted data
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Extracted Data",
                csv,
                "extracted_data.csv",
                "text/csv",
                key='download-csv'
            )

if __name__ == "__main__":
    main()