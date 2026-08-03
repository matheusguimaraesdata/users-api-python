"""
Popula o banco com 100 usuários sintéticos.

Uso:
    python -m scripts.seed_100
"""
from sqlmodel import Session

from app.db.database import engine, init_db
from app.db.seed_bulk import seed_bulk

if __name__ == "__main__":
    init_db()
    with Session(engine) as session:
        total = seed_bulk(session, quantidade=100)
        print(f"{total} usuários sintéticos inseridos com sucesso.")
