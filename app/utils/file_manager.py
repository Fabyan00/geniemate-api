"""Module for file management"""

from fastapi import HTTPException
from io import BytesIO
import logging
from PyPDF2 import PdfReader  # For reading PDF files
from docx import Document  # For reading DOCX files


class FileManagerHelper:
    """Helper function to read the content of PDF files"""

    def read_pdf(file: BytesIO):
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            logging.error(f"Error reading PDF file: {e}")
            raise HTTPException(status_code=400, detail="Unable to process PDF file")

    """ Helper function to read the content of DOCX files """

    def read_docx(file: BytesIO):
        try:
            doc = Document(file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logging.error(f"Error reading DOCX file: {e}")
            raise HTTPException(status_code=400, detail="Unable to process DOCX file")
