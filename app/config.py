"""Setting api config"""

import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from app.locales.localization import Localization, tr

load_dotenv()

Localization.set_language("en")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error(tr("ERROR_API_KEY"))
    raise SystemExit()

client = OpenAI(api_key=api_key)
