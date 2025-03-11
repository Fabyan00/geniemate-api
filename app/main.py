"""Main app"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers import mind_maps, user_content
from .locales.localization import Localization, tr
from .config import client  # pylint: disable=unused-import

Localization.set_language("es")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_content.router, prefix="/api")
app.include_router(mind_maps.router, prefix="/api")


@app.get("/")
async def root():
    """Returns welcome message"""
    return {"message": tr("WELCOME")}
