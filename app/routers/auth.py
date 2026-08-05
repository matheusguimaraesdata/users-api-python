from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.security import create_access_token, verify_password
from app.db.database import get_session
from app.models.auth import AuthUser, Token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """
    Login OAuth2 padrão (username + password via form).
    Retorna um JWT que deve ser enviado como `Authorization: Bearer <token>`
    nos endpoints de escrita (POST/PUT/PATCH/DELETE de /usuario).
    """
    user = session.exec(
        select(AuthUser).where(AuthUser.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.username)
    return Token(access_token=token)
