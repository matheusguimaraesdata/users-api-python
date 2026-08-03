# 📌 Users API — FastAPI + SQLModel + Pandas

API RESTful desenvolvida em **Python com FastAPI**, responsável pelo gerenciamento de usuários, contas, cartões e comunicações personalizadas **(news)**, com persistência real em banco relacional e endpoints de **analytics** para consumo por pipelines de ETL e ferramentas de BI.

Este projeto atua como uma **camada de dados acessível via HTTP**, funcionando como **fonte central de informações** para aplicações externas e pipelines de dados.

## 🎯 Objetivo do Projeto

Demonstrar a construção de uma **API REST profissional**, com modelagem relacional, persistência real, e uma camada de análise de dados (Pandas) sobre a própria base — unindo desenvolvimento backend e análise de dados no mesmo projeto.

## 🚀 Funcionalidades

- CRUD completo de usuários (**GET, POST, PUT, PATCH, DELETE**);
- Paginação e filtro por nome na listagem;
- Modelagem relacional real (chaves estrangeiras, relacionamentos 1:1 e 1:N) via SQLModel;
- Persistência em banco (SQLite local / Postgres em produção via `DATABASE_URL`);
- Endpoints de **analytics** com Pandas (estatísticas agregadas da base);
- Exportação de dados em **CSV** para consumo em BI/Excel;
- Documentação interativa via Swagger (OpenAPI);
- Deploy em nuvem com URL pública.

## 🧱 Modelagem de Domínio

```
Usuario 1───1 Conta
Usuario 1───1 Cartao
Usuario 1───N Recurso
Usuario 1───N News
```

Cada entidade é uma tabela própria, relacionada por chave estrangeira — não mais um objeto único com listas aninhadas em memória.

## 🔌 Endpoints Principais

| Método | Endpoint                    | Descrição                                   |
| ------ | ---------------------------- | -------------------------------------------- |
| GET    | `/usuario`                   | Lista usuários (paginação + filtro por nome) |
| GET    | `/usuario/{id}`              | Retorna um usuário por ID                    |
| POST   | `/usuario`                   | Cria um novo usuário                         |
| PUT    | `/usuario/{id}`               | Atualiza o usuário completo                  |
| PATCH  | `/usuario/{id}`               | Atualiza campos específicos do usuário       |
| DELETE | `/usuario/{id}`               | Remove um usuário                            |
| GET    | `/relatorios/estatisticas`    | Estatísticas agregadas da base (Pandas)      |
| GET    | `/relatorios/usuarios.csv`    | Exporta a base em CSV                        |

## 📃 Documentação (Swagger)

- 🔗 [https://usersapipython.up.railway.app/docs](https://usersapipython.up.railway.app/docs)

## ☁️ Deploy em Produção

Publicado no **Railway**. Em produção, defina a variável de ambiente `DATABASE_URL` apontando para um Postgres gerenciado (o projeto usa SQLite localmente por padrão, sem exigir configuração extra).

## 🛠️ Tecnologias Utilizadas

- Python
- FastAPI
- SQLModel (Pydantic + SQLAlchemy)
- Pandas
- Uvicorn
- OpenAPI/Swagger
- Railway (Deploy)

## 🔄 Integração com Outros Projetos

Esta API foi construída para ser consumida por **pipelines ETL**, onde:

- Dados são extraídos via HTTP (`GET /usuario`, `GET /relatorios/usuarios.csv`);
- Informações são enriquecidas externamente (ex.: geração de texto via LLM);
- Atualizações são persistidas via API (`PUT`/`PATCH`);

👉 O pipeline **ETL + IA** que consome esta API está disponível em um **repositório separado**.

## ▶️ Execução Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse:

```
http://127.0.0.1:8000/docs
```

Na primeira execução, o banco (`database.db`) é criado automaticamente e populado com 3 usuários de exemplo.

### 🌱 Popular com massa de dados (100 usuários sintéticos)

Para testar paginação, filtros e os endpoints de analytics com volume real, é possível gerar 100 usuários sintéticos (dados brasileiros realistas via Faker):

```bash
pip install -r requirements-dev.txt
python -m scripts.seed_100
```

O script é aditivo — pode ser executado mais de uma vez para acumular mais registros — e não remove os dados já existentes.

## ✅ Testes Automatizados

A suíte usa `pytest` com banco SQLite em memória isolado por teste (não toca no `database.db` real):

```bash
pip install -r requirements-dev.txt
pytest -v
```

Cobertura atual: 15 testes, cobrindo CRUD completo (incluindo casos de 404), paginação, filtro por nome e os endpoints de analytics/CSV.

## 🐳 Docker

```bash
docker build -t users-api .
docker run -p 8000:8000 users-api
```

Acesse `http://localhost:8000/docs`. Em produção, a variável `PORT` é injetada automaticamente pela plataforma de deploy (Railway, Render etc.).

## 🏛️ Arquitetura

```
app/
├── main.py            # instancia o FastAPI, inclui routers, cria/popula o banco no startup
├── core/
│   └── config.py       # configurações via variável de ambiente
├── db/
│   ├── database.py     # engine e sessão do banco
│   └── seed.py         # dados de exemplo (idempotente)
├── models/
│   └── usuario.py      # tabelas SQLModel + schemas de entrada/saída
└── routers/
    ├── usuario.py       # CRUD de usuários
    └── relatorios.py    # analytics (Pandas) e export CSV
```

### Visão Geral
![Arquitetura da API](docs/diagramas/Arquitetura%20-%20Visão%20Geral.svg)

### Fluxo de Requisições
![Fluxo de Requisições](docs/diagramas/Fluxo%20de%20Requisições.svg)

> Os diagramas acima refletem a versão anterior (banco em memória) e serão atualizados para representar a camada de persistência e o router de relatórios.

## ⭐ Diferenciais Técnicos

- Modelagem relacional real, não objetos aninhados em memória
- Persistência que sobrevive a redeploy
- CRUD genuinamente completo (inclui PATCH e DELETE)
- Camada de analytics com Pandas sobre os próprios dados da API
- Separação clara em camadas (routers / models / db / core)
- Suíte de testes automatizados (pytest) com banco isolado por teste
- Containerizado com Docker, pronto para qualquer plataforma de deploy
- Geração de massa de dados sintética para testes e demonstração
- Testado ponta a ponta antes do deploy
