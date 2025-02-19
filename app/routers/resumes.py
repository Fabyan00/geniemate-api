"""Module for user api endpoints"""

import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from openai import OpenAIError
from app.config import client
from app.models.promt_model import Promt
from app.utils.promp_validations import validate_input
from app.locales.localization import Localization, tr
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from app.utils.file_manager import FileManagerHelper

router = APIRouter()


@router.post("/resume")
async def get_resume(user_input: Promt):
    """Creates a resume based on user input"""
    try:
        Localization.set_language("en")
        validate_input(user_input.prompt)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": tr("SYSTEM_PROMPT_RESUME")},
                {"role": "user", "content": user_input.prompt},
            ],
        )
        return {"message": "Success", "response": completion.choices[0].message.content}
    except ValueError as ve:
        logging.getLogger().error("Invalid data error: %s", ve)
        raise HTTPException(status_code=422, detail=f"Invalid data error: {ve}") from ve
    except OpenAIError as oe:
        logging.getLogger().error("OpenAI API Error: %s", oe)
        raise HTTPException(status_code=502, detail=f"OpenAI API Error: {oe}") from oe
    except HTTPException as he:
        logging.getLogger().error("HTTP Error: %s", he)
        raise he
    except Exception as e:
        logging.exception(tr("ERROR_PROCESSING_REQUEST"))
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {e}"
        ) from e


@router.post("/file_resume")
async def get_file_resume(file: UploadFile = File(...)):
    """Processes a file (PDF, TXT, DOCX), summarizes it using ChatGPT, and returns a downloadable PDF."""

    if not file:
        return {"message": "Success", "response": "No file attached"}

    try:
        # Read the file content
        content = await file.read()
        file_extension = file.filename.split(".")[-1].lower()
        text_content = ""

        # Process based on file type
        if file_extension == "pdf":
            text_content = FileManagerHelper.read_pdf(BytesIO(content))
        elif file_extension == "txt":
            text_content = content.decode("utf-8")
        elif file_extension == "docx":
            text_content = FileManagerHelper.read_docx(BytesIO(content))
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Only PDF, TXT, and DOCX are allowed.",
            )

        MAX_TOKENS = 4096  # Adjust based on model token limits
        if len(text_content) > MAX_TOKENS:
            text_content = text_content[:MAX_TOKENS]

        # Call GPT for summary
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": tr("SYSTEM_PROMPT_RESUME")},
                {"role": "user", "content": text_content},
            ],
        )

        summary_text = completion.choices[0].message.content

        title_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Now define a short title based on the summary topic, no more than 2 to 4 words",
                },
                {"role": "user", "content": summary_text},
            ],
        )

        summary_title = title_completion.choices[0].message.content

        # Generate PDF with the summary
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter  # Standard letter page size (8.5 x 11 inches)

        # PDF Formatting Resume")
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

        # Return PDF
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{summary_title}_summary.pdf"'
            },
        )

    except ValueError as ve:
        logging.getLogger().error("Invalid data error: %s", ve)
        raise HTTPException(status_code=422, detail=f"Invalid data error: {ve}") from ve
    except Exception as e:
        logging.exception("Error processing request")
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
