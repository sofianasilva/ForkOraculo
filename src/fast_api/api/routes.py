from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.vanna_client import MyVanna

router = APIRouter()

class Question(BaseModel):
    question: str

vn = MyVanna(config={'print_prompt': False, 'print_sql': False})

@router.post("/ask")
async def ask_question(question: Question):
    try:
        sql_gerado = vn.generate_sql(question.question)
        resultado = vn.run_sql(sql_gerado)
        return {"result": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))