# 📌Users API — FastAPI

API RESTful desenvolvida em **Python com FastAPI**, responsável pelo gerenciamento de usuários, contas, cartões e comunicações personalizadas **(news)**.

Este projeto atua como uma **camada de dados acessível via HTTP**, funcionando como **fonte central de informações** para aplicações externas e pipelines de dados.

## 🎯Objetivo do Projeto

Demonstrar a construção de uma **API REST profissional**, reutilizável e em produção, preparada para integração com outros sistemas (ex.: pipelines ETL e automações).

## 🚀Funcionalidades

- CRUD completo de usuários;
- Modelagem de domínio com validação automática (Pydantic);
- Documentação interativa via Swagger (OpenAPI);
- Geração automática de IDs;
- API pronta para integração com pipelines de dados;
- Deploy em nuvem com URL pública;

## 🧱Modelagem de Domínio

Cada usuário possui:

- Conta bancária;
- Cartão;
- Lista de recursos;
- Lista de comunicações (news);

A entidade Usuário é identificada unicamente por um **ID**, utilizado como chave primária para integrações externas.

## 🔌Enpoints Principais

| Método | Endpoint       | Descrição                        |
| ------ | -------------- | -------------------------------- |
| GET    | `\usuario`     | Listar todos os usuários         |
| GET    | `\usuario{id}` | Retorna todos os usuários por ID |
| POST   | `\usuario`     | Cria um novo usuário             |
| PUT    | `\usuario{id}` | Atualiza o usuário completo      |

## 📃Documentação (Swagger)

A documentação interativa pode ser acessada em:

- 🔗 [https://usersapipython.up.railway.app/docs](https://usersapipython.up.railway.app/docs)

## ☁️Deploy em Produção

A API está publicada em ambiente de produção utilizando **Railway**, com porta dinâmica e roteamento automático.

## 🛠️Técnologias utilizadas

• Python
• FastAPI
• Pydantic
• Uvicorn
• OpenAPI/Swagger
• Railway (Deploy)

## 🔄Integração com outros projetos

Esta API foi construida para ser consumida por **pipelines ETL**, onde:

- IDs de usuários são lidos de arquivos CSV;
- Dados são extraídos via HTTP;
- Informações são enriquecidas externamente;
- Atualizações são persistidas via API(`PUT`);

👉 O pipeline **ETL + IA** que consome esta API está disponível em um **repositório separado**.

## ▶️ Execução Local

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Acesse:

```
http://127.0.0.1:8000/docs
```

## 🏛️Arquitetura

### Visão Geral

flowchart LR
subgraph Clients["Clientes / Consumidores"]
Swagger["Swagger UI (/docs)"]
ExtClient["Aplicações externas\n(cURL / Postman / Scripts)"]
ETL["Pipeline ETL (projeto separado)\nCSV + IA"]
end

subgraph Cloud["Railway (Produção)"]
Router["Railway Router / Proxy\nHTTPS → $PORT"]
API["FastAPI Users API\n(main.py)"]
MemDB["In-memory Store\n(database_fake)\n(para MVP/estudo)"]
end

Swagger -->|HTTP GET/POST/PUT| Router
ExtClient -->|HTTP GET/POST/PUT| Router
ETL -->|GET /usuario/id\nPUT /usuario/id| Router

Router --> API
API --> MemDB
MemDB --> API

#### Leitura rápida do diagrama:

    • O Railway recebe HTTPS, encaminha para a porta dinâmica ($PORT) e entrega na FastAPI.
    • Swagger, Postman/cURL e o futuro ETL consomem os endpoints.
    • A persistência, por enquanto, é um “banco” em memória (database_fake) — suficiente para o desafio e para o ETL.

### Fluxo de Requisições:

sequenceDiagram
participant C as Cliente (Swagger/Postman/ETL)
participant R as Railway Router
participant A as FastAPI Users API
participant D as database_fake (memória)

C->>R: HTTP Request (ex: GET /usuario/4)
R->>A: Forward request to $PORT
A->>D: Buscar usuário por ID
D-->>A: Dados do usuário
A-->>R: 200 OK + JSON
R-->>C: 200 OK + JSON

C->>R: PUT /usuario/4 (usuário atualizado com nova news)
R->>A: Forward request to $PORT
A->>D: Persistir usuário atualizado
D-->>A: OK
A-->>R: 200 OK + JSON atualizado
R-->>C: 200 OK + JSON atualizado

## ⭐Diferenciais Técnicos

    • Separação clara de responsabilidades (API x ETL)
    • API pensada para reuso e integração
    • Deploy real em produção
    • Documentação automática
    • Arquitetura alinhada a cenários corporativos
