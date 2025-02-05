"""Module for user api endpoints"""

import logging
from fastapi import APIRouter
from fastapi import HTTPException
from openai import OpenAIError
from app.config import client
from app.models.promt_model import Promt
from app.utils.promp_validations import validate_input
from app.locales.localization import Localization, tr

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
        raise HTTPException(status_code=422, detail=f"Invalid data error: {ve}")
    except OpenAIError as oe:
        logging.getLogger().error("OpenAI API Error: %s", oe)
        raise HTTPException(status_code=502, detail=f"OpenAI API Error: {oe}")
    except HTTPException as he:
        logging.getLogger().error("HTTP Error: %s", he)
        raise he
    except Exception as e:
        logging.exception(tr("ERROR_PROCESSING_REQUEST"))
        raise HTTPException(status_code=500, detail=e)
