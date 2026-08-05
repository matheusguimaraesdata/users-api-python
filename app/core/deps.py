from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token

# tokenUrl aponta pro endpoint de login — é o que faz o botão "Authorize" do
# Swagger funcionar automaticamente, sem precisar copiar/colar token manualmente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    """Dependency usada nos endpoints de escrita. Levanta 401 se o token
    não vier, for inválido ou tiver expirado."""
    username = decode_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username
