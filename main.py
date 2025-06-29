from src.etl.ETL import ETL 
import uvicorn
from src.assets.aux.flags import flags

# Airbyte 

from src.assets.aux.env import env
# GitHub env var
GITHUB_TOKEN = env["GITHUB_TOKEN"]

# Todos seus repositorios:  ["username/*"] ou 
# Repositorios especificos: ["username/repo1", "username/repo2"] ...
repos = ["bpthiago/oraculo-documentation", "bpthiago/oraculo"]

# Quais informações deseja trazer do github
streams = ["issues", "repositories", "pull_requests", "commits", "teams", "users", "issue_milestones", "projects_v2", "team_members", "team_memberships", "assignees", "branches"]

if(flags.etl == True or flags.etl_only == True):
    etl = ETL(repos, streams, GITHUB_TOKEN)
    try:
        etl.run()
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    if(flags.etl_only == True):
        print("Fim do programa")
        exit(0)

print("Prosseguindo para inicio da API.")
# --- API ---

api_root_path = "src.api.app"
port = 8000
config = uvicorn.Config(api_root_path + ":app",host="0.0.0.0", port=port, log_level="info", reload=True)
server = uvicorn.Server(config)
server.run()