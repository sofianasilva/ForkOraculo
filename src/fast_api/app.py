from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel
from src.fast_api.database.vanna_ai import MyVanna, get_schema
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# DB env vars
DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_URL = getenv("DB_URL")

# Gemini env vars
GEMINI_API_KEY = getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = getenv("GEMINI_MODEL_NAME")

app = FastAPI()

client = genai.Client(api_key=GEMINI_API_KEY)

vn = MyVanna(config={
    'print_prompt': False, 
    'print_sql': False,
    'api_key': GEMINI_API_KEY,
    'model_name': GEMINI_MODEL_NAME
})

vn.connect_to_postgres(
    host = DB_HOST,
    port = DB_PORT,
    dbname = DB_NAME,
    user = DB_USER,
    password = DB_PASSWORD
)

schema = get_schema(vn.db_url)

vn.train(ddl=schema)
vn.train(documentation="""A  tabela commits armazena informações sobre os commits realizados em repositórios, incluindo o nome do repositório, o branch, a data de criação, o hash SHA do commit, URLs associadas e diversos campos em formato JSON que detalham o conteúdo do commit, os autores, os responsáveis pela aplicação e os pais do commit. Os campos iniciados por _airbyte_ são metadados técnicos usados para controle de extração e versionamento dos dados.
A tabela issue_milestones representa os marcos definidos nos repositórios para organizar o progresso das issues. Ela contém informações como o repositório, título e descrição do marco, estado (aberto ou fechado), contagens de issues abertas e fechadas, e datas relevantes como criação, atualização, encerramento e prazo.
A tabela issues registra as issues criadas nos repositórios, com detalhes como título, estado, descrição, usuário autor, labels, responsáveis atribuídos, associação com pull requests e marcos, número de comentários, e datas de criação, atualização e encerramento. Há também campos JSON que armazenam dados estruturados como informações de usuários e reações.
A tabela projects_v2 reúne dados sobre projetos do tipo GitHub Projects versão 2, contendo informações como título, descrição curta, status de visibilidade, se é um template, se está fechado, URLs associadas e o repositório ao qual pertence. Campos booleanos indicam permissões de visualização e edição por parte do usuário.
A tabela pull_requests registra os pull requests enviados nos repositórios, contendo o título, corpo, estado, data de criação, encerramento e merge, bem como URLs e status relacionados. Também inclui vários campos em formato JSON detalhando o usuário que criou o PR, revisores solicitados, branches de origem e destino, e links para outros recursos.
A tabela repositories contém os dados gerais dos repositórios. Inclui identificadores como nome, descrição, URLs da API, estatísticas como número de estrelas, forks, issues abertas, permissões, visibilidade, e informações sobre recursos habilitados (wiki, issues, downloads, páginas, entre outros). Também são armazenadas datas de criação, atualização e último push, além de dados sobre a licença e tópicos associados.
A tabela team_members lista os membros de equipes dentro de uma organização, com informações como login, ID, URLs de perfil e eventos, tipo de conta, se é administrador do site, e a organização e equipe às quais pertencem.
A tabela team_memberships relaciona usuários a equipes específicas, com campos que indicam o estado da associação, o papel do membro, a organização, o slug da equipe e o nome de usuário correspondente.
A tabela teams armazena dados sobre equipes em uma organização, incluindo nome, slug, descrição, privacidade, configuração de notificações, permissões de acesso, URLs relacionadas e dados sobre a equipe-pai quando aplicável.
Por fim, a tabela users contém informações sobre os usuários do GitHub, com dados como login, ID, tipo de conta, URLs de perfil e atividades, organização associada, e se o usuário é um administrador. Também contém informações extraídas via API, como avatares e dados de eventos.
Cada uma dessas tabelas utiliza índices nos campos de extração do Airbyte e em campos principais como IDs ou SHAs, permitindo buscas eficientes e controle sobre a origem e atualização dos dados.""")

vn.train(sql="""
SELECT
    i.repository,
    COUNT(*) AS total_issues_abertas,
    MAX(i.created_at) AS data_ultima_issue
FROM
    public.issues i
WHERE
    i.state = 'open'
GROUP BY
    i.repository
ORDER BY
    total_issues_abertas DESC
LIMIT 10;
""")

class Question(BaseModel):
    question: str
    
class Resposta(BaseModel):
    texto: str

@app.post("/ask")
async def ask_question(question: Question):
    try:
        sql_gerado = vn.generate_sql(question.question)
        resultado = vn.run_sql(sql_gerado)
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents="Transforme"+ str({"result": resultado}) +"em uma frase",
            config={
                "response_mime_type": "application/json",
                "response_schema": list[Resposta],
                }
            )
        texto = response.parsed[0].texto
        return {"output":texto}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))