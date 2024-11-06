import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, 
                            QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pdfplumber
import tempfile

class PDFReviewApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Review and Data Extraction')
        self.setGeometry(100, 100, 1400, 800)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Left panel for PDF viewer
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Upload button
        upload_btn = QPushButton('Upload PDF')
        upload_btn.clicked.connect(self.upload_pdf)
        left_layout.addWidget(upload_btn)

        # PDF viewer
        self.pdf_viewer = QWebEngineView()
        self.pdf_viewer.setMinimumWidth(700)
        left_layout.addWidget(self.pdf_viewer)

        # Right panel for extracted information
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Extracted info display
        right_layout.addWidget(QLabel('Extracted Information:'))
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        right_layout.addWidget(self.info_display)

        # Add panels to main layout
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

        self.show()

    def upload_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", "", "PDF Files (*.pdf)")
        
        if file_name:
            # Display PDF
            self.pdf_viewer.setUrl(f'file:///{file_name}')
            
            # Extract information
            self.extract_information(file_name)

    def extract_information(self, pdf_path):
        extracted_info = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
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

        except Exception as e:
            extracted_info.append(f"Error processing PDF: {str(e)}")

        # Update the info
