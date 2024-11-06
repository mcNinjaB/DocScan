import streamlit as st
import pdfplumber
import pandas as pd
import re

def extract_information_by_page(pdf_file):
    page_data = {}
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            
            # Define patterns for common data types and insurance-related terms
            patterns = {
                'Dates': r'\d{2}[/-]\d{2}[/-]\d{4}',
                'Emails': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'Phone Numbers': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'Dollar Amounts': r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
                
                # Insurance-specific patterns
                'Policy Numbers': r'\b(?:Policy|Policy Number|ID)\s*[:#]?\s*\d{5,}\b',
                'Insurance Terms': r'\b(?:Insurance|Policy|Coverage|Claim|Premium|Deductible|Insured|Insurer)\b',
                'Insured Names': r'\b(?:Insured Name|Policy Holder|Covered Individual)\s*[:#]?\s*\w+\s*\w*\b',
                
                # Capture text following "Primary Insurance," "Secondary Insurance," etc.
                'Primary Insurance Info': r'\b(?:Primary Insurance|Secondary Insurance|Tertiary Insurance)\s*[:#]?\s*([A-Za-z0-9.,\- ]+)',
            }
            
            # Extract data for each page
            extracted_data = []
            for data_type, pattern in patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    extracted_data.append({
                        'Page': page_num,
                        'Type': data_type,
                        'Value': match.group(1) if data_type == 'Primary Insurance Info' else match.group(),
                        'Extracted Text': match.group(),
                        'Position': match.span()
                    })
            
            # Save DataFrame for each page
            page_data[page_num] = pd.DataFrame(extracted_data)
    
    return page_data

def main():
    st.title("PDF Insurance Review and Data Extraction Tool")
    
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
            st.subheader("Extracted Information by Page")
            # Extract and display information page by page
            page_data = extract_information_by_page(uploaded_file)
            
            for page_num, df in page_data.items():
                st.markdown(f"### Page {page_num}")
                if not df.empty:
                    st.write(df)  # Display the DataFrame for each page
                else:
                    st.write("No data extracted on this page.")
                
            # Download all extracted data as a single CSV
            all_data = pd.concat(page_data.values(), ignore_index=True)
            csv = all_data.to_csv(index=False)
            st.download_button(
                "Download All Extracted Data",
                csv,
                "extracted_data.csv",
                "text/csv",
                key='download-csv'
            )

if __name__ == "__main__":
    main()
