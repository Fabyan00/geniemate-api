"""Utils module for validating user inputs"""

from fastapi import HTTPException
from app.locales.localization import Localization, tr
from app.config import client


def validate_input(text: str):
    """Checks user input"""

    Localization.set_language("en")
    if not text or text.strip() == "":
        raise HTTPException(status_code=400, detail=tr("ERROR_INVALID_PROMPT"))


def create_rompt_model(systemRole: str, userInput: str, model: str = "gpt-4o-mini"):
    """Creates the request to chat gpt model"""
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": systemRole},
            {"role": "user", "content": userInput},
        ],
    )
