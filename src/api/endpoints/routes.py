from fastapi import APIRouter, HTTPException
from src.api.models import Question, Response
from src.api.controller.AskController import AskController

router = APIRouter()

ask = AskController()

@router.post("/ask")
async def ask_question(question: Question):
    try:
        return ask.ask(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))