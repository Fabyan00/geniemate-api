import logging
from fastapi import HTTPException
from openai import OpenAIError
from app.locales.localization import Localization, tr
from app.utils.promp_manager import create_rompt_model, validate_input


class QuestionaryManager:
    def generate_questionary(content: str):
        """Creates Q&A based on user input"""
        try:
            Localization.set_language("en")
            validate_input(content)
            completion = create_rompt_model(tr("SYSTEM_PROMPT_Q&A"), content)
            return completion.choices[0].message.content
        except ValueError as ve:
            logging.getLogger().error("Invalid data error: %s", ve)
            raise HTTPException(
                status_code=422, detail=f"Invalid data error: {ve}"
            ) from ve
        except OpenAIError as oe:
            logging.getLogger().error("OpenAI API Error: %s", oe)
            raise HTTPException(
                status_code=502, detail=f"OpenAI API Error: {oe}"
            ) from oe
        except HTTPException as he:
            logging.getLogger().error("HTTP Error: %s", he)
            raise he
        except Exception as e:
            logging.exception(tr("ERROR_PROCESSING_REQUEST"))
            raise HTTPException(
                status_code=500, detail=f"Error processing request: {e}"
            ) from e
