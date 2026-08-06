# Users API — FastAPI + SQLModel + Pandas

API REST em Python para gerenciar usuários, contas, cartões e notificações, com persistência real em banco relacional e uma camada de analytics em cima dos próprios dados.

> **Quer testar rápido?** Dá uma olhada no [GUIA_RAPIDO.md](GUIA_RAPIDO.md) — tem o passo a passo completo lá.

Comecei esse projeto no Bootcamp Santander (DIO) como um desafio de API simples com dados em memória. Depois resolvi evoluir para algo mais próximo do que se vê em produção: banco de dados de verdade, modelagem relacional, testes automatizados e um endpoint de análise de dados com Pandas.

## O que a API faz

- CRUD completo de usuários (GET, POST, PUT, PATCH, DELETE)
- Autenticação via JWT — leitura é pública, escrita exige login
- Paginação e filtro por nome na listagem
- Modelagem relacional com chaves estrangeiras
- Persistência em PostgreSQL (Neon) / SQLite local
- Analytics com Pandas: média, mediana, desvio padrão, distribuição por faixa de limite, contas negativas, correlação saldo×limite, ranking dos maiores/menores saldos
- Exportação da base em CSV
- Suíte de testes com pytest, banco isolado em memória
- Dockerfile pronto pra build

## Modelagem

```
Usuario 1───1 Conta
Usuario 1───1 Cartao
Usuario 1───N Recurso
Usuario 1───N News
```

Cada uma dessas é uma tabela própria, ligada por chave estrangeira.

## Endpoints

| Método | Endpoint                     | Autenticação | O que faz                                       |
| ------- | ---------------------------- | :------------: | ----------------------------------------------- |
| POST    | `/auth/login`              |       —       | Login (usuário + senha), retorna JWT           |
| GET     | `/usuario`                 |    pública    | Lista usuários (paginação + filtro por nome) |
| GET     | `/usuario/{id}`            |    pública    | Busca um usuário específico                   |
| POST    | `/usuario`                 |       🔒       | Cria um usuário                                |
| PUT     | `/usuario/{id}`            |       🔒       | Substitui o usuário inteiro                    |
| PATCH   | `/usuario/{id}`            |       🔒       | Atualiza só os campos enviados                 |
| DELETE  | `/usuario/{id}`            |       🔒       | Remove um usuário                              |
| GET     | `/relatorios/estatisticas` |    pública    | Estatísticas agregadas (Pandas)                |
| GET     | `/relatorios/top-usuarios` |    pública    | Ranking por saldo ou limite                     |
| GET     | `/relatorios/usuarios.csv` |    pública    | Exporta a base em CSV                           |

🔒 = exige header `Authorization: Bearer <token>`, obtido em `/auth/login`.

Documentação interativa (Swagger) disponível em `/docs` assim que a API sobe. Os assets do Swagger UI ficam hospedados localmente (`app/static/swagger-ui`) em vez de vir de CDN — testando numa rede mais restrita percebi que a página ficava em branco quando o acesso à CDN externa era bloqueado, então resolvi servir os arquivos direto pela própria API.

## Autenticação

Leitura (`GET`) é pública de propósito, pra facilitar avaliar o projeto sem precisar logar antes. Escrita exige token.

### Como testar no Swagger

Acesse `/docs` e você vai ver todos os endpoints. Para testar os que exigem autenticação:

**1. Faça login:**
- Procure o endpoint `POST /auth/login`
- Clique em "Try it out"
- Preencha username e password (credenciais do `.env`)
- Execute e copie o `access_token` da resposta

**2. Autorize:**
- Clique no botão "Authorize" no topo da página
- Cole o token no formato: `Bearer <seu-token-aqui>`
- Pronto, agora pode testar os endpoints protegidos

### Exemplo de criação de usuário

No endpoint `POST /usuario`, você pode usar este JSON como base:

```json
{
  "nome": "Jorge Fontes",
  "conta": {
    "numero": "00004-4",
    "agencia": "0001",
    "balanco": 1000.0,
    "limite": 1500.0
  },
  "cartao": {
    "icone": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
    "descricao": "Cartão de crédito"
  },
  "news": []
}
```

**Atenção:** Use ponto (`.`) para decimais, não vírgula. Não inclua campos `id` — eles são gerados automaticamente.

### Via cURL

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=admin&password=sua-senha"

# Usar o token
curl -X DELETE http://localhost:8000/usuario/1 \
  -H "Authorization: Bearer <token>"
```

## Rodando localmente

### Pré-requisitos
- Python 3.12+
- Conta no [Neon](https://neon.tech) (banco PostgreSQL gratuito)

### Setup

**1. Clone e instale as dependências:**
```bash
git clone <seu-repositorio>
cd users-api-python
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Configure o banco de dados Neon:**

Crie uma conta em [neon.tech](https://neon.tech) e um novo projeto. Na aba **Connection Details**, copie a connection string. A string que o Neon fornece vem assim:

```
postgresql://neondb_owner:senha@ep-nome-123.aws.neon.tech/neondb?sslmode=require
```

Você precisa ajustar o prefixo de `postgresql://` para `postgresql+psycopg://`:

```
postgresql+psycopg://neondb_owner:senha@ep-nome-123.aws.neon.tech/neondb?sslmode=require
```

**3. Crie o arquivo `.env` na raiz do projeto:**

Copie o `.env.example` e ajuste com suas credenciais:

```bash
cp .env.example .env
```

Depois edite o `.env` com suas informações:
```bash
DATABASE_URL=postgresql+psycopg://sua-string-ajustada-aqui
SECRET_KEY=gere-uma-chave-com-openssl-rand-hex-32
ADMIN_PASSWORD=sua-senha-de-admin
```

**4. Crie as tabelas e popule o banco:**
```bash
python -c "from app.db.database import init_db, get_session; from app.db.seed import seed_if_empty, seed_admin_if_empty; init_db(); session = next(get_session()); seed_admin_if_empty(session); seed_if_empty(session); print('Banco pronto!')"
```

**5. Suba a API:**
```bash
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000/docs` para a documentação interativa.

### Dados de teste

Se quiser testar com mais volume (100 usuários sintéticos):

```bash
pip install -r requirements-dev.txt
python -m scripts.seed_100
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest -v
```

26 testes cobrindo CRUD, autenticação (login válido/inválido, token ausente/expirado), casos de erro (404), paginação, filtro e os endpoints de relatório (incluindo o ranking). Rodam em banco SQLite em memória, isolado — não tocam no banco local.

## Troubleshooting

### `ModuleNotFoundError: No module named 'psycopg'`
Instale o driver PostgreSQL:
```bash
pip install psycopg[binary]
```

### `RuntimeError` ao iniciar a API
Provavelmente faltam variáveis no `.env`. Confira se tem `SECRET_KEY` e `ADMIN_PASSWORD` definidos.

### `401 Unauthorized` no Swagger
Seu token expirou ou não foi configurado. Faça login de novo no endpoint `/auth/login` e autorize com o novo token.

### Erro ao criar usuário: `JSON parse error`
Geralmente é vírgula no lugar de ponto em números decimais.  
Errado: `"limite": 1500,0`  
Certo: `"limite": 1500.0`

### Banco não conecta no Neon
Checklist:
- A URL no `.env` começa com `postgresql+psycopg://`?
- Tem `?sslmode=require` no final da URL?
- Instalou `psycopg[binary]`?
- Não tem espaços antes/depois do `=` no `.env`?

Testar conexão:
```bash
python -c "from app.db.database import engine; engine.connect(); print('Conexão OK!')"
```

## Docker

```bash
docker build -t users-api .
docker run -p 8000:8000 users-api
```

## Deploy

Publicado no Railway. Em produção, defina `DATABASE_URL` apontando pra um Postgres gerenciado — localmente ele cai em SQLite sem precisar configurar nada.

## Estrutura do projeto

```
app/
├── main.py            # cria o FastAPI, registra os routers, popula o banco no startup
├── core/
│   ├── config.py       # configuração via variável de ambiente
│   ├── security.py     # hash de senha (bcrypt) e JWT
│   └── deps.py          # dependency que valida o token nos endpoints protegidos
├── db/
│   ├── database.py    # conexão com o banco
│   ├── seed.py         # dados de exemplo + usuário admin padrão
│   └── seed_bulk.py    # gerador de dados sintéticos (Faker)
├── models/
│   ├── usuario.py       # tabelas e schemas de negócio
│   └── auth.py           # tabela do usuário de login
├── routers/
│   ├── auth.py           # POST /auth/login
│   ├── usuario.py       # CRUD
│   └── relatorios.py    # analytics e CSV
└── static/swagger-ui/   # assets do Swagger self-hosted (css/js), sem depender de CDN

scripts/seed_100.py      # popula o banco com dados sintéticos
tests/                    # suíte pytest
Dockerfile
```

## Sobre a arquitetura

Comecei com tudo num `main.py` só (dado fake em dicionário Python, sem persistência). Reestruturei em camadas — routers separados de modelos, modelos separados de acesso a banco — depois de perceber que isso ia ficar difícil de manter conforme eu fosse adicionando funcionalidade.

<div align="center">
<p align="center">
  <img src="docs/diagramas/arquitetura_preview.png" alt="Arquitetura da API" style="border-radius: 12px;" width: 50%; />
</p>

<p align="center">
  <img src="docs/diagramas/fluxo_preview.png" alt="Fluxo de Requisições" style="border-radius: 12px;" width: 70%; />
</p>
</div>

## Atualizações possíveis (Futuramente)

- Autenticação por perfil (hoje é um único usuário admin — não tem controle por papel/permissão)
- Endpoint de analytics com série temporal (hoje as tabelas não guardam data de criação, então não dá pra ver evolução no tempo)
- Rate limiting nos endpoints públicos

## Stack

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLModel-E92063?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLModel" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <br/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT" />
  <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" />
  <br/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black" alt="Swagger" />
  <img src="https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white" alt="Railway" />
</div>
