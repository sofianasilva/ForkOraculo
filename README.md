# Oráculo
Este projeto almeja desenvolver uma plataforma de chatbot para agilizar e simplificar respostas de perguntas sobre o estado das tarefas de uma equipe de desenvolvimento.

Para este fim, planejamos integrar ferramentas como repositório do Github, JIRA... e utilizando uma IA para fazer queries SQL e retornar a resposta certa.


## Sobre o projeto
Um chatbot que utiliza a IA para pesquisar em um banco com  dados, de ferramentas integradas (Github, JIRA, ...), afim de agilizar uma resposta à uma pergunta do tipo: O que **membro da equipe de desenvolvimento** está trabalhando agora?

Criado para simplificar o processo de gerenciamento de uma equipe.

## Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes requisitos instalados:
- [Docker](https://www.docker.com/)
  - Utilizado para subir o banco de dados Postgres, na versão 15.
- [Python 3.10](https://www.python.org/)
  - Utilizar a lib Airbyte para buscar dados do Github

## Instalação
Siga estas etapas para configurar o projeto localmente:

1. Gere um token pessoal no [Github](https://github.com) e insira com a chave **GITHUB_TOKEN** no arquivo .env

    - Pode ser gerado [**aqui**](https://github.com/settings/tokens)


2. Utilize os comandos a seguir para iniciar e parar contêiner com o banco de dados

    Para iniciar o contêiner:
    ```bash
      docker compose up -d
    ```

    Para parar o contêiner:
    ```bash
      docker compose down -d
    ```

3. Inicie um ambiente virtual e ative-o

    Iniciando um ambiente virtual:
    ```bash
      python -m venv .venv
    ```

    Ativando o ambiente virtual, no Linux e MacOS:
    ```bash
      source .venv/bin/activate
    ```

    No Windows Powershell:
    ```bash
      .venv\Scripts\Activate.ps1
    ```

    Desativando o ambiente virtual:
    ```bash
      deactivate
    ```

4. Instale os requerimentos do projeto com o comando:
    ```bash
      pip install -r py_requirements.txt
    ```

5. Após sucesso na instalação dos requerimentos, rode o arquivo python principal:
    ```bash
      python main.py
    ```

    Ou inicie a aplicação FastAPI com:
    ```bash
    uvicorn src.app:app --reload
    ```

## Uso da API

Uma vez que a aplicação esteja em execução, você pode enviar uma requisição POST para o endpoint `/ask` com um corpo JSON contendo sua pergunta. Por exemplo:

```json
{
  "question": "Me liste os produtos e suas quantidades em estoque"
}
```

A aplicação retornará o resultado da consulta SQL gerada com base na sua pergunta.

## Estrutura de diretórios

```
Oraculo/
├── src/
│   ├── etl/
│   │   └── airbyte.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── vanna_client.py    
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          
│   ├── models/
│   │   ├── __init__.py
│   │   └── query.py           
│   └── config.py              
├── app.py                     
├── main.py                    
├── py_requirements.txt        
├── docker-compose.yml
├── .env                       
├── .env.example               
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
└── README.md
```