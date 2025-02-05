"""Main app"""

from fastapi import FastAPI
from app.routers import resumes
from .locales.localization import Localization, tr
from .config import client  # pylint: disable=unused-import

Localization.set_language("es")

app = FastAPI()

app.include_router(resumes.router, prefix="/api")


@app.get("/")
async def root():
    """Returns welcome message"""
    return {"message": tr("WELCOME")}
