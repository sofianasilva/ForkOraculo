import pandas as pd
from sqlalchemy import create_engine, text
import datetime # Para timestamps
import pytz
import json

from src.etl.airbyte import airbyte
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

    def load_data(self, transformed_data):
        # print("\nUsers")
        # print(transformed_data['users'])
        # print("\nRepos")
        # print(transformed_data['repositories'])
        # print("\nBranches")
        # print(transformed_data['branches'])
        # print("\nMilestones")
        # print(transformed_data['milestones'])
        # print("\nissues")
        # print(transformed_data['issues'][0])
        # print("\nPull requests")
        # print(transformed_data['pull_requests'][0])
        # print("\ncommits")
        # print(transformed_data['commits'][0])

        # Ordem de inserção é crucial devido às chaves estrangeiras
        self.load_users(transformed_data['users'])
        self.load_repositories(transformed_data['repositories'])
        self.load_milestones(transformed_data['milestones']) # Depende de repositorios
        self.load_branches(transformed_data['branches']) # Depende de repositórios
        self.load_issues(transformed_data['issues'])
        self.load_pull_requests(transformed_data['pull_requests'])
    # --- Orquestração da Inserção ---
    def run(self):
        airbyte_cached_data = self.airbyte_extract()            # Extract
        transformed_data = self.data_transform(airbyte_cached_data)  # Transform
        self.load_data(transformed_data)                             # Load

    def data_transform(self, read_result):
        print("\n--- Data Transform Initiated---")
        added_user_logins = [] # Mapeia logins ja inseridos no users
        added_repo_branches = [] # Mapeia repo:branch ja inseridos

        users = []
        issues = []
        commits = []
        branches = []
        milestones = []
        repositories = []
        pull_requests = []

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

                ## Populando repos em todas as streams
                if(getattr(record, 'repository', False) != False):
                    repo = record.repository.lower()
                    # print(f"  Record {i+1}: repo: {repo}") # Imprime toda vez q encontra um repositório
                    if(repo not in repositories):
                        repositories.append(repo)
                
                ## Populando branches em todas as streams
                if(getattr(record, 'branch', False) != False):
                    branch = record.branch
                    # print(f"  Record {i+1}: branch: {record}") # Imprime toda vez q encontra um branch
                    repository = record.repository.lower()
                    branch = record.branch.lower()
                    repo_branch = f"{repository}:{branch}"
                    if(repo_branch not in added_repo_branches):
                        branches.append({
                            "repository": repository,
                            "branch": branch
                        })
                        added_repo_branches.append(repo_branch)
                        
                ## Populando milestones em todas as streams
                if (stream_name.lower() == 'issue_milestones'):
                    # print(f"    milestone {i+1}: id: {record.id}, title: {record.title}, body: {record.description}, number: {record.number}, state: {record.state}, created_at: {record.created_at}, updated_at: {record.updated_at}, creator: {record.creator['id']}") # Imprime toda vez q encontra milestone
                    
                    milestones.append({
                        "id": record.id, "repository": record.repository.lower(), "title": record.title, "description": record.description, "number": record.number, "state": record.state, "created_at": record.created_at, "updated_at": record.updated_at, "creator": record.creator['id']
                    })

                # Se a stream for issues
                if (stream_name.lower() == 'issues'):
                    # print(f"    issue {i+1}: {record}") # Imprime toda vez q encontra issues

                    issues.append({
                        "id": record.id, "title": record.title, "body": record.body, "number": record.number, "html_url": record.html_url, "created_at": record.created_at, "updated_at": record.updated_at, "assignees": record.assignees, "created_by": record.user['id'], "repository": record.repository.lower(), "milestone": record.milestone 
                    })

                # Se a stream for pull requests
                if (stream_name.lower() == 'pull_requests'):
                    # print(f"    assignee {i+1}: id: {record.id}, login: {record.login}, html_url: {record.html_url}") # Imprime toda vez q encontra pull_requests

                    pull_requests.append({
                        "id": record.id, "created_by": record.user['id'], "repository": record.repository.lower(), "number": record.number, "state": record.state, "title": record.title, "body": record.body, "html_url": record.html_url, "created_at": record.created_at, "updated_at": record.updated_at, "merged_at": record.merged_at, "milestone": record.milestone, "assignees": record.assignees 
                    })

                # Se a stream for commits
                if (stream_name.lower() == 'commits'):
                    # print(f"    commit {i+1}: {record}") # Imprime toda vez q encontra commit

                    # caso nao tenha author no commit, ele será ignorado.
                    # possivelmente problemas de vinculo email no commit -> email cadastrado no github
                    commitHasAuthor = getattr(record, 'author', False)
                    if(commitHasAuthor != False and commitHasAuthor != None):
                        user_login = record.author['login'].lower()
                        if(user_login not in added_user_logins):
                            users.append({
                                "id": record.author['id'],
                                "login": user_login,
                                "html_url": record.author['html_url']
                            })
                            added_user_logins.append(user_login)

                        commits.append({
                            "user_id": record.author['id'], "repository": record.repository.lower(), "branch": record.branch.lower(), "created_at": record.created_at, "message": record.commit['message'], "sha": record.sha, "parents": record.parents, "html_url": record.html_url 
                        })
                
                # Se a stream for assginees, adiciona mais usuarios, se possível
                if (stream_name.lower() == 'assignees'):
                    # print(f"    assignee {i+1}: id: {record.id}, login: {record.login}, html_url: {record.html_url}") # Imprime toda vez q encontra usuario em assignees
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
            "repositories": repositories,
            "branches": branches,
            "milestones": milestones,
            "issues": issues,
            "pull_requests": pull_requests,
            "commits": commits
        } 

    # --- Inserindo Usuários ---
    def load_users(self,users_airbyte):
        print("\n--- Loading Users ---")
        if len(users_airbyte) == 0:
            print("Nenhum dado de usuário no cache do Airbyte.")
            return

        # print(users_airbyte)

        try:
            # Tenta inserir. Se 'id' for PK e já existir, vai dar erro.
            # O ideal é um UPSERT. Aqui, vamos simular um insert ignorando duplicatas ou um UPSERT.
            with self.engine.connect() as connection:
                for index, user in enumerate(users_airbyte):
                    # Verifica se o usuário já existe pelo airbyte_id (se você mantiver essa coluna no seu DB)
                    # Ou pelo 'login' se 'login' for UNIQUE
                    
                    query = text(f"SELECT id FROM \"user\" WHERE id = :id") # usar "user" por ser palavra reservada
                    result = connection.execute(query, {'id': user['id']}).fetchone()

                    if result:
                        print(f"Usuário '{user['login']}' já existe. ID: {result[0]}")
                    else:
                        insert_query = text(f"INSERT INTO \"user\" (id, login, html_url) VALUES (:id, :login, :html_url) RETURNING id")
                        new_id = connection.execute(insert_query, {'id': user['id'], 'login': user['login'], 'html_url': user['html_url']}).scalar_one()
                        print(f"Usuário '{user['login']}' inserido com ID: {new_id}")
                connection.commit() # Commit das operações

        except Exception as e:
            print(f"Erro ao inserir users: {e}")
        print("--- Users Done ---")

    def load_repositories(self, repos_airbyte):
        print("\n--- Loading Repositories ---")
        if len(repos_airbyte) == 0:
            print("Nenhum dado de repositório no cache do Airbyte.")
            return

        # print(repos_airbyte);
        try:
            with self.engine.connect() as connection:
                for index, repo_name in enumerate(repos_airbyte):
                    query = text(f"SELECT id FROM repository WHERE name = :name")
                    result = connection.execute(query, {'name': repo_name}).fetchone()

                    if result:
                        print(f"Repositório '{repo_name}' já existe. ID: {result[0]}")
                    else:
                        insert_query = text(f"INSERT INTO repository (name) VALUES (:name) RETURNING id")
                        new_id = connection.execute(insert_query, {'name': repo_name}).scalar_one()
                        print(f"Repositório '{repo_name}' inserido com ID: {new_id}")
                connection.commit()
        except Exception as e:
            print(f"Erro ao inserir repositories: {e}")

        print("\n--- Repositories Done ---")

    def load_branches(self, branches_airbyte):
        print("\n--- Loading Branches ---")
        if len(branches_airbyte) == 0:
            print("Nenhum dado de branch no cache do Airbyte.")
            return

        # print(branches_airbyte)

        try:
            with self.engine.connect() as connection:
                for index, branch in enumerate(branches_airbyte):
                    query = text(f"SELECT id FROM repository WHERE name = :name")
                    repo_result = connection.execute(query, {'name': branch['repository']}).fetchone()
                    repository_id = repo_result[0]

                    query = text(f"SELECT id FROM branch WHERE name = :name AND repository_id = :repository_id")
                    result = connection.execute(query, {'name': branch['branch'], 'repository_id': repository_id}).fetchone()

                    branch_repo = f"{branch['repository']}:{branch['branch']}"
                    if result:
                        print(f"Branch '{branch['branch']}' já existe para o repositório {branch['repository']}. ID: {result[0]}")
                    else:
                        insert_query = text(f"INSERT INTO branch (name, repository_id) VALUES (:name, :repository_id) RETURNING id")
                        new_id = connection.execute(insert_query, {'name': branch['branch'], 'repository_id': repository_id}).scalar_one()
                        print(f"Branch '{branch['branch']}' inserida para repo {branch['repository']} com ID: {new_id}")
                connection.commit()
        except Exception as e:
            print(f"Erro ao inserir branches: {e}")

        print("\n--- Branches Done ---")


    def load_milestones(self, milestones_airbyte):
        print("\n--- Loading Milestones ---")
        if len(milestones_airbyte) == 0:
            print("Nenhum dado de repositório no cache do Airbyte.")
            return

        # print(milestones_airbyte);
        # print('\n')

        try:
            with self.engine.connect() as connection:
                for index, milestone in enumerate(milestones_airbyte):
                    query = text(f"SELECT id FROM milestone WHERE id = :id")
                    result = connection.execute(query, {'id': milestone['id']}).fetchone()

                    if result:
                        print(f"Milestone '{milestone['title']}' já existe. ID: {result[0]}")
                    else:
                        # Resolvendo id repo
                        query = text(f"SELECT id FROM repository WHERE name = :name")
                        result = connection.execute(query, {'name': milestone['repository']}).fetchone()
                        repository_id = result[0];

                        # Inserindo SaoPaulo TIMEZONE
                        milestone['created_at'] = self.handlingTimeZoneToPostgres(milestone['created_at'])
                        milestone['updated_at'] = self.handlingTimeZoneToPostgres(milestone['updated_at'])

                        insert_query = text(f"INSERT INTO milestone (id, repository_id, title, description, number, state, created_at, updated_at, creator) VALUES (:id, :repository_id, :title, :description, :number, :state, :created_at, :updated_at, :creator) RETURNING id")
                        new_id = connection.execute(insert_query, {'id': milestone['id'], 'repository_id': repository_id, 'title': milestone['title'], 'description': milestone['description'], 'number': milestone['number'], 'state': milestone['state'], 'created_at': milestone['created_at'], 'updated_at': milestone['updated_at'], 'creator': milestone['creator']}).scalar_one()
                        print(f"Milestone '{milestone['title']}' inserida com ID: {new_id}")
                connection.commit()
        except Exception as e:
            print(f"Erro ao inserir milestones: {e}")

        print("\n--- Milestones Done ---")

    def load_issues(self, issues_airbyte):
        print("\n--- Loading Issues ---")
        if len(issues_airbyte) == 0:
            print("Nenhum dado de issue no cache do Airbyte.")
            return

        # print(issues_airbyte[0])

        try:
            with self.engine.connect() as connection:
                for index, issue in enumerate(issues_airbyte):
                    # Preparativos para inserir
                    query = text(f"SELECT id FROM issue WHERE id = :id")
                    result = connection.execute(query, {'id': issue['id']}).fetchone()

                    if result:
                        print(f"Issue '{issue['title']}' já existe. ID: {result[0]}")
                    else:
                        # Resolvendo id repo
                        query = text(f"SELECT id FROM repository WHERE name = :name")
                        repo_id_result = connection.execute(query, {'name': issue['repository']}).fetchone()
                        repository_id = repo_id_result[0];

                        # Se existe milestone vinculada
                        milestone_id = None
                        if(issue['milestone']):
                            # print("issue milestone id: ", issue['milestone']['id'])
                            milestone_id = issue['milestone']['id']

                        # Inserindo SaoPaulo TIMEZONE
                        issue['created_at'] = self.handlingTimeZoneToPostgres(issue['created_at'])
                        issue['updated_at'] = self.handlingTimeZoneToPostgres(issue['updated_at'])

                        insert_query = text(f"INSERT INTO issue (id, title, body, number, html_url, created_at, updated_at, created_by, repository_id, milestone_id) VALUES (:id, :title, :body, :number, :html_url, :created_at, :updated_at, :created_by, :repository_id, :milestone_id) RETURNING id")

                        new_issue_id = connection.execute(insert_query, {'id': issue['id'], 'title': issue['title'], 'body': issue['body'], 'number': issue['number'], 'html_url': issue['html_url'], 'created_at': issue['created_at'], 'updated_at': issue['updated_at'], 'created_by': issue['created_by'], 'repository_id': repository_id, 'milestone_id': milestone_id}).scalar_one()
                        print(f"Issue '{issue['title']}' inserida com ID: {new_issue_id}")

                        # 
                        if(issue['assignees']):
                            for assignee in issue['assignees']:
                                # print(f"Row: issue_id: {issue['id']}; ass: {assignee['id']}")
                                insert_query = text(f"INSERT INTO issue_assignees (issue_id, user_id) VALUES (:issue_id, :user_id)")
                                connection.execute(insert_query, {'issue_id': issue['id'], 'user_id': assignee['id']})
                                print(f"Assignee '{assignee['login']}' adicionado.")
                        
                connection.commit()
        except Exception as e:
            print(f"Erro ao inserir issues: {e}")

        print("\n--- Issues Done ---")


    def load_pull_requests(self, prs_airbyte):
        print("\n--- Loading Pull Requests ---")
        if len(prs_airbyte) == 0:
            print("Nenhum dado de pull request no cache do Airbyte.")
            return

        # print(prs_airbyte[0])
        # print(prs_airbyte[1])

        try:
            with self.engine.connect() as connection:
                for index, pr in enumerate(prs_airbyte):
                    # Preparativos para inserir
                    query = text(f"SELECT id FROM pull_requests WHERE id = :id")
                    result = connection.execute(query, {'id': pr['id']}).fetchone()

                    if result:
                        print(f"Pull request '{pr['title']}' já existe. ID: {result[0]}")
                    else:
                        # Resolvendo id repo
                        query = text(f"SELECT id FROM repository WHERE name = :name")
                        repo_id_result = connection.execute(query, {'name': pr['repository']}).fetchone()
                        repository_id = repo_id_result[0];

                        # Se existe milestone vinculada
                        milestone_id = None
                        if(pr['milestone']):
                            print("issue milestone id: ", pr['milestone']['id'])
                            milestone_id = pr['milestone']['id']

                        # Inserindo SaoPaulo TIMEZONE
                        pr['created_at'] = self.handlingTimeZoneToPostgres(pr['created_at'])
                        pr['updated_at'] = self.handlingTimeZoneToPostgres(pr['updated_at'])

                        insert_query = text(f"INSERT INTO pull_requests (id, created_by, repository_id, number, state, title, body, html_url, created_at, updated_at, milestone_id) VALUES (:id, :created_by, :repository_id, :number, :state, :title, :body, :html_url, :created_at, :updated_at, :milestone_id) RETURNING id")

                        new_pr_id = connection.execute(insert_query, {'id': pr['id'], 'created_by': pr['created_by'], 'repository_id': repository_id, 'number': pr['number'], 'state': pr['state'], 'title': pr['title'], 'body': pr['body'], 'html_url': pr['html_url'], 'created_at': pr['created_at'], 'updated_at': pr['updated_at'], 'milestone_id': milestone_id}).scalar_one()
                        print(f"Pull request '{pr['title']}' inserida com ID: {new_pr_id}")

                        if(pr['assignees']):
                            for assignee in issue['assignees']:
                                # print(f"Row: pr_id: {pr['id']}; ass: {assignee['id']}")
                                insert_query = text(f"INSERT INTO pull_request_assignees (pull_request_id, user_id) VALUES (:pull_request_id, :user_id)")
                                connection.execute(insert_query, {'pull_request_id': pr['id'], 'user_id': assignee['id']})
                                print(f"Assignee '{assignee['login']}' adicionado.")
                connection.commit()
        except Exception as e:
            print(f"Erro ao inserir issues: {e}")

        print("\n--- Pull Requests Done ---")
    def handlingTimeZoneToPostgres(self, naive_datetime):
        # Definir o fuso horário brasileiro de São Paulo
        brazil_tz = pytz.timezone('America/Sao_Paulo')

        # Isso anexa a informação de fuso horário SEM mudar os componentes de hora.
        dt_localized_brazil = brazil_tz.localize(naive_datetime, is_dst=None) # 'is_dst=None' para inferir DST se houver ambiguidade

        # print(f"Localizado (Brasil): {dt_localized_brazil} | Timezone: {dt_localized_brazil.tzinfo}")

        return dt_localized_brazil