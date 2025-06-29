import airbyte as ab
import pandas as pd
from sqlalchemy import create_engine, text
import datetime # Para timestamps
import pytz
import json

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

# --- 1. Configuração do Banco de Dados de Destino ---
# Substitua pelas suas credenciais do PostgreSQL

# String de conexão SQLAlchemy
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# --- Dicionários para mapear IDs do Airbyte para IDs do seu BD (se suas PKs são auto-increment) ---
# Se suas IDs de destino forem auto-increment, você precisará de um mapeamento
# Se você usar as IDs originais do Airbyte como PKs, este passo é simplificado.
user_id_map = {}
# --- Funções para Mapear e Inserir ---

def insert_users(users_airbyte):
    print("\n--- Loading Users ---")
    if len(users_airbyte) == 0:
        print("Nenhum dado de usuário no cache do Airbyte.")
        return

    # print(users_airbyte)

    try:
        # Tenta inserir. Se 'id' for PK e já existir, vai dar erro.
        # O ideal é um UPSERT. Aqui, vamos simular um insert ignorando duplicatas ou um UPSERT.
        with engine.connect() as connection:
            for index, user in enumerate(users_airbyte):
                # Verifica se o usuário já existe pelo airbyte_id (se você mantiver essa coluna no seu DB)
                # Ou pelo 'login' se 'login' for UNIQUE
                
                query = text(f"SELECT id FROM \"user\" WHERE id = :id") # usar "user" por ser palavra reservada
                result = connection.execute(query, {'id': user['id']}).fetchone()

                if result:
                    user_id_map[user['id']] = result[0] # Mapeia ID Airbyte para ID existente no BD
                    print(f"Usuário '{user}' já existe. ID: {result[0]}")
                else:
                    insert_query = text(f"INSERT INTO \"user\" (id, login, html_url) VALUES (:id, :login, :html_url) RETURNING id")
                    new_id = connection.execute(insert_query, {'id': user['id'], 'login': user['login'], 'html_url': user['html_url']}).scalar_one()
                    user_id_map[user['id']] = new_id
                    print(f"Usuário '{user['login']}' inserido com ID: {new_id}")
            connection.commit() # Commit das operações

    except Exception as e:
        print(f"Erro ao inserir users: {e}")
    print("--- Users Done ---")

def data_transform(read_result):
    print("\n--- Data Transform Initiated---")
    added_user_logins = []
    users = []
    for stream_name, dataset in read_result.streams.items():
        for i, record in enumerate(dataset):
            ## Populando usuários em todas as streams
            if(getattr(record, 'user', False) != False):
                # print(f"  Record {i+1}: id: {record.user['id']}, login:{record.user['login']}") # Imprime toda vez q encontra usuario
                user_login = record.user['login'].lower()
                if(user_login not in added_user_logins):
                    users.append({
                        "id": record.user['id'],
                        "login": user_login,
                        "html_url": record.user['html_url']
                    })
                    added_user_logins.append(user_login)
            # Se a stream for assginees, adiciona mais usuarios, se possível
            if (stream_name.lower() == 'assignees'):
                # print(f"    assignee {i+1}: id: {record.id}, login: {record.login}, html_url: {record.html_url}") # Imprime toda vez q encontra usuario
                user_login = record.login.lower()
                if(user_login not in added_user_logins):
                    users.append({
                        "id": record.id,
                        "login": user_login,
                        "html_url": record.html_url
                    })
                    added_user_logins.append(user_login)
    print("--- Data Transform Completed ---")
    return {
        "users": users,
    } 


# --- Execução ---
if __name__ == "__main__":
    try:
        run_data_insertion(read_result)
        print("\nProcesso de inserção de dados concluído!")
    except Exception as e:
        print(f"\nOcorreu um erro fatal durante a inserção de dados: {e}")
    finally:
        engine.dispose() # Fechar a conexão com o banco de dados
        print("Conexão com o banco de dados fechada.")