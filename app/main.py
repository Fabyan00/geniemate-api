"""Main app"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers import resumes
from .locales.localization import Localization, tr
from .config import client  # pylint: disable=unused-import

Localization.set_language("es")

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

app.include_router(resumes.router, prefix="/api")


@app.get("/")
async def root():
    """Returns welcome message"""
    return {"message": tr("WELCOME")}
