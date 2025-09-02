from src.api.endpoints.routes import router

from fastapi import FastAPI, HTTPException
from google import genai

from src.api.database.MyVanna import MyVanna

app = FastAPI()

app.include_router(router)