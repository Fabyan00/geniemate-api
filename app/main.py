from fastapi import FastAPI
from app.routers import resumes
from .locales.localization import Localization, tr
from .config import client
from starlette.middleware.cors import CORSMiddleware

Localization.set_language('es')

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
  return {"message": tr('WELCOME')}