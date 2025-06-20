# Oráculo
Este projeto almeja desenvolver uma plataforma de chatbot para agilizar e simplificar respostas de perguntas sobre o estado das tarefas de uma equipe de desenvolvimento.

Para este fim, planejamos integrar ferramentas como repositório do Github, JIRA... e utilizando uma IA para fazer queries SQL e retornar a resposta certa.


## Sobre o projeto
Um chatbot que utiliza a IA para pesquisar em um banco com  dados, de ferramentas integradas (Github, JIRA, ...), afim de agilizar uma resposta à uma pergunta do tipo: O que **membro da equipe de desenvolvimento** está trabalhando agora?

Criado para simplificar o processo de gerenciamento de uma equipe.

## Pré-requisitos

Antes de começar, certifique-se de que você tem os seguintes requisitos instalados:
- [Docker](https://www.docker.com/)
  - Utilizado para disponibilizar serviços como: o banco de dados Postgres:15 e a interface de usuário, Open-web UI.
- [Python 3.10.17](https://www.python.org/)
  - Utilizar a lib Airbyte para buscar dados do Github

## Instalação
Siga estas etapas para configurar o projeto localmente:

1. Gere um token pessoal no [Github](https://github.com) e insira a chave na variável **GITHUB_TOKEN** no arquivo `example.env`

    - Pode ser gerado [**neste link**](https://github.com/settings/tokens)

2. Gere um token pessoal do [Gemini](https://aistudio.google.com/) e insira na variável **GEMINI_API_KEY** no arquivo `example.env`

    - Pode ser gerado [**neste link**](https://aistudio.google.com/app/apikey)

3. Renomeie o arquivo `example.env` para somente `.env`

4. Utilize os comandos a seguir para iniciar os serviços:

    Para iniciar o contêiner:
    ```bash
      docker compose up -d
    ```
5. Utilize os comandos a seguir para parar os contêineres:

    Para parar o contêiner:
    ```bash
      docker compose down
    ```

## Uso da API

Para abrir a ferramenta, acesse:

- **Fast API**: [http://localhost:8000](http://localhost:8000)

Uma vez que a aplicação esteja em execução, você pode enviar uma requisição POST para o endpoint `/ask` com um corpo JSON contendo sua pergunta. Por exemplo:

```json
{
  "question": "Me liste os produtos e suas quantidades em estoque"
}
```

A aplicação retornará o resultado da consulta SQL gerada com base na sua pergunta.

## Uso do OpenWebUI

Para abrir a ferramenta, acesse:

- **OpenWebUI**: [http://localhost:3000](http://localhost:3000)

### OpenWebUI

Adicione a pipeline como uma nova função, importando o arquivo `src/assets/open_web_ui/pipeline_api.json` no painel admin do OpenWebUI. 

A pipeline ja está configurada para direcionar as perguntas para a api no backend.

## Arquitetura e Modularização

O projeto é dividido em módulos bem definidos que seguem uma arquitetura desacoplada, com responsabilidades específicas. Abaixo, explicamos de forma clara o papel de cada componente:

### Componentes Principais

- **🔁 Airbyte (ETL)**  
  Responsável por extrair dados de fontes externas como o GitHub. Ele coleta essas informações e envia para o banco de dados.
  Local: `src/etl/`

- **⚙️ Backend (FastAPI)**  
  API desenvolvida em FastAPI, responsável por receber as perguntas, processá-las com ajuda da IA (Vanna.AI), gerar a consulta SQL e retornar a resposta ao usuário.  
  Local: `src/api/`

- **🧠 Vanna.AI (LLM)**  
  Modelo de linguagem usado para interpretar perguntas em linguagem natural e gerar a SQL correspondente.  
  Local: `src/api/database/`

- **🌐 OpenWebUI (Interface)**  
  Interface Web usada para interagir com o usuário final. Permite enviar perguntas e visualizar respostas.  
  Local: `src/assets/open_web_ui/`

---

### Visão Geral do Fluxo de Dados

```
Usuário (interface OpenWebUI)
         ↓
      Webhook
         ↓
  FastAPI (backend/API)
         ↓
     Vanna.AI (LLM)
         ↓
    SQL → Banco de dados
         ↓
   ↪ Resposta exibida ao usuário
```

---

### Resumo da Arquitetura por Papel

| Componente     | Papel              | Descrição                                                                 |
|----------------|--------------------|---------------------------------------------------------------------------|
| OpenWebUI      | Interface           | Frontend para o usuário interagir com o sistema, envia a pergunta diretamente para a api web                          |
| FastAPI        | Backend/API         | Processa as perguntas e coordena as respostas                            |
| Airbyte        | ETL                 | Coleta dados externos do Github e injeta no banco de dados                         |
| Vanna.AI       | LLM / IA            | Converte perguntas em SQL com base na linguagem natural                  |
| Postgres/Chromadb | Banco de Dados      | Armazena dados coletados e usados pela IA                                |


## Estrutura de diretórios

```
Oraculo/
├── .github/
├── .docker/
│   ├── back-end/
│   │   └── Dockerfile
│   ├── db/
│   │   ├── Dockerfile
│   │   └── oraculo_20-06-25.sql
│   └── front-end/
│       └── Dockerfile
├── src/
│   ├── api/
│   │   ├── controller/
│   │   │   ├── __init__.py
│   │   │   └── AskController.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── MyVanna.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── query.py
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── config.py
│   ├── assets/
│   │   ├── aux/
│   │   │   ├── __init__.py
│   │   │   ├── env.py
│   │   │   └── flags.py
│   │   ├── open_web_ui/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline_api.py
│   │   │   └── pipeline_api.json
│   │   └── pattern/
│   │       ├── __init__.py
│   │       └── singleton.py
│   └── etl/
│       ├── __init__.py
│       └── airbyte.py
├── tests/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_app.py
│   │   ├── test_pipeline_api.py
│   │   └── test_vanna_client.py
│   ├── __init__.py
│   ├── conftest.py
│   └── README.md
├── .env
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── README.md
├── docker-compose.yml
├── example.env
├── main.py
└── requirements.txt 
```