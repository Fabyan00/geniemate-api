"""Module helper for file management"""

import os
from fastapi import HTTPException
from io import BytesIO
import logging
from PyPDF2 import PdfReader  # For reading PDF files
from docx import Document
from reportlab.pdfgen import canvas
from app.locales.localization import tr
from app.utils.promp_manager import create_rompt_model  # For reading DOCX files
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from fastapi.responses import StreamingResponse

UPLOAD_DIR = "uploads"  # Folder to store generated files
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists


class FileManagerHelper:
    def get_file_type(fileExtension: str, fileContent: BytesIO):
        """Extract the content of a file"""
        if fileExtension == "pdf":
            text = FileManagerHelper.read_pdf(fileContent)
        elif fileExtension == "txt":
            text = fileContent.read().decode("utf-8")
        elif fileExtension == "docx":
            text = FileManagerHelper.read_docx(fileContent)
        else:
            raise HTTPException(status_code=400, detail="File type unsupported")

        return text

    def manage_file(content: str):
        """Creates a pdf file with the content given"""
        MAX_TOKENS = 4096
        if len(content) > MAX_TOKENS:
            content = content[:MAX_TOKENS]

        completion = create_rompt_model(tr("SYSTEM_PROMPT_RESUME"), content)
        summary_text = completion.choices[0].message.content

        title_completion = create_rompt_model(
            systemRole="Define a short title based on the summary topic, no more than 2 to 4 words",
            userInput=summary_text,
        )
        summary_title = title_completion.choices[0].message.content

        # Generate PDF
        pdf_path = f"uploads/{summary_title}_summary.pdf"

        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        # PDF Formatting Resume
        pdf.setTitle(f"{summary_title}")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(width / 2, height - 50, summary_title)

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 90, " ")
        margin_x = 50
        margin_y = height - 100

        # Split text into multiple lines that fit the page width
        max_width = width - 2 * margin_x
        line_height = 18  # Spacing between lines

        text_lines = simpleSplit(summary_text, "Helvetica", 12, max_width)

        # Write text line by line, handling page breaks
        for line in text_lines:
            if margin_y < 50:  # If near bottom, create a new page
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                margin_y = height - 50  # Reset Y position

            pdf.drawString(margin_x, margin_y, line)
            margin_y -= line_height  # Move cursor down
        pdf.save()

        pdf_buffer.seek(0)  # Reset buffer position

        # Save PDF to local storage
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.read())

        return {
            "filename": f"{summary_title}_summary.pdf",
            "preview": summary_text[:100] if len(summary_text) > 100 else summary_text,
            "download_url": f"/download/{summary_title}_summary.pdf",
        }

    def read_pdf(file: BytesIO):
        """Handling content of PDF files"""
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

    # Path Security
    def get_absolute_path(filename: str) -> str:
        """Get the absolute path of the file."""
        return os.path.abspath(FileManagerHelper.safe_file_path(filename))

    def is_safe_file(file_path: str) -> bool:
        """Check if the file is within the UPLOAD_DIR."""
        abs_upload_dir = os.path.abspath(UPLOAD_DIR)
        return os.path.commonpath([abs_upload_dir, file_path]) == abs_upload_dir

    def safe_file_path(filename: str) -> str:
        """Ensure the file path stays within the UPLOAD_DIR."""
        abs_upload_dir = os.path.abspath(UPLOAD_DIR)
        file_path = os.path.normpath(os.path.join(abs_upload_dir, filename))

        if not file_path.startswith(abs_upload_dir):
            raise ValueError("Invalid file path detected")

        return file_path
