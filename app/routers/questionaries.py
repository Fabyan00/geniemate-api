"""Module for user api endpoints"""

import logging
from fastapi import APIRouter, HTTPException
from openai import OpenAIError
from app.models.promt_model import Promt
from app.utils.promp_manager import validate_input, create_rompt_model
from app.locales.localization import Localization, tr

router = APIRouter()


@router.post("/questions_and_answers")
async def generate_questionary(user_input: Promt):
    """Creates Q&A based on user input"""
    try:
        Localization.set_language("en")
        validate_input(user_input.prompt)
        completion = create_rompt_model(tr("SYSTEM_PROMPT_Q&A"), user_input.prompt)
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
