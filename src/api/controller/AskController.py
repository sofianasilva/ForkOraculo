from src.assets.pattern.singleton import SingletonMeta
from src.api.models import Question, Response

from google import genai
from src.api.database.MyVanna import MyVanna

from src.assets.aux.env import env
# Gemini env vars
GEMINI_API_KEY = env["GEMINI_API_KEY"]
GEMINI_MODEL_NAME = env["GEMINI_MODEL_NAME"]

class AskController(metaclass=SingletonMeta):
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

        self.vn = MyVanna(config={
            'print_prompt': False, 
            'print_sql': False,
            'api_key': GEMINI_API_KEY,
            'model_name': GEMINI_MODEL_NAME
        })

        self.vn.prepare()

    def ask(self, question: Question):

        try:

            
            sql_gerado = self.vn.generate_sql(question.question)

            if "SELECT" not in sql_gerado.upper():
                return {"output": "Não consegui entender sua pergunta bem o suficiente para gerar uma resposta SQL válida."}

            resultado = self.vn.run_sql(sql_gerado)

            if not resultado:
                return {"output": "A consulta foi feita, mas não há dados correspondentes no banco."}

            # Prompt mais informativo
            prompt = f"""
            Você é um assistente que responde perguntas sobre dados extraídos do GitHub.

            Pergunta do usuário: "{question.question}"

            Resultado da consulta SQL: {resultado}

            Gere uma resposta clara e útil para o usuário, explicando o que o resultado significa.
            """

            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[Response],
                }
            )

            texto = response.parsed[0].texto
            return {"output": texto}

        except Exception as e:
            return {"output": f"Ocorreu um erro ao processar sua pergunta: {str(e)}"}