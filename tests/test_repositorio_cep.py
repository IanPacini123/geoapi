import pytest
from api.repositorios.repositorio_cep import RepositorioCep
from core.models.cep_model import Cep

def test_get_by_cep(db_session_memory):
    repo = RepositorioCep(db_session_memory)
    
    # Prepara o banco
    cep_data = Cep(cep="01001000", logradouro="Praca da Se")
    db_session_memory.add(cep_data)
    db_session_memory.commit()
    
    result = repo.get_by_cep("01001000")
    assert result is not None
    assert result.cep == "01001000"
    assert result.logradouro == "Praca da Se"

def test_create(db_session_memory):
    repo = RepositorioCep(db_session_memory)
    
    cep_data = Cep(cep="01001000", logradouro="Praca da Se")
    result = repo.create(cep_data)
    
    # Verifica o banco de verdade
    db_val = db_session_memory.query(Cep).filter(Cep.cep == "01001000").first()
    assert db_val is not None
    assert db_val.cep == "01001000"
    assert db_val.logradouro == "Praca da Se"
    assert result.cep == "01001000"

def test_update(db_session_memory):
    repo = RepositorioCep(db_session_memory)
    
    # Insere dado inicial
    cep_data = Cep(cep="01001000", logradouro="Antigo")
    db_session_memory.add(cep_data)
    db_session_memory.commit()
    
    # Atualiza a instancia
    cep_data.logradouro = "Novo Logradouro"
    result = repo.update(cep_data)
    
    # Verifica persistencia real
    db_val = db_session_memory.query(Cep).filter(Cep.cep == "01001000").first()
    assert db_val.logradouro == "Novo Logradouro"
    assert result.logradouro == "Novo Logradouro"
