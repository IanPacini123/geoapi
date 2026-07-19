import pytest
from api.services.servico_validacao_lote import ServicoValidacaoLote
from api.schemas.validacao_schema import BatchValidationRequest
from core.models.ibge_models import Municipio, Uf, Pais

@pytest.fixture
def servico_lote(db_session_memory):
    return ServicoValidacaoLote(db_session_memory)

def test_validate_all_valid(servico_lote, db_session_memory):
    # Popula o banco com os IDs esperados
    db_session_memory.add(Municipio(codigo_ibge=3550308, nome="Sao Paulo"))
    db_session_memory.add(Municipio(codigo_ibge=2304400, nome="Fortaleza"))
    db_session_memory.add(Uf(codigo_ibge=35, sigla="SP", nome="Sao Paulo"))
    db_session_memory.add(Uf(codigo_ibge=23, sigla="CE", nome="Ceara"))
    db_session_memory.add(Pais(codigo_ibge=76, nome="Brasil"))
    db_session_memory.commit()

    carga_dados = BatchValidationRequest(
        municipiosIbge=[3550308, 2304400],
        ufsIbge=[35, 23],
        paisesIbge=[76]
    )
    
    eh_valido, mensagens_erro = servico_lote.validar(carga_dados)
    
    assert eh_valido is True
    assert len(mensagens_erro) == 0

def test_validate_some_missing(servico_lote, db_session_memory):
    # Popula apenas um ID, deixando o 9999999 faltando
    db_session_memory.add(Municipio(codigo_ibge=3550308, nome="Sao Paulo"))
    db_session_memory.commit()

    carga_dados = BatchValidationRequest(
        municipiosIbge=[3550308, 9999999],
        ufsIbge=[],
        paisesIbge=[]
    )
    
    eh_valido, mensagens_erro = servico_lote.validar(carga_dados)
    
    assert eh_valido is False
    assert len(mensagens_erro) == 1
    assert "9999999" in mensagens_erro[0]
