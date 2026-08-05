# Users API — FastAPI + SQLModel + Pandas

API REST em Python para gerenciar usuários, contas, cartões e notificações, com persistência real em banco relacional e uma camada de analytics em cima dos próprios dados.

Comecei esse projeto no Bootcamp Santander (DIO) como um desafio de API simples com dados em memória. Depois resolvi evoluir para algo mais próximo do que se vê em produção: banco de dados de verdade, modelagem relacional, testes automatizados e um endpoint de análise de dados com Pandas —.

## O que a API faz

- CRUD completo de usuários (GET, POST, PUT, PATCH, DELETE)
- Autenticação via JWT — leitura é pública, escrita exige login
- Paginação e filtro por nome na listagem
- Modelagem relacional com chaves estrangeiras (não mais objetos soltos em memória)
- Persistência em SQLite local / Postgres em produção
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

Documentação interativa (Swagger) disponível em `/docs` assim que a API sobe. Os assets do Swagger UI ficam hospedados localmente (`app/static/swagger-ui`) em vez de vir de CDN — testando numa rede mais restrita percebi que a página ficava em branco quando o acesso à CDN externa era bloqueado, então resolvi servir os arquivos direto pela própria API. O Swagger também tem um botão "Authorize" que já usa esse mesmo login.

## Autenticação

Leitura (`GET`) é pública de propósito, pra facilitar avaliar o projeto sem precisar logar antes. Escrita exige token:

```bash
# 1. login (usuário/senha de demonstração, ver abaixo)
curl -X POST http://localhost:8000/auth/login -d "username=admin&password=admin123"
# -> {"access_token": "...", "token_type": "bearer"}

# 2. usa o token nos endpoints de escrita
curl -X DELETE http://localhost:8000/usuario/1 -H "Authorization: Bearer <token>"
```

O usuário administrador (`admin` / `admin123` por padrão) é criado automaticamente no primeiro boot. Essas credenciais e a `SECRET_KEY` usada para assinar o token são só para rodar localmente sem configuração — em qualquer ambiente que não seja a sua própria máquina, defina `ADMIN_USERNAME`, `ADMIN_PASSWORD` e `SECRET_KEY` como variáveis de ambiente antes de subir.

## Rodando localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000/docs`. Na primeira execução o banco é criado e populado com 3 usuários de exemplo.

Se quiser testar com mais volume de dados (paginação, filtro, estatísticas fazendo mais sentido), dá pra gerar 100 usuários sintéticos com Faker:

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

<div>
<p align="center">
  <img src="docs/diagramas/arquitetura_preview.png" alt="Arquitetura da API" style="border-radius: 12px;" width: 50%; />
</p>

<p align="center">
  <img src="docs/diagramas/fluxo_preview.png" alt="Fluxo de Requisições" style="border-radius: 12px;" width: 70%; />
</p>


# Atualizações possíveis (Futuramente)

- Autenticação por perfil (hoje é um único usuário admin — não tem controle por papel/permissão)
- Endpoint de analytics com série temporal (hoje as tabelas não guardam data de criação, então não dá pra ver evolução no tempo)
- Rate limiting nos endpoints públicos

## Stack

<p align="left">
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
</p>
