"""
Fixtures e configurações gerais para testes do projeto Oráculo.
"""
import os
import sys
import pytest
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

@pytest.fixture
def mock_env_vars():
    original_environ = dict(os.environ)
    os.environ.update({
        'API_KEY': 'test_api_key',
        'MODEL_NAME': 'test-model',
        'GITHUB_TOKEN': 'test_github_token',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    })
    yield
    os.environ.clear()
    os.environ.update(original_environ)

@pytest.fixture
def sample_database_schema():
    """Retorna um exemplo de schema de banco de dados para testes"""
    return """
    CREATE TABLE issues (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        state TEXT NOT NULL,
        repository TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP
    );
    
    CREATE TABLE repositories (
        name TEXT PRIMARY KEY,
        description TEXT,
        url TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL
    );
    """
