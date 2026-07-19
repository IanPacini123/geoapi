import pytest
import httpx
from unittest.mock import patch
from api.services.clientes.clientes_cep import ViaCepClient, BrasilApiClient, CepClientException

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_viacep_success(mock_get):
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "cep": "01001-000",
                "logradouro": "Praca da Se",
                "bairro": "Se",
                "localidade": "Sao Paulo",
                "uf": "SP"
            }
    
    mock_get.return_value = MockResponse()
    result = await ViaCepClient.buscar("01001000")
    
    assert result is not None
    assert result["cep"] == "01001000"
    assert result["logradouro"] == "Praca da Se"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_viacep_error_payload(mock_get):
    class MockResponse:
        status_code = 200
        def json(self):
            return {"erro": "true"}
    
    mock_get.return_value = MockResponse()
    result = await ViaCepClient.buscar("99999999")
    assert result is None

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_viacep_request_error(mock_get):
    mock_get.side_effect = httpx.RequestError("Timeout")
    with pytest.raises(CepClientException):
        await ViaCepClient.buscar("01001000")

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_brasilapi_success(mock_get):
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "cep": "01001000",
                "street": "Praca da Se",
                "neighborhood": "Se",
                "city": "Sao Paulo",
                "state": "SP"
            }
    
    mock_get.return_value = MockResponse()
    result = await BrasilApiClient.buscar("01001000")
    
    assert result is not None
    assert result["cep"] == "01001000"
    assert result["logradouro"] == "Praca da Se"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_brasilapi_404(mock_get):
    class MockResponse:
        status_code = 404
        def raise_for_status(self):
            pass
    
    mock_get.return_value = MockResponse()
    result = await BrasilApiClient.buscar("99999999")
    assert result is None

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_brasilapi_request_error(mock_get):
    mock_get.side_effect = httpx.RequestError("Timeout")
    with pytest.raises(CepClientException):
        await BrasilApiClient.buscar("01001000")
