from fastapi import HTTPException
from app.locales.localization import Localization, tr


def validate_input(text: str):
    Localization.set_language("en")
    if not text or text.strip() == "":
        raise HTTPException(status_code=400, detail=tr("ERROR_INVALID_PROMPT"))
