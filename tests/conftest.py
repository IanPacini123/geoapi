import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.banco_dados import Base
import core.models.ibge_models
import core.models.cep_model
import core.models.auditoria_model
import core.models.sistema_autorizado_model

from sqlalchemy.pool import StaticPool

# Cria um engine SQLite em memoria
# O SQLite e muito mais leve e rapido para os testes, 
# e dispensa a necessidade de ter o PostgreSQL rodando.
engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}, # Necessario para SQLite em memoria em alguns contextos multi-thread, mas inofensivo aqui
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="function")
def db_session_memory():
    """
    Fixture que cria as tabelas no SQLite em memoria,
    prove a sessao para o teste, e depois destroi as tabelas.
    O escopo "function" garante que o banco nasce e morre para cada teste,
    garantindo total isolamento de estado.

    Gera:
        Session: A sessao de banco de dados SQLite em memoria para uso no teste.

    Fixture that creates the tables in the in-memory SQLite,
    provides the session for the test, and then drops the tables.
    The "function" scope guarantees the database is born and dies for each test,
    ensuring total state isolation.

    Yields:
        Session: The in-memory SQLite database session for use in the test.
    """
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)
