from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.usuario import (
    Cartao,
    Conta,
    News,
    Recurso,
    Usuario,
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
)

router = APIRouter(prefix="/usuario", tags=["Usuários"])


@router.get("", response_model=List[UsuarioRead])
def listar_usuarios(
    offset: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros retornados"),
    nome: Optional[str] = Query(None, description="Filtra por nome (busca parcial)"),
    session: Session = Depends(get_session),
):
    """Lista usuários com paginação e filtro opcional por nome."""
    query = select(Usuario)
    if nome:
        query = query.where(Usuario.nome.ilike(f"%{nome}%"))
    query = query.offset(offset).limit(limit)
    return session.exec(query).all()


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obter_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.post("", response_model=UsuarioRead, status_code=201)
def criar_usuario(payload: UsuarioCreate, session: Session = Depends(get_session)):
    usuario = Usuario(
        nome=payload.nome,
        conta=Conta(**payload.conta.model_dump(exclude={"id"})),
        cartao=Cartao(**payload.cartao.model_dump(exclude={"id"})),
        recurso=[Recurso(**r.model_dump(exclude={"id"})) for r in payload.recurso],
        news=[News(**n.model_dump(exclude={"id"})) for n in payload.news],
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioRead)
def atualizar_usuario_completo(
    usuario_id: int, payload: UsuarioCreate, session: Session = Depends(get_session)
):
    """Substitui o usuário inteiro (todos os campos são obrigatórios)."""
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.nome = payload.nome
    usuario.conta = Conta(**payload.conta.model_dump(exclude={"id"}))
    usuario.cartao = Cartao(**payload.cartao.model_dump(exclude={"id"}))
    usuario.recurso = [Recurso(**r.model_dump(exclude={"id"})) for r in payload.recurso]
    usuario.news = [News(**n.model_dump(exclude={"id"})) for n in payload.news]

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioRead)
def atualizar_usuario_parcial(
    usuario_id: int, payload: UsuarioUpdate, session: Session = Depends(get_session)
):
    """Atualiza só os campos enviados — não exige o objeto inteiro."""
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if payload.nome is not None:
        usuario.nome = payload.nome
    if payload.conta is not None:
        usuario.conta = Conta(**payload.conta.model_dump(exclude={"id"}))
    if payload.cartao is not None:
        usuario.cartao = Cartao(**payload.cartao.model_dump(exclude={"id"}))
    if payload.recurso is not None:
        usuario.recurso = [Recurso(**r.model_dump(exclude={"id"})) for r in payload.recurso]
    if payload.news is not None:
        usuario.news = [News(**n.model_dump(exclude={"id"})) for n in payload.news]

    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=204)
def deletar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(usuario)
    session.commit()
    return None
