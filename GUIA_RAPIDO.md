# Guia Rápido

Esse guia é pra quem quer testar a API rapidamente. Se tiver dúvida, o README tem mais detalhes.

## Antes de começar

- Python 3.12+ instalado
- Conta gratuita no [Neon](https://neon.tech)

## Setup

### Instalar dependências

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Ativar (Linux/Mac)
source .venv/bin/activate

# Instalar
pip install -r requirements.txt
```

### Configurar banco Neon

**1. Criar projeto no Neon:**
- Acesse [neon.tech](https://neon.tech) e faça login
- Crie um novo projeto
- Na aba "Connection Details", copie a connection string

**2. Ajustar a string:**

O Neon te dá algo assim:
```
postgresql://usuario:senha@host.neon.tech/neondb?sslmode=require
```

Você precisa trocar o começo:
```
postgresql+psycopg://usuario:senha@host.neon.tech/neondb?sslmode=require
```

**3. Criar o `.env`:**

Copie o `.env.example` e preencha:

```bash
DATABASE_URL=postgresql+psycopg://sua-string-aqui
SECRET_KEY=gere-com-openssl-rand-hex-32
ADMIN_PASSWORD=escolha-uma-senha
```

### Criar tabelas e popular

```bash
python -c "from app.db.database import init_db, get_session; from app.db.seed import seed_if_empty, seed_admin_if_empty; init_db(); session = next(get_session()); seed_admin_if_empty(session); seed_if_empty(session); print('Pronto!')"
```

### Subir a API

```bash
uvicorn app.main:app --reload
```

Se aparecer `Uvicorn running on http://127.0.0.1:8000`, tá funcionando.

## Testando no Swagger

### Abrir a documentação

No navegador: **http://localhost:8000/docs**

### Fazer login

1. Procure `POST /auth/login`
2. Clique em "Try it out"
3. Preencha username e password (do `.env`)
4. Execute e copie o `access_token`

### Autorizar

1. Clique no botão "Authorize" no topo
2. Cole: `Bearer seu-token-aqui` (com espaço depois de Bearer)
3. Clique em "Authorize" e "Close"

Pronto, agora você pode testar os endpoints.

## Testando endpoints

### Listar usuários

- `GET /usuario` → Try it out → Execute
- Deve retornar 3 usuários: João, Maria e Antony

### Buscar usuário específico

- `GET /usuario/{usuario_id}`
- Digite `1` no campo usuario_id
- Execute
- Deve retornar o João Silva

### Criar usuário

- `POST /usuario`
- Try it out
- Cole este JSON:

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

- Execute
- Deve retornar o usuário criado com id 4

### Ver relatórios

- `GET /relatorios/balanco-total` - soma de todos os saldos
- `GET /relatorios/limite-medio` - média dos limites
- `GET /relatorios/usuarios-por-agencia` - agrupa por agência

## Personalizando

Quando for criar um usuário, ajuste o JSON:

```json
{
  "nome": "Seu Nome",
  "conta": {
    "numero": "00005-5",        // número único
    "agencia": "0001",
    "balanco": 2500.0,          // use ponto, não vírgula
    "limite": 3000.0
  },
  "cartao": {
    "icone": "https://...",
    "descricao": "Descrição do cartão"
  },
  "news": []                    // pode ser vazio ou ter notícias
}
```

## Erros comuns

**401 Unauthorized**  
Token expirou. Faça login de novo.

**422 Unprocessable Entity**  
JSON com erro. Geralmente:
- Vírgula em vez de ponto: `1500,0` → `1500.0`
- Falta vírgula entre campos
- Campo `id` incluído (ele é automático)

**404 Not Found**  
ID não existe. Liste com `GET /usuario` pra ver quais existem.

## Gerar dados de teste

Se quiser 100 usuários pra testar paginação:

```bash
pip install -r requirements-dev.txt
python -m scripts.seed_100
```

Depois teste:
- `GET /usuario?skip=10&limit=20` (paginação)
- `GET /usuario?nome=Silva` (filtro)

## Checklist

Conseguiu fazer?

- [ ] Subir a API
- [ ] Acessar o Swagger
- [ ] Fazer login e autorizar
- [ ] Listar usuários
- [ ] Criar um usuário
- [ ] Buscar por ID
- [ ] Ver relatórios

Se conseguiu tudo, beleza! Agora dá uma olhada no README pra entender a arquitetura e rodar os testes.

## Deu problema?

Confere a seção Troubleshooting no README.md
