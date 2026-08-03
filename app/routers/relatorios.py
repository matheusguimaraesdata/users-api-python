import io

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.usuario import Usuario

router = APIRouter(prefix="/relatorios", tags=["Relatórios & Analytics"])


def _usuarios_para_dataframe(session: Session) -> pd.DataFrame:
    """Achata os usuários (com conta/cartão) em um DataFrame tabular."""
    usuarios = session.exec(select(Usuario)).all()
    linhas = [
        {
            "id": u.id,
            "nome": u.nome,
            "agencia": u.conta.agencia if u.conta else None,
            "balanco": u.conta.balanco if u.conta else 0.0,
            "limite": u.conta.limite if u.conta else 0.0,
            "qtd_recursos": len(u.recurso),
            "qtd_news": len(u.news),
        }
        for u in usuarios
    ]
    return pd.DataFrame(linhas)


@router.get("/estatisticas")
def estatisticas(session: Session = Depends(get_session)):
    """
    Retorna estatísticas agregadas da base de usuários — saldo médio,
    limite médio, distribuição por agência etc. Demonstra manipulação
    analítica dos dados (Pandas), não só CRUD.
    """
    df = _usuarios_para_dataframe(session)
    if df.empty:
        return {"total_usuarios": 0, "mensagem": "Nenhum usuário cadastrado ainda."}

    return {
        "total_usuarios": int(len(df)),
        "balanco_medio": round(float(df["balanco"].mean()), 2),
        "balanco_total": round(float(df["balanco"].sum()), 2),
        "limite_medio": round(float(df["limite"].mean()), 2),
        "limite_maximo": round(float(df["limite"].max()), 2),
        "media_recursos_por_usuario": round(float(df["qtd_recursos"].mean()), 2),
        "media_news_por_usuario": round(float(df["qtd_news"].mean()), 2),
        "usuarios_por_agencia": df.groupby("agencia")["id"].count().to_dict(),
    }


@router.get("/usuarios.csv")
def exportar_csv(session: Session = Depends(get_session)):
    """Exporta a base de usuários (achatada) em CSV — útil para consumo em BI/Excel."""
    df = _usuarios_para_dataframe(session)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usuarios.csv"},
    )
