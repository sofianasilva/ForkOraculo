from src.assets.pattern.singleton import SingletonMeta
import airbyte as ab
from airbyte.caches import PostgresCache
from os import getenv
from dotenv import load_dotenv

load_dotenv() # Loads env variables

# GitHub personal access token stored securely in environment variable
GITHUB_TOKEN = getenv("GITHUB_TOKEN")
GITHUB_REPOS = getenv("GITHUB_REPOS")

DB_HOST = getenv("DB_HOST")
DB_AB_DESTINATION_HOST = getenv("DB_AB_DESTINATION_HOST")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")

class airbyte:
    def __init__(self, repos, streams, metaclass=SingletonMeta):
        self.repos = repos
        self.streams = streams

    def start(self):
        print("Iniciando processo ETL...")
        # Configure the GitHub source
        source = ab.get_source(
            "source-github",
            install_if_missing=True,
            config={
                "repositories": self.repos,
                "credentials": {
                    "personal_access_token": GITHUB_TOKEN,
                },
            },
        )

        # Check source configuration
        source.check()

        # Select the streams to extract
        source.select_streams(self.streams)

        # Define PostgreSQL as a cache
        cache = PostgresCache(
            host = DB_HOST,
            port = DB_PORT,
            username = DB_USER,
            password = DB_PASSWORD,
            database = DB_NAME
        )

        # Read from the source
        read_result = source.read(force_full_refresh=True, cache=cache)

        # Define PostgreSQL as the destination
        destination = ab.get_destination(
            "destination-postgres",
            config={
                "host": DB_AB_DESTINATION_HOST,
                "port": int(DB_PORT),
                "database": DB_NAME,
                "username": DB_USER,
                "password": DB_PASSWORD,
                "schema": "public",
                "ssl": False,
                "sslmode": "disable"
            },
            docker_image=True
        )

        # Write the data to the destination
        write_result = destination.write(read_result, force_full_refresh=True, cache=cache)

        # Output result
        # print(write_result.__dict__)
        print("...Fim do processo de ETL")