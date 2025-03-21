"""Module for user api endpoints"""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse
from app.utils.promp_manager import create_rompt_model
from io import BytesIO
from app.utils.file_manager import FileManagerHelper
from app.utils.questionary_manager import QuestionaryManager
from typing import Optional

UPLOAD_DIR = "uploads"  # Folder to store generated files
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

router = APIRouter()


@router.get("/downloads/{filename}")
async def download_file(filename: str):
    try:
        file_path = FileManagerHelper.get_absolute_path(filename)

        if not FileManagerHelper.is_safe_file(file_path):
            raise HTTPException(
                status_code=403, detail="Forbidden: Access to this file is not allowed"
            )

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process_content")
async def process_content(
    text: Optional[str] = Body(default=None),
    file: Optional[UploadFile] = File(None),
    actions: Optional[list[str]] = Body(default=None),
):
    resumeFile = None
    qaContent = ""
    diagramFile = None

    finalContent = ""

    try:
        if not actions or "".join(actions) == "":
            raise HTTPException(
                status_code=400,
                detail="Failed to process content. No actions defined",
            )

        if file and text:
            raise HTTPException(
                status_code=400,
                detail="Failed to process content. Either both types of content were provided or neither.",
            )
        else:
            if file:
                content = await file.read()
                file_extension = file.filename.split(".")[-1].lower()
                finalContent = FileManagerHelper.get_file_type(
                    file_extension, BytesIO(content)
                )
            if text:
                finalContent = text

        if finalContent == "":
            raise HTTPException(
                status_code=400,
                detail="No content provided",
            )

        completion = create_rompt_model(
            systemRole="Eres un asistente para estudiantes. Ayudalos a realizar buenos resumenes, cuestionarios o diagramas basandote en el contenido que te comparten para facilitar su estudio de este. Se breve y puntual, trata de sintetizar lo mejor que puedas el contenido para que este sea claro y tenga información relevante",
            userInput=f"Tomando en cuenta solo esta lista de opciones: {', '.join(actions)}; Porfavor únicamente devuelveme la o las opciones (sin saltos de linea, ni nada extra, solo la opcion, si hay mas de una separala por coma) que puedes realizar para este contenido: {finalContent}. Tratando obviamente de que todas las opciones se puedan realizar, sin embargo si el contenido no cuenta con estructura para realizar alguna opción, puedes dejarla fuera, pero si es posible trabajar las opciones con el contenido brindado, entonces no dudes en poder tomar todas las opciones.",
        )

        actions_list = [
            action.strip()
            for action in completion.choices[0].message.content.split(",")
            if action.strip()
        ]

        if "resumen" in actions_list or "resume" in actions_list:
            resumeFile = FileManagerHelper.manage_file(finalContent)

        if "cuestionario" in actions_list or "questionary" in actions_list:
            qaContent = QuestionaryManager.generate_questionary(finalContent)

        response = {
            "message": "Success",
            "response": {
                "resume": resumeFile,
                "questionary": qaContent,
                "diagram": diagramFile,
            },
        }

        return response

    except HTTPException as e:
        # Handle HTTPException specifically and return the correct status code and detail
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        # Handle general exceptions with status code 500
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process content: {e}",
        )
