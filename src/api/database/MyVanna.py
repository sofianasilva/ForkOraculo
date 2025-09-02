from src.assets.pattern.singleton import SingletonMeta

from vanna.vannadb import VannaDB_VectorStore
from vanna.google import GoogleGeminiChat
from vanna.chromadb import ChromaDB_VectorStore
import psycopg2
import os

from src.assets.aux.env import env
# DB env vars
DB_HOST = env["DB_HOST"]
DB_PORT = env["DB_PORT"]
DB_NAME = env["DB_NAME"]
DB_USER = env["DB_USER"]
DB_PASSWORD = env["DB_PASSWORD"]
DB_URL = env["DB_URL"]

class MyVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        ChromaDB_VectorStore.__init__(self, config=config)
        
        GEMINI_API_KEY = config.get('api_key')
        GEMINI_MODEL_NAME = config.get('model_name')
        
        GoogleGeminiChat.__init__(self, config={
            'api_key': GEMINI_API_KEY, 
            'model_name': GEMINI_MODEL_NAME
        })
        
        self.print_prompt = config.get('print_prompt', False)
        self.print_sql = config.get('print_sql', False)
        self.db_url = DB_URL

    def get_schema(self):
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            tables = cursor.fetchall()

            schema = []
            for table in tables:
                table_name = table[0]

                cursor.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public';
                """, (table_name,))
                columns = cursor.fetchall()

                cursor.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = %s 
                    AND tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = 'public';
                """, (table_name,))
                pk_columns = {row[0] for row in cursor.fetchall()}

                create_stmt = f"CREATE TABLE {table_name} (\n"
                for i, col in enumerate(columns):
                    col_name, col_type, is_nullable, default = col
                    not_null = "NOT NULL" if is_nullable == "NO" else ""
                    is_pk = "PRIMARY KEY" if col_name in pk_columns else ""
                    default_str = f"DEFAULT {default}" if default else ""

                    parts = [col_name, col_type, default_str, not_null, is_pk]
                    col_def = "    " + " ".join(p for p in parts if p)

                    if i < len(columns) - 1:
                        col_def += ",\n"
                    else:
                        col_def += "\n"

                    create_stmt += col_def
                create_stmt += ");"
                schema.append(create_stmt)

            conn.close()
            return "\n\n".join(schema)
        except Exception as e:
            print(f"Erro ao obter esquema: {e}")
            return ""

    def connect_to_postgres(self, host, dbname, user, password, port):
        self.db_url = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
        self.schema = self.get_schema()

    def run_sql(self, sql):
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            print(f"Erro ao executar SQL: {e}")
            return []


    def prepare(self):
        self.connect_to_postgres(
            host = DB_HOST,
            port = DB_PORT,
            dbname = DB_NAME,
            user = DB_USER,
            password = DB_PASSWORD
        )

        schema = self.get_schema()

        self.train(ddl=self.schema)

        self.train(documentation="""
        A tabela repository armazena os repositórios, identificados por um ID único e nome.

        A tabela user contém informações dos usuários, como login e URL de perfil. É usada como referência em outras tabelas, como quem criou issues, pull requests e milestones.

        A tabela milestone representa marcos definidos nos repositórios, contendo título, descrição, número, estado (aberta ou fechada), datas de criação e atualização, o repositório ao qual pertence e o usuário criador.

        A tabela issue armazena tarefas ou bugs reportados. Contém título, corpo, número, autor, repositório, milestone relacionada, datas e URL. As atribuições de usuários a uma issue são registradas em issue_assignees.

        A tabela pull_requests armazena os pull requests criados nos repositórios. Inclui título, corpo, número, estado, criador, repositório, milestone (opcional), datas e URL. Os responsáveis são registrados em pull_request_assignees.

        A tabela branch armazena os nomes de branches de cada repositório.

        A tabela commits armazena cada commit feito. Cada registro contém o SHA, mensagem, autor (usuário), repositório, branch (opcional), data de criação e URL. Também há referência à tabela de usuários.

        A tabela parents_commits representa a relação entre commits e seus pais (para commits com múltiplos ancestrais, como em merges). Usa o SHA do commit pai e o ID do commit filho.

        A tabela issue_assignees relaciona múltiplos usuários a uma mesma issue, representando atribuições de tarefas. É uma tabela de junção entre issues e usuários.

        A tabela pull_request_assignees relaciona múltiplos usuários a um pull request, permitindo registrar quem é responsável por revisar ou aprovar um PR.

        O modelo garante integridade por meio de chaves estrangeiras, e unicidade de registros por restrições compostas (como número + repositório para issues, pull requests e milestones).
        """)
        
        self.train(sql="""
        -- 1. Repositórios com mais issues abertas
        SELECT
            r.name AS repositorio,
            COUNT(*) AS total_issues_abertas,
            MAX(i.created_at) AS data_ultima_issue
        FROM
            issue i
        JOIN
            repository r ON i.repository_id = r.id
        WHERE
            i.state = 'open'
        GROUP BY
            r.name
        ORDER BY
            total_issues_abertas DESC
        LIMIT 10;
        """)

        self.train(sql="""
        -- 2. Top 5 usuários com mais commits registrados
        SELECT
            u.login,
            COUNT(*) AS total_commits
        FROM
            commits c
        JOIN
            user_info u ON c.user_id = u.id
        GROUP BY
            u.login
        ORDER BY
            total_commits DESC
        LIMIT 5;
        """)

        self.train(sql="""
        -- 3. Total de pull requests abertos por repositório
        SELECT
            r.name AS repositorio,
            COUNT(*) AS total_pr_abertos
        FROM
            pull_requests pr
        JOIN
            repository r ON pr.repository_id = r.id
        WHERE
            pr.state = 'open'
        GROUP BY
            r.name
        ORDER BY
            total_pr_abertos DESC;
        """)

        self.train(sql="""
        -- 4. Número de issues por milestone
        SELECT
            m.title AS milestone,
            COUNT(*) AS total_issues
        FROM
            issue i
        JOIN
            milestone m ON i.milestone_id = m.id
        GROUP BY
            m.title
        ORDER BY
            total_issues DESC;
        """)

        self.train(sql="""
        -- 5. Commits feitos por branch
        SELECT
            b.name AS branch,
            COUNT(*) AS total_commits
        FROM
            commits c
        JOIN
            branch b ON c.branch_id = b.id
        GROUP BY
            b.name
        ORDER BY
            total_commits DESC;
        """)
