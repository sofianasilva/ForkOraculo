from typing import Optional, Callable, Awaitable
from pydantic import BaseModel, Field
import time
import requests


class Pipe:
    class Valves(BaseModel):
        """
        Classe interna que define as configurações (válvulas) do pipe.
        Utiliza Pydantic para validação dos campos.
        """

        webhook_url: str = Field(
            default="http://host.docker.internal:5678/webhook-test/34323dd2-6d14-492b-a889-aebcd6d72810",
            description="URL do Webhook para onde as mensagens serão enviadas.",
        )
        webhook_bearer_token: str = Field(
            default="",
            description="Token de autenticação do tipo Bearer para o Webhook.",
        )
        input_field: str = Field(
            default="chatInput", description="Campo de entrada enviado para o Webhook."
        )
        response_field: str = Field(
            default="output", description="Campo da resposta esperada do Webhook."
        )
        emit_interval: float = Field(
            default=2.0,
            description="Intervalo em segundos entre atualizações de status.",
        )
        enable_status_indicator: bool = Field(
            default=True, description="Ativa ou desativa os indicadores de status."
        )
        max_file_size: int = Field(
            default=1048576, description="Tamanho máximo do arquivo (1MB por padrão)."
        )

    def __init__(self):
        """
        Inicializa a instância do Pipe com identificadores e configurações padrão.
        """
        self.type = "pipe"
        self.id = "webhook_pipe"
        self.name = "Webhook Pipe"
        self.valves = self.Valves()
        self.last_emit_time = (
            0  # Usado para controlar o intervalo entre atualizações de status
        )

    async def emit_status(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        level: str,
        message: str,
        done: bool,
    ):
        """
        Emite um status para o WebUI (caso o emissor esteja ativo e o tempo de intervalo tenha passado).
        """
        current_time = time.time()
        if (
            __event_emitter__
            and self.valves.enable_status_indicator
            and (
                current_time - self.last_emit_time >= self.valves.emit_interval or done
            )
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
            self.last_emit_time = current_time

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
        __event_call__: Callable[[dict], Awaitable[dict]] = None,
    ) -> Optional[dict]:
        """
        Processa a entrada do usuário, envia para um Webhook e retorna a resposta.

        Args:
            body (dict): Conteúdo da mensagem (incluindo histórico de mensagens).
            __user__ (dict, opcional): Dados do usuário, usado para ID de sessão.
            __event_emitter__ (Callable, opcional): Função para emitir status no UI.
            __event_call__ (Callable, opcional): Não usado neste pipe.

        Returns:
            dict | None: Resposta recebida do Webhook ou erro.
        """
        await self.emit_status(__event_emitter__, "info", "Chamando Webhook...", False)

        messages = body.get("messages", [])
        if messages:
            question_content = messages[-1]["content"]

            # Verifica se o conteúdo é texto puro ou lista com arquivos
            if not isinstance(question_content, str):
                text_found = ""
                file_detected = False

                # Processa itens da mensagem: texto ou arquivos
                for item in question_content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_found = item.get("text", "").strip()
                        elif item.get("type") == "file" and not text_found:
                            file_detected = True
                            file_size = item.get("size", 0)
                            file_name = item.get("name", "arquivo")
                            if file_size > self.valves.max_file_size:
                                text_found = f"Recebemos o arquivo {file_name}, mas ele é muito grande para ser processado neste momento."
                            else:
                                text_found = f"Recebemos o arquivo {file_name}."

                # Define o texto final da pergunta
                if text_found:
                    question = text_found
                else:
                    question = "Arquivo recebido. Ainda não suportamos esse tipo de arquivo aqui."
            else:
                # Extrai o texto limpo, se estiver dentro de 'Prompt:'
                if "Prompt: " in question_content:
                    question = question_content.split("Prompt: ")[-1]
                else:
                    question = question_content

            try:
                # Cabeçalhos da requisição
                headers = {
                    "Authorization": f"Bearer {self.valves.webhook_bearer_token}",
                    "Content-Type": "application/json",
                }

                # Corpo da requisição
                payload = {
                    self.valves.input_field: question,
                }

                # Se disponível, adiciona o ID da sessão
                if __user__ and "id" in __user__:
                    payload["sessionId"] = __user__["id"]

                # Envia a requisição para o Webhook
                response = requests.post(
                    self.valves.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=900,
                )

                # Verifica a resposta do Webhook
                if response.status_code == 200:
                    if response.content and response.headers.get(
                        "Content-Type", ""
                    ).startswith("application/json"):
                        response_json = response.json()
                        if self.valves.response_field in response_json:
                            webhook_response = response_json[self.valves.response_field]
                        else:
                            raise KeyError(
                                f"Campo '{self.valves.response_field}' não encontrado na resposta do webhook"
                            )
                    else:
                        webhook_response = "Recebemos sua mensagem/arquivo."
                else:
                    raise Exception(f"Erro: {response.status_code} - {response.text}")

                # Adiciona a resposta do Webhook como nova mensagem
                body["messages"].append(
                    {"role": "assistant", "content": webhook_response}
                )
                await self.emit_status(
                    __event_emitter__, "info", "Resposta do webhook processada", False
                )
            except requests.Timeout:
                await self.emit_status(
                    __event_emitter__,
                    "error",
                    "Erro: timeout ao chamar o webhook",
                    True,
                )
                return {"error": "Timeout ao chamar o webhook"}
            except KeyError as e:
                await self.emit_status(
                    __event_emitter__,
                    "error",
                    f"Erro na resposta do webhook: {str(e)}",
                    True,
                )
                return {"error": str(e)}
            except Exception as e:
                await self.emit_status(
                    __event_emitter__,
                    "error",
                    f"Erro ao chamar webhook: {str(e)}",
                    True,
                )
                return {"error": str(e)}
        else:
            # Nenhuma mensagem encontrada
            await self.emit_status(
                __event_emitter__, "error", "Nenhuma mensagem encontrada.", True
            )
            body["messages"].append(
                {"role": "assistant", "content": "Nenhuma mensagem encontrada."}
            )

        await self.emit_status(__event_emitter__, "info", "Processo Finalizando", True)
        return webhook_response
