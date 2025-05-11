from vanna.vannadb import VannaDB_VectorStore
from vanna.google import GoogleGeminiChat
from vanna.chromadb import ChromaDB_VectorStore
import psycopg2
import os

class MyVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        ChromaDB_VectorStore.__init__(self, config=config)
        
        api_key = config.get('api_key')
        model_name = config.get('model_name')
        
        GoogleGeminiChat.__init__(self, config={
            'api_key': api_key, 
            'model_name': model_name
        })
        
        self.print_prompt = config.get('print_prompt', False)
        self.print_sql = config.get('print_sql', False)

    def connect_to_postgres(self, host, dbname, user, password, port):
        self.db_url = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
        self.schema = get_schema(self.db_url)

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

def get_schema(db_url):
    try:
        conn = psycopg2.connect(db_url)
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