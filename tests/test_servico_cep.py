import pytest
from unittest.mock import MagicMock, patch
from api.services.servico_cep import ServicoCep
from core.models.cep_model import Cep

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def servico_cep(mock_db_session):
    return ServicoCep(mock_db_session)

@pytest.mark.asyncio
async def test_fetch_cep_invalid_length(servico_cep):
    with pytest.raises(ValueError, match="CEP invalido"):
        await servico_cep.buscar_cep("123")

@pytest.mark.asyncio
@patch("api.services.servico_cep.BrasilApiClient.buscar")
async def test_fetch_cep_brasil_api_success(mock_brasil_api, servico_cep, mock_db_session):
    mock_brasil_api.return_value = {
        "cep": "01001000",
        "logradouro": "Praca da Se",
        "bairro": "Se",
        "localidade": "Sao Paulo",
        "uf": "SP"
    }
    
    servico_cep.repository.get_by_cep = MagicMock(return_value=None)
    
    mock_created_cep = Cep(cep="01001000", logradouro="Praca da Se", bairro="Se", localidade="Sao Paulo", uf="SP")
    servico_cep.repository.create = MagicMock(return_value=mock_created_cep)

    resultado = await servico_cep.buscar_cep("01001000")
    
    assert resultado is not None
    assert resultado["cep"] == "01001000"
    assert resultado["logradouro"] == "Praca da Se"
    mock_brasil_api.assert_called_once_with("01001000")
    servico_cep.repository.create.assert_called_once()

@pytest.mark.asyncio
@patch("api.services.servico_cep.BrasilApiClient.buscar")
@patch("api.services.servico_cep.ViaCepClient.buscar")
async def test_fetch_cep_brasil_api_fail_viacep_success(mock_viacep, mock_brasil, servico_cep):
    from api.services.clientes.clientes_cep import CepClientException
    mock_brasil.side_effect = CepClientException("Timeout")
    mock_viacep.return_value = {
        "cep": "01001000",
        "logradouro": "Praca da Se",
        "bairro": "Se",
        "localidade": "Sao Paulo",
        "uf": "SP"
    }
    
    servico_cep.repository.get_by_cep = MagicMock(return_value=None)
    
    mock_created_cep = Cep(cep="01001000", logradouro="Praca da Se", bairro="Se", localidade="Sao Paulo", uf="SP")
    servico_cep.repository.create = MagicMock(return_value=mock_created_cep)

    resultado = await servico_cep.buscar_cep("01001000")
    
    assert resultado is not None
    mock_brasil.assert_called_once_with("01001000")
    mock_viacep.assert_called_once_with("01001000")

@pytest.mark.asyncio
@patch("api.services.servico_cep.BrasilApiClient.buscar")
@patch("api.services.servico_cep.ViaCepClient.buscar")
async def test_fetch_cep_both_fail(mock_viacep, mock_brasil, servico_cep):
    from api.services.clientes.clientes_cep import CepClientException
    mock_brasil.side_effect = CepClientException("Timeout")
    mock_viacep.side_effect = CepClientException("Timeout")
    
    servico_cep.repository.get_by_cep = MagicMock(return_value=None)
    
    resultado = await servico_cep.buscar_cep("01001000")
    assert resultado is None

@pytest.mark.asyncio
@patch("api.services.servico_cep.BrasilApiClient.buscar")
async def test_fetch_cep_upsert_local_data(mock_brasil_api, servico_cep, mock_db_session):
    mock_brasil_api.return_value = {
        "cep": "01001000",
        "logradouro": "Novo Logradouro",
        "bairro": "Novo Bairro",
        "localidade": "Nova Localidade",
        "uf": "SP"
    }
    
    mock_local_cep = Cep(
        cep="01001000",
        logradouro="Velho Logradouro",
        bairro="Velho Bairro",
        localidade="Velha Localidade",
        uf="SP",
        uf_codigo=35,
        municipio_codigo=3550308,
        tipo_logradouro_codigo=None
    )
    
    servico_cep.repository.get_by_cep = MagicMock(return_value=mock_local_cep)
    
    resultado = await servico_cep.buscar_cep("01001000")
    
    assert resultado is not None
    assert resultado["logradouro"] == "Novo Logradouro"
    assert resultado["bairro"] == "Novo Bairro"
    assert resultado["localidade"] == "Nova Localidade"
    assert mock_local_cep.logradouro == "Novo Logradouro"
    
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
@patch("api.services.servico_cep.BrasilApiClient.buscar")
async def test_fetch_cep_missing_optional_fields(mock_brasil_api, servico_cep, mock_db_session):
    mock_brasil_api.return_value = {
        "cep": "01001000",
        "localidade": "Sao Paulo",
        "uf": "SP"
    }
    
    servico_cep.repository.get_by_cep = MagicMock(return_value=None)
    
    mock_created_cep = Cep(cep="01001000", logradouro=None, bairro=None, localidade="Sao Paulo", uf="SP")
    servico_cep.repository.create = MagicMock(return_value=mock_created_cep)

    resultado = await servico_cep.buscar_cep("01001000")
    
    assert resultado is not None
    assert resultado["cep"] == "01001000"
    assert resultado["logradouro"] is None
    assert resultado["bairro"] is None
    assert resultado["localidade"] == "Sao Paulo"
    assert resultado["uf"] == "SP"
    mock_brasil_api.assert_called_once_with("01001000")
    servico_cep.repository.create.assert_called_once()
