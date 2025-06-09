"""
Testes para o cliente Vanna
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_psycopg2():
    """Mock para o módulo psycopg2"""
    with patch('src.api.database.MyVanna.psycopg2') as mock_pg:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        mock_cursor.fetchall.side_effect = [
            [('issues',), ('repositories',)],
            [
                ('id', 'integer', 'NO', None),
                ('title', 'text', 'NO', None),
                ('state', 'text', 'NO', None)
            ],
            [('id',)],
            [
                ('name', 'text', 'NO', None),
                ('url', 'text', 'NO', None)
            ],
            [('name',)]
        ]
        
        mock_conn.cursor.return_value = mock_cursor
        mock_pg.connect.return_value = mock_conn
        
        yield mock_pg


@pytest.fixture
def mock_vanna_classes():
    with patch('src.api.database.MyVanna.ChromaDB_VectorStore') as mock_chroma, \
         patch('src.api.database.MyVanna.GoogleGeminiChat') as mock_gemini:
        yield mock_chroma, mock_gemini


class TestVannaClient:
    
    def test_myvanna_init(self, mock_vanna_classes):
        from src.api.database.MyVanna import MyVanna
        
        mock_chroma, mock_gemini = mock_vanna_classes
        
        mock_chroma.return_value = MagicMock()
        mock_gemini.return_value = MagicMock()
        
        config = {
            'api_key': 'test_key',
            'model_name': 'test_model',
            'print_prompt': True,
            'print_sql': True
        }
        vn = MyVanna(config=config)
        
        assert vn.print_prompt is True
        assert vn.print_sql is True
    
    def test_connect_to_postgres(self, mock_psycopg2, mock_vanna_classes):
        from src.api.database.MyVanna import MyVanna
        
        vn = MyVanna()
        vn.connect_to_postgres(
            host='localhost',
            dbname='test_db',
            user='test_user',
            password='test_pass',
            port='5432'
        )
        # Não funcionará, coloquei para receber na classe a var DB_URL do env
        assert vn.db_url == 'postgresql://test_user:test_pass@localhost:5432/test_db'
        assert hasattr(vn, 'schema')

    def test_run_sql_success(self, mock_psycopg2, mock_vanna_classes):
        from src.api.database.MyVanna import MyVanna
        
        mock_chroma, mock_gemini = mock_vanna_classes
        
        with patch('src.api.database.MyVanna.psycopg2') as mock_pg:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            expected_result = [('result1',), ('result2',)]
            mock_cursor.fetchall.return_value = expected_result
            
            mock_conn.cursor.return_value = mock_cursor
            mock_pg.connect.return_value = mock_conn
            
            vn = MyVanna(config={
                'api_key': 'test_key',
                'model_name': 'gemini-1.5-flash-002'
            })
            vn.db_url = 'postgresql://test_user:test_pass@localhost:5432/test_db'
            
            result = vn.run_sql("SELECT * FROM issues;")
            
            assert isinstance(result, list)
            assert result == expected_result
            mock_cursor.execute.assert_called_once_with("SELECT * FROM issues;")

    
    def test_run_sql_error(self, mock_psycopg2, mock_vanna_classes):
        """Testa o tratamento de erro na execução de SQL"""
        from src.api.database.MyVanna import MyVanna
        
        mock_chroma, mock_gemini = mock_vanna_classes
        
        mock_psycopg2.reset_mock()
        
        mock_psycopg2.connect.side_effect = Exception("Erro de conexão")
        
        vn = MyVanna(config={
            'api_key': 'test_key',
            'model_name': 'gemini-1.5-flash-002'
        })
        vn.db_url = 'postgresql://test_user:test_pass@localhost:5432/test_db'
        
        result = vn.run_sql("SELECT * FROM issues;")
        assert isinstance(result, list)
        assert result == []


class TestGetSchema:
    def test_get_schema_success(self, mock_psycopg2):
        from src.api.database.MyVanna import get_schema
        
        schema = get_schema('postgresql://test_user:test_pass@localhost:5432/test_db')
        
        assert "CREATE TABLE issues" in schema
        assert "CREATE TABLE repositories" in schema
        assert "id integer NOT NULL PRIMARY KEY" in schema.replace("    ", "")
    
    def test_get_schema_error(self, mock_psycopg2):
        from src.api.database.MyVanna import get_schema
        
        mock_psycopg2.connect.side_effect = Exception("Erro de conexão")
        
        schema = get_schema('postgresql://test_user:test_pass@localhost:5432/test_db')
        
        assert schema == ""


# Se quiser executar este módulo diretamente
if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
