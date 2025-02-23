"""Module helper for file management"""

from fastapi import HTTPException
from io import BytesIO
import logging
from PyPDF2 import PdfReader  # For reading PDF files
from docx import Document  # For reading DOCX files


class FileManagerHelper:
    def manage_file(file_extension: str, content: BytesIO):
        """Handling file type"""

        if file_extension == "pdf":
            return FileManagerHelper.read_pdf(content)
        elif file_extension == "txt":
            return content.decode("utf-8")
        elif file_extension == "docx":
            return FileManagerHelper.read_docx(content)
        else:
            raise HTTPException(
                status_code=400,
                detail="File type unssuported, only PDF, TXT, and DOCX are allowed.",
            )

    def read_pdf(file: BytesIO):
        """Hndling content of PDF files"""
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            logging.error(f"Error reading PDF file: {e}")
            raise HTTPException(status_code=400, detail="Unable to process PDF file")

    def read_docx(file: BytesIO):
        """Handling content of DOCX files"""
        try:
            doc = Document(file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            logging.error(f"Error reading DOCX file: {e}")
            raise HTTPException(status_code=400, detail="Unable to process DOCX file")
