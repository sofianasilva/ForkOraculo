from src.etl.airbyte import airbyte 
from src.assets.pattern.singleton import SingletonMeta
import uvicorn
from src.assets.aux.flags import flags

# Airbyte 

# Todos seus repositorios:  ["username/*"] ou 
# Repositorios especificos: ["username/repo1", "username/repo2"] ...
repos = ["bpthiago/oraculo-documentation", "bpthiago/oraculo"]

# Quais informações deseja trazer do github
streams = ["issues", "repositories", "pull_requests", "commits", "teams", "users", "issue_milestones", "projects_v2", "team_members", "team_memberships"]

if(flags.etl == True or flags.etl_only == True):
    etl = airbyte(repos, streams)
    try:
        etl.start()
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        print("Prosseguindo para inicio da API.")

    if(flags.etl_only == True):
        exit(0)

# --- API ---

api_root_path = "src.api.app"
port = 8000
config = uvicorn.Config(api_root_path + ":app", port=port, log_level="info", reload=True)
server = uvicorn.Server(config)
server.run()