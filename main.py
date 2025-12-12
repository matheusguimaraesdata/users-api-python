
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

#=====================================================
# MODELOS DE DOMÍNIO (Pydantic)
#=====================================================

class Conta(BaseModel):
  id: int
  numero: str
  agencia: str
  balanco: float
  limite: float

class Cartao(BaseModel):
  id: int
  icone: str
  descricao: str

class Recurso(BaseModel):
  id: int
  icone: str
  descricao: str

class News(BaseModel):
  id: int
  icone: str
  descricao: str

class Usuario(BaseModel):
  id: int
  nome: str
  conta: Conta
  cartao: Cartao
  recurso: List[Recurso] = Field(default_factory=list)
  news: List[News] = Field(default_factory=list)

# Modelo de uso para o POST (sem id)
class CreateUsuario(BaseModel):
  nome: str
  conta: Conta
  cartao: Cartao
  recurso: List[Recurso] = Field(default_factory=list)
  news: List[News] = Field(default_factory=list)
#==============================================
# "BANCO DE DADOS" em memória
#==============================================

database_fake: Dict[int, Usuario] = {
    4: Usuario(
        id=4,
        nome="João Silva",
        conta=Conta(
            id=7, numero="00001-1", agencia="0001", balanco=0.0, limite=500.0
        ),
        cartao=Cartao(
            id=4, 
            icone="https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
            descricao="Cartão de crédito principal"
        ),
        recurso=[],
        news=[
            News(
                id=9,
                icone="https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
                descricao="João Silva, invista hoje para garantir um futuro seguro e próspero. Seu futuro agradece!"
            )
        ]
    ),
    5: Usuario(
        id=5,
        nome="Maria Oliveira",
        conta=Conta(
            id=8, numero="00002-2", agencia="0001", balanco=0.0, limite=500.0
        ),
        cartao=Cartao(
            id=5,
            icone="https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg", # Adicionado
            descricao="Cartão de crédito principal"
        ),
        recurso=[],
        news=[
            News(
                id=10,
                icone="https://digitalinnovationone.io/santander-dev-week-2023-api/icons/credit.svg",
                descricao="Invista hoje para um futuro seguro e estável, Maria Oliveira. O seu futuro financeiro depende disso!"
            )
        ]
    ),
    6: Usuario(
        id=6,
        nome="Antony Guimarães",
        conta=Conta(
            id=9, numero="00003-3", agencia="0001", balanco=0.0, limite=500.0
        ),
        cartao=Cartao(
            id=6,
            icone="https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg", # Adicionado
            descricao="Cartão de crédito principal"
        ),
        recurso=[],
        news=[
            News(
                id=11,
                icone="https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
                descricao="Oi Tony, investir é a chave para multiplicar seu dinheiro. Não deixe sua grana parada!"
            )
        ]
    ),
}

#============================================================================
# App FastApi
#============================================================================

app = FastAPI(
    title= "Projeto Santander DIO 2025 - Users API com Python",
    description= "API de usuários, contas, cartões, features e news para o pipeline ETL com IA.",
    version= "1.0.0",
)

@app.get("/")
def root():
  return {"status": "API online no Railway. Acesse /docs para ter acesso ao Swagger"}


#===============================================================================
# ENDPOINTS DE USUARIOS
#===============================================================================

@app.get("/usuario", response_model=List[Usuario])
def lista_usuarios():
    """
    Retorna todos os usuários.
    """
    return list(database_fake.values())


@app.get("/usuario/{id_de_usuario}", response_model=Usuario)
def get_usuarios_by_id(id_de_usuario: int):
    """
    Retorna um usuário pelo ID.
    """
    usuario = database_fake.get(id_de_usuario)
    if not usuario:
      raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@app.post("/usuario",response_model=Usuario, status_code=201)
def create_usuario(usuario_data: CreateUsuario):
    """
    Cria um novo usuário e retorna usuário criado
    """
    novo_id = max(database_fake.keys(), default = 0) + 1
    novo_usuario = Usuario(
      id=novo_id,
      nome=usuario_data.nome,
      conta=usuario_data.conta,
      cartao=usuario_data.cartao,
      recurso=usuario_data.recurso,
      news=usuario_data.news
    )
    
    database_fake[novo_id] = novo_usuario
    return novo_usuario
  

@app.put("/usuario/{id_de_usuario}", response_model = Usuario)
def update_de_usuario(id_de_usuario: int, usuario: Usuario):
    """
    Atualiza o usuário completo.
    """
    if id_de_usuario != usuario.id:
      raise HTTPException(status_code=400, detail="O ID da URL diferente do ID enviado no corpo.")

    if id_de_usuario not in database_fake:
      raise HTTPException(status_code=404, detail="Usuário não encontrado")

    database_fake[id_de_usuario] = usuario
    return usuario





#
