from typing import Optional, Callable, Awaitable
import time
import requests
from pydantic import BaseModel, Field


class Pipe:

    class Valves(BaseModel):
        """Configurações editáveis no painel do OpenWebUI."""

        api_url: str = Field(
            default="http://host.docker.internal:8000/ask",
            description="Endpoint da API FastAPI que recebe a pergunta (POST).",
        )
        bearer_token: str = Field(
            default="",
            description="Token Bearer opcional para autenticação na API.",
        )
        emit_interval: float = Field(
            default=2.0,
            description="Intervalo, em segundos, entre atualizações de status no UI.",
        )
        enable_status_indicator: bool = Field(
            default=True,
            description="Ativa ou desativa a barra de progresso no chat.",
        )
        max_file_size: int = Field(
            default=1048576,
            description="Tamanho máximo (bytes) para arquivos recebidos — 1 MB por padrão.",
        )

    def __init__(self):
        self.type = "pipe"
        self.id = "fastapi_pipe"
        self.name = "FastAPI Pipe"
        self.valves = self.Valves()
        self.last_emit_time = 0.0  # controle de throttle dos status

    # --------------------------------------------------------------
    # Utilitário para reportar progresso para o OpenWebUI
    # --------------------------------------------------------------
    async def _emit_status(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        level: str,
        message: str,
        done: bool = False,
    ) -> None:
        now = time.time()
        if (
            __event_emitter__
            and self.valves.enable_status_indicator
            and (now - self.last_emit_time >= self.valves.emit_interval or done)
        ):
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "status": "complete" if done else "in_progress",
                        "level": level,
                        "description": message,
                        "done": done,
                    },
                }
            )
            self.last_emit_time = now

    # --------------------------------------------------------------
    # Método principal chamado pelo OpenWebUI
    # --------------------------------------------------------------
    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
        __event_call__: Callable[[dict], Awaitable[dict]] = None,  # não usado
    ) -> Optional[dict]:
        """Envia a última mensagem do usuário à API FastAPI e retorna a resposta."""

        # Recupera a última mensagem do usuário
        await self._emit_status(__event_emitter__, "info", "Processando entrada...", False)

        messages = body.get("messages", [])
        if not messages:
            await self._emit_status(__event_emitter__, "error", "Nenhuma mensagem encontrada", True)
            return {"error": "Nenhuma mensagem encontrada"}

        last_content = messages[-1]["content"]
        # Estrutura de content pode ser: str  | list[ {type: text|file} ]
        question = self._extract_text(last_content)

        # Monta request para API FastAPI
        headers = {"Content-Type": "application/json"}
        if self.valves.bearer_token:
            headers["Authorization"] = f"Bearer {self.valves.bearer_token}"

        payload = {"question": question}

        await self._emit_status(__event_emitter__, "info", "Chamando API FastAPI...", False)

        try:
            response = requests.post(
                self.valves.api_url,
                json=payload,
                headers=headers,
                timeout=120,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            await self._emit_status(__event_emitter__, "error", f"Erro: {exc}", True)
            return {"error": str(exc)}

        # Interpreta resposta da API.
        try:
            data = response.json()
        except ValueError:
            data = {"output": response.text}

        answer = data.get("output") or data

        # Acrescenta a resposta ao histórico e devolve ao WebUI
        body["messages"].append({"role": "assistant", "content": answer})

        await self._emit_status(__event_emitter__, "info", "Resposta entregue", True)
        return answer

    # --------------------------------------------------------------
    # Auxiliar: extrair texto da mensagem (lida com arquivos/objetos)
    # --------------------------------------------------------------
    def _extract_text(self, content) -> str:
        if isinstance(content, str):
            return content.replace("Prompt: ", "", 1).strip()

        # Caso seja uma lista (arquivos + texto)
        text_found = ""
        file_detected = False
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and item.get("text"):
                    text_found = item["text"].strip()
                elif item.get("type") == "file" and not text_found:
                    file_detected = True
                    size = item.get("size", 0)
                    name = item.get("name", "arquivo")
                    if size > self.valves.max_file_size:
                        text_found = f"Recebemos o arquivo {name}, mas ele é muito grande para ser processado."
                    else:
                        text_found = f"Recebemos o arquivo {name}. Ainda não processamos arquivos neste chat."
        return text_found or "Arquivo recebido."
