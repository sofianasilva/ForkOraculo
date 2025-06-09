from src.etl.airbyte import airbyte 

# Airbyte 

# Todos seus repositorios:  ["username/*"] ou 
# Repositorios especificos: ["username/repo1", "username/repo2"] ...
repos = ["bpthiago/oraculo"]

# Quais informações deseja trazer do github
streams = ["issues", "repositories", "pull_requests", "commits", "teams", "users", "issue_milestones", "projects_v2", "team_members", "team_memberships"]

    etl = airbyte(repos, streams)
    etl.start()
