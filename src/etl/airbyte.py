from __future__ import annotations
import airbyte as ab
from airbyte.caches import PostgresCache
from os import getenv
from dotenv import load_dotenv

load_dotenv() # Loads env variables

# GitHub personal access token stored securely in environment variable
GITHUB_TOKEN = getenv("GITHUB_TOKEN")

def startETL():
    # Configure the GitHub source
    source = ab.get_source(
        "source-github",
        install_if_missing=True,
        config={
            "repositories": ["bedrohenr/angular-xiv"],
            "credentials": {
                "personal_access_token": GITHUB_TOKEN,
            },
        },
    )

    # Check source configuration
    source.check()

    # Select the streams to extract
    source.select_streams([
        "issues", "repositories", "pull_requests", "commits",
        "teams", "users", "issue_milestones", "projects_v2",
        "team_members", "team_memberships"
    ])

    # Define PostgreSQL as a cache
    cache = PostgresCache(
        host="localhost",
        port=5432,
        username="postgres",
        password="postgres",
        database="databasex"
    )

    # Read from the source
    read_result = source.read(force_full_refresh=True, cache=cache)

    # Define PostgreSQL as the destination
    destination = ab.get_destination(
        "destination-postgres",
        config={
            "host": "host.docker.internal", # Funciona no windows...
            "port": 5432,
            "database": "databasex",
            "username": "postgres",
            "password": "postgres",
            "schema": "public",
            "ssl": False,
            "sslmode": "disable"
        },
        docker_image=True
    )

    # Write the data to the destination
    write_result = destination.write(read_result, force_full_refresh=True, cache=cache)

    # Output result
    print(write_result.__dict__)