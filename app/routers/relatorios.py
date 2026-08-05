import io

import pandas as pd
from fastapi import APIRouter, Depends, Query
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
    Estatísticas agregadas da base de usuários: tendência central (média,
    mediana), dispersão (desvio padrão, quartis), distribuição por faixa de
    limite, proporção de contas negativas e correlação entre saldo e limite.
    """
    df = _usuarios_para_dataframe(session)
    if df.empty:
        return {"total_usuarios": 0, "mensagem": "Nenhum usuário cadastrado ainda."}

    total = len(df)
    contas_negativas = int((df["balanco"] < 0).sum())

    def _std_seguro(serie: pd.Series) -> float:
        """Desvio padrão de 1 registro é matematicamente indefinido (NaN).
        Pandas retorna NaN nesse caso — tratamos como 0 pra não quebrar o JSON
        (NaN não é serializável em JSON puro)."""
        valor = serie.std()
        return 0.0 if pd.isna(valor) else float(valor)

    # Faixas de limite — dá pra ver a distribuição da carteira, não só a média
    faixas = pd.cut(
        df["limite"],
        bins=[-float("inf"), 1000, 5000, 10000, float("inf")],
        labels=["até 1k", "1k–5k", "5k–10k", "acima de 10k"],
    )
    distribuicao_limite = faixas.value_counts().sort_index().to_dict()

    # Correlação simples entre saldo e limite (Pearson) — só faz sentido com
    # mais de 1 usuário e variância não-nula nas duas colunas.
    correlacao_saldo_limite = None
    if total > 1 and df["balanco"].std() > 0 and df["limite"].std() > 0:
        correlacao_saldo_limite = round(float(df["balanco"].corr(df["limite"])), 3)

    return {
        "total_usuarios": total,
        "saldo": {
            "medio": round(float(df["balanco"].mean()), 2),
            "mediano": round(float(df["balanco"].median()), 2),
            "desvio_padrao": round(_std_seguro(df["balanco"]), 2),
            "minimo": round(float(df["balanco"].min()), 2),
            "maximo": round(float(df["balanco"].max()), 2),
            "total": round(float(df["balanco"].sum()), 2),
            "contas_negativas": contas_negativas,
            "percentual_contas_negativas": round(100 * contas_negativas / total, 1),
        },
        "limite": {
            "medio": round(float(df["limite"].mean()), 2),
            "mediano": round(float(df["limite"].median()), 2),
            "desvio_padrao": round(_std_seguro(df["limite"]), 2),
            "maximo": round(float(df["limite"].max()), 2),
            "distribuicao_por_faixa": {str(k): int(v) for k, v in distribuicao_limite.items()},
        },
        "engajamento": {
            "media_recursos_por_usuario": round(float(df["qtd_recursos"].mean()), 2),
            "media_news_por_usuario": round(float(df["qtd_news"].mean()), 2),
        },
        "usuarios_por_agencia": df.groupby("agencia")["id"].count().to_dict(),
        "correlacao_saldo_limite": correlacao_saldo_limite,
    }


@router.get("/top-usuarios")
def top_usuarios(
    criterio: str = Query("balanco", pattern="^(balanco|limite)$", description="Campo usado pra ordenar"),
    limite: int = Query(5, ge=1, le=50, description="Quantos usuários retornar"),
    ordem: str = Query("desc", pattern="^(asc|desc)$", description="asc (menores primeiro) ou desc (maiores primeiro)"),
    session: Session = Depends(get_session),
):
    """
    Ranking dos usuários por saldo ou limite. Útil pra identificar outliers
    (maiores contas, ou contas mais negativas quando ordem=asc).
    """
    df = _usuarios_para_dataframe(session)
    if df.empty:
        return {"total_usuarios": 0, "resultado": []}

    ordenado = df.sort_values(by=criterio, ascending=(ordem == "asc")).head(limite)
    colunas = ["id", "nome", "agencia", "balanco", "limite"]
    return {
        "criterio": criterio,
        "ordem": ordem,
        "resultado": ordenado[colunas].to_dict(orient="records"),
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
