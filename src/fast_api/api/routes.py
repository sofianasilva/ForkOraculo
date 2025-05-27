from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.vanna_client import MyVanna
from google import genai
import os

router = APIRouter()

class Question(BaseModel):
    question: str

vn = MyVanna(config={'print_prompt': False, 'print_sql': False})

client = genai.Client()

class Resposta(BaseModel):
    texto: str

@router.post("/ask")
async def ask_question(question: Question):
    try:
        sql_gerado = vn.generate_sql(question.question)
        resultado = vn.run_sql(sql_gerado)
        response = client.models.generate_content(model=os.getenv("MODEL_NAME"),contents="Transforme"+ {"result": resultado} +"em uma frase", config= {
        "response_mime_type": "application/json",
        "response_schema": list[Resposta],
        },)
        return {"output": response.parsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))