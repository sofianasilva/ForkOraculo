"""
Testes para o Pipe do OpenWebUI
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import requests 


@pytest.fixture
def pipe():
    """Fixture que retorna uma instância do Pipe para testes"""
    from src.assets.open_web_ui.pipeline_api import Pipe
    return Pipe()


@pytest.fixture
def mock_requests():
    
    with patch('src.assets.open_web_ui.pipeline_api.requests') as mock_req:
        mock_req.RequestException = requests.RequestException
        mock_response = MagicMock()
        mock_response.json.return_value = {"output": "Resposta de teste"}
        mock_response.text = "Resposta de teste em texto"
        mock_response.raise_for_status.return_value = None
        
        mock_req.post.return_value = mock_response
        yield mock_req


class TestPipeClass:
    
    def test_pipe_init_default_values(self, pipe):
        assert pipe.type == "pipe"
        assert pipe.id == "fastapi_pipe"
        assert pipe.name == "FastAPI Pipe"
        assert pipe.valves.api_url == "http://back-end:8000/ask"
        assert pipe.valves.bearer_token == ""
        assert pipe.valves.emit_interval == 2.0
        assert pipe.valves.enable_status_indicator is True
        assert pipe.valves.max_file_size == 1048576  # 1MB
    
    def test_extract_text_simple_string(self, pipe):
        content = "Como estão as issues?"
        result = pipe._extract_text(content)
        assert result == "Como estão as issues?"
    
    def test_extract_text_prompt_prefix(self, pipe):
        content = "Prompt: Como estão as issues?"
        result = pipe._extract_text(content)
        assert result == "Como estão as issues?"
    
    def test_extract_text_complex_content(self, pipe):
        content = [
            {"type": "text", "text": "Como estão as issues?"},
            {"type": "file", "name": "report.csv", "size": 1000}
        ]
        result = pipe._extract_text(content)
        assert result == "Como estão as issues?"
    
    def test_extract_text_file_only(self, pipe):
        content = [
            {"type": "file", "name": "report.csv", "size": 1000}
        ]
        result = pipe._extract_text(content)
        assert "Recebemos o arquivo report.csv" in result
    
    def test_extract_text_large_file(self, pipe):
        large_size = pipe.valves.max_file_size + 1000
        content = [
            {"type": "file", "name": "large.pdf", "size": large_size}
        ]
        result = pipe._extract_text(content)
        assert "muito grande para ser processado" in result


@pytest.mark.asyncio
class TestPipeMethods:
    
    async def test_emit_status(self, pipe):
        mock_emitter = AsyncMock()
        
        await pipe._emit_status(mock_emitter, "info", "Processando...", False)
        
        mock_emitter.assert_called_once()
        call_arg = mock_emitter.call_args[0][0]
        assert call_arg["type"] == "status"
        assert call_arg["data"]["status"] == "in_progress"
        assert call_arg["data"]["level"] == "info"
        assert call_arg["data"]["description"] == "Processando..."
        assert call_arg["data"]["done"] is False
    
    async def test_emit_status_done(self, pipe):
        mock_emitter = AsyncMock()
        
        await pipe._emit_status(mock_emitter, "info", "Concluído!", True)
        
        call_arg = mock_emitter.call_args[0][0]
        assert call_arg["data"]["status"] == "complete"
        assert call_arg["data"]["done"] is True
    
    async def test_emit_status_throttling(self, pipe):
        mock_emitter = AsyncMock()
        pipe.last_emit_time = float('inf')
        
        await pipe._emit_status(mock_emitter, "info", "Processando...", False)
        
        mock_emitter.assert_not_called()
    
    async def test_pipe_method_success(self, pipe, mock_requests):
        mock_emitter = AsyncMock()
        
        body = {
            "messages": [
                {"role": "user", "content": "Quantas issues estão abertas?"}
            ]
        }
        
        result = await pipe.pipe(body, None, mock_emitter, None)
        
        mock_requests.post.assert_called_once_with(
            pipe.valves.api_url,
            json={"question": "Quantas issues estão abertas?"},
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        expected_output = "Resposta de teste"
        expected_dict = {"output": "Resposta de teste"}
        assert result == expected_output or result == expected_dict
        
        assert mock_emitter.call_count >= 2 
    
    async def test_pipe_method_with_auth(self, pipe, mock_requests):
        mock_emitter = AsyncMock()
        pipe.valves.bearer_token = "test_token"
        
        body = {
            "messages": [
                {"role": "user", "content": "Quantas issues estão abertas?"}
            ]
        }
        
        await pipe.pipe(body, None, mock_emitter, None)
        
        headers = mock_requests.post.call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test_token"
    
    async def test_pipe_method_request_error(self, pipe, mock_requests):
        mock_emitter = AsyncMock()
        
        mock_requests.post.side_effect = requests.RequestException("Erro de conexão")
        
        body = {
            "messages": [
                {"role": "user", "content": "Pergunta com erro de requisição"}
            ]
        }
        
        result = await pipe.pipe(body, None, mock_emitter, None)
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "Erro de conexão" in str(result["error"])
        
        error_calls = [
            call for call in mock_emitter.call_args_list 
            if call[0][0].get('data', {}).get('level') == 'error'
        ]
        assert len(error_calls) >= 1


