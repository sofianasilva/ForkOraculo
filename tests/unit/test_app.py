import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_vanna():
    """Mock para a classe MyVanna"""
    with patch('src.api.controller.AskController.MyVanna') as MockVanna:
        mock_vn = MagicMock()
        mock_vn.generate_sql.return_value = "SELECT * FROM issues LIMIT 10;"
        mock_vn.run_sql.return_value = [("issue1", "open"), ("issue2", "closed")]
        mock_vn.train.return_value = None
        MockVanna.return_value = mock_vn
        yield mock_vn

@pytest.fixture
def mock_genai():
    """Mock para o Google Generative AI"""
    with patch('src.api.controller.AskController.genai') as mock_genai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.parsed = [MagicMock(texto="Resposta processada")]
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.CLient.return_value = mock_client
        yield mock_genai

@pytest.fixture
def client():
    """Client(Gemini) de teste para a aplicação FastAPI"""
    from src.api.app import app
    return TestClient(app)


class TestFastAPI:
    
    def test_ask_endpoint_success(self, client, mock_vanna, mock_genai):

        response = client.post(
            "/ask",
            json={"question": "Quais são as issues abertas?"}
        )
        
        assert response.status_code == 200
        assert "output" in response.json()
        
        mock_vanna.generate_sql.assert_called_once_with("Quais são as issues abertas?")
        mock_vanna.run_sql.assert_called_once()
    
    def test_ask_endpoint_error(self, client, mock_vanna, mock_genai):

        mock_vanna.generate_sql.side_effect = Exception("Erro de teste")
        
        response = client.post(
            "/ask",
            json={"question": "Pergunta com erro"}
        )
        
        assert response.status_code == 500
        assert "detail" in response.json()
