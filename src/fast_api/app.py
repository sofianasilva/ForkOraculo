from src.fast_api.endpoints.routes import router

from fastapi import FastAPI, HTTPException
from google import genai

from src.fast_api.database.MyVanna import MyVanna

app = FastAPI()

app.include_router(router)