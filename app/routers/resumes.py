import logging
from fastapi import APIRouter
from fastapi import HTTPException
from openai import OpenAIError
from app.config import client
from app.models.promt_model import Promt
from app.utils.promp_validations import validate_input
from app.locales.localization import Localization, tr

router = APIRouter()

@router.post('/resume')
async def get_resume(input: Promt):
  try:
    Localization.set_language('en')
    validate_input(input.prompt)
      
    completion = client.chat.completions.create(
      model = "gpt-4o-mini",
      messages=[
        {
          "role": "system", 
          "content": tr("SYSTEM_PROMPT_RESUME")
        },
        {
          "role": "user", 
          "content": input.prompt
        },
      ]
    )
    return {
      "message": "Success", 
      "response": completion.choices[0].message.content
    }
  except ValueError as ve:
    logging.error(f"Invalid data error: {str(ve)}")
    raise HTTPException(status_code=422, detail=(f"Invalid data error: {str(ve)}"))
  except OpenAIError as oe:
    logging.error(f"OpenAI API Error: {str(oe)}")
    raise HTTPException(status_code=502, detail=(f"OpenAI API Error: {str(oe)}"))
  except HTTPException as he:
    logging.error(f"HTTP Error: {he.detail}")
    raise he
  except Exception as e:
    logging.exception(tr('ERROR_PROCESSING_REQUEST'))
    raise HTTPException(status_code=500, detail=str(e))