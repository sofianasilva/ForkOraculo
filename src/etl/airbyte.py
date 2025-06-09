from src.assets.pattern.singleton import SingletonMeta
import airbyte as ab
from airbyte.caches import PostgresCache

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

class airbyte:
    def __init__(self, repos, streams, metaclass=SingletonMeta):
        self.repos = repos
        self.streams = streams

    def start(self):
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