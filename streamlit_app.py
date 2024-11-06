import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

def extract_information(pdf_file):
    extracted_data = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            
            # Define patterns for insurance and patient information
            patterns = {
                'Patient Name': r'(?i)(?:patient\s+name|name)[:\s]+([A-Za-z\s\-]+)',
                'Date of Birth': r'(?i)(?:DOB|Date\s+of\s+Birth)[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})',
                'Address': r'(?i)address[:\s]+([A-Za-z0-9\s\.,]+)',
                'Primary Insurance': r'(?i)(?:primary|first)\s+insurance[:\s]+([A-Za-z0-9\s\.,]+)',
                'Secondary Insurance': r'(?i)(?:secondary|second)\s+insurance[:\s]+([A-Za-z0-9\s\.,]+)',
                'Insurance ID': r'(?i)(?:insurance|member|policy)\s+(?:id|number)[:\s]+([A-Za-z0-9\-]+)',
                'Group Number': r'(?i)group\s+(?:id|number)[:\s]+([A-Za-z0-9\-]+)',
                'Phone Number': r'(?i)(?:phone|tel)[:\s]+(\d{3}[-.]?\d{3}[-.]?\d{4})',
                'SSN': r'(?i)(?:ssn|social)[:\s]+(\d{3}[-]?\d{2}[-]?\d{4})'
            }
            
            # Extract data using patterns
            for data_type, pattern in patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = match.group(1).strip() if match.groups() else match.group(0).strip()
                        extracted_data.append({
                            'Page': page_num,
                            'Field': data_type,
                            'Value': value,
                            'Character Position': match.span()
                        })
                    except AttributeError:
                        continue
    
    return pd.DataFrame(extracted_data)

def main():
    st.title("Medical Document Review and Data Extraction Tool")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Medical Document (PDF)", type="pdf")
    
    if uploaded_file is not None:
        # Create two columns for layout
        col1, col2 = st.columns([0.6, 0.4])  # Adjust ratio to make PDF viewer larger
        
        with col1:
            st.subheader("Document Text")
            # Display PDF text content
            with pdfplumber.open(uploaded_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    st.markdown(f"**Page {page_num + 1}**")
                    text = page.extract_text()
                    st.text_area(f"Page {page_num + 1} Content", text, height=300)
        
        with col2:
            st.subheader("Extracted Information")
            # Extract and display information
            df = extract_information(uploaded_file)
            
            # Group by Field for better organization
            if not df.empty:
                for field in df['Field'].unique():
                    field_data = df[df['Field'] == field]
                    st.markdown(f"**{field}:**")
                    for _, row in field_data.iterrows():
                        st.write(f"Value: {row['Value']}")
                        st
