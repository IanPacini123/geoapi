from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from core.configuracoes import settings

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def obter_bd() -> Generator[Session, None, None]:
    """
    Injecao de dependencia para sessao de banco de dados.

    Gera:
        Session: Um objeto de sessao de banco de dados SQLAlchemy.

    Dependency injection for database session.

    Yields:
        Session: A SQLAlchemy database session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
