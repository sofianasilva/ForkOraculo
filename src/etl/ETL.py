from sqlalchemy import create_engine, text
from src.assets.pattern.singleton import SingletonMeta
from src.assets.aux.env import env
# GitHub env var
GITHUB_TOKEN = env["GITHUB_TOKEN"]
# Db env vars
DB_HOST = env["DB_HOST"]
DB_AB_DESTINATION_HOST = env["DB_AB_DESTINATION_HOST"]
DB_PORT = env["DB_PORT"]
DB_NAME = env["DB_NAME"]
DB_USER = env["DB_USER"]
DB_PASSWORD = env["DB_PASSWORD"]

# String de conexão SQLAlchemy
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class ETL(metaclass=SingletonMeta):
    def __init__(self, repos, streams, github_token):
        self.repos = repos
        self.streams = streams
        self.github_token = github_token
        
        # Conexão do branco de dados
        self.engine = create_engine(DATABASE_URL)

    def getAirbyteRepos():
        return repos

    def getAirbyteStreams():
        return streams

    ''' Deve receber uma lista de strings, com as streams. 
        ex: streams = ["issues", "repositories", "pull_requests", ...]
    ''' 
    def setAirbyteStreams(self, streams):
        self.streams = streams

    ''' Deve receber um novo token do github
    ''' 
    def setAirbyteGithubToken(self, streams):
        self.github_token = github_token

    def airbyte_extract(self):
        airbyte_instance = airbyte(self.repos, self.streams, self.github_token)
        try:
            return airbyte_instance.extract()
        except Exception as e:
            print(f"Ocorreu um erro na execução do airbyte: {e}")
            return None
