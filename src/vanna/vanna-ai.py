from vanna.google import GoogleGeminiChat
from vanna.chromadb import ChromaDB_VectorStore
import psycopg2

def get_schema(db_url):
    """
    Obtém o esquema do banco de dados PostgreSQL para treinamento
    """
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


class MyVanna(ChromaDB_VectorStore, GoogleGeminiChat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        GoogleGeminiChat.__init__(self, config={'api_key': "AIzaSyD9g5yT45LLaHgKR5ixc8Z1rpQPborvMcw", 'model_name': "gemini-2.0-flash"})


def main():
    vn = MyVanna()
    db_url = 'postgresql://postgres:postgres@localhost:5432/databasex'
    vn.connect_to_postgres(host='localhost', dbname='databasex', user='postgres', password='postgres', port='5432')
    schema = get_schema(db_url)

    vn.train(ddl=schema)
    vn.train(documentation="""A  tabela commits armazena informações sobre os commits realizados em repositórios, incluindo o nome do repositório, o branch, a data de criação, o hash SHA do commit, URLs associadas e diversos campos em formato JSON que detalham o conteúdo do commit, os autores, os responsáveis pela aplicação e os pais do commit. Os campos iniciados por _airbyte_ são metadados técnicos usados para controle de extração e versionamento dos dados.
    A tabela issue_milestones representa os marcos definidos nos repositórios para organizar o progresso das issues. Ela contém informações como o repositório, título e descrição do marco, estado (aberto ou fechado), contagens de issues abertas e fechadas, e datas relevantes como criação, atualização, encerramento e prazo.
    A tabela issues registra as issues criadas nos repositórios, com detalhes como título, estado, descrição, usuário autor, labels, responsáveis atribuídos, associação com pull requests e marcos, número de comentários, e datas de criação, atualização e encerramento. Há também campos JSON que armazenam dados estruturados como informações de usuários e reações.
    A tabela projects_v2 reúne dados sobre projetos do tipo GitHub Projects versão 2, contendo informações como título, descrição curta, status de visibilidade, se é um template, se está fechado, URLs associadas e o repositório ao qual pertence. Campos booleanos indicam permissões de visualização e edição por parte do usuário.
    A tabela pull_requests registra os pull requests enviados nos repositórios, contendo o título, corpo, estado, data de criação, encerramento e merge, bem como URLs e status relacionados. Também inclui vários campos em formato JSON detalhando o usuário que criou o PR, revisores solicitados, branches de origem e destino, e links para outros recursos.
    A tabela repositories contém os dados gerais dos repositórios. Inclui identificadores como nome, descrição, URLs da API, estatísticas como número de estrelas, forks, issues abertas, permissões, visibilidade, e informações sobre recursos habilitados (wiki, issues, downloads, páginas, entre outros). Também são armazenadas datas de criação, atualização e último push, além de dados sobre a licença e tópicos associados.
    A tabela team_members lista os membros de equipes dentro de uma organização, com informações como login, ID, URLs de perfil e eventos, tipo de conta, se é administrador do site, e a organização e equipe às quais pertencem.
    A tabela team_memberships relaciona usuários a equipes específicas, com campos que indicam o estado da associação, o papel do membro, a organização, o slug da equipe e o nome de usuário correspondente.
    A tabela teams armazena dados sobre equipes em uma organização, incluindo nome, slug, descrição, privacidade, configuração de notificações, permissões de acesso, URLs relacionadas e dados sobre a equipe-pai quando aplicável.
    Por fim, a tabela users contém informações sobre os usuários do GitHub, com dados como login, ID, tipo de conta, URLs de perfil e atividades, organização associada, e se o usuário é um administrador. Também contém informações extraídas via API, como avatares e dados de eventos.
    Cada uma dessas tabelas utiliza índices nos campos de extração do Airbyte e em campos principais como IDs ou SHAs, permitindo buscas eficientes e controle sobre a origem e atualização dos dados.""")

    vn.train(sql="""
    SELECT
        i.repository,
        COUNT(*) AS total_issues_abertas,
        MAX(i.created_at) AS data_ultima_issue
    FROM
        public.issues i
    WHERE
        i.state = 'open'
    GROUP BY
        i.repository
    ORDER BY
        total_issues_abertas DESC
    LIMIT 10;
    """)

    pergunta = ""
    sql_gerado = vn.generate_sql(pergunta)
        
    print("\nPergunta:", pergunta)
    #print("SQL gerado:", sql_gerado)

    resultado = vn.run_sql(sql_gerado)
    print("\nResultado:")
    print(resultado)


main()