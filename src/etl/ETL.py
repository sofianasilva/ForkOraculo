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

    # --- Orquestração da Inserção ---
    def run(self):
        airbyte_cached_data = self.airbyte_extract()            # Extract
        transformed_data = self.data_transform(airbyte_cached_data)  # Transform

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

