import httpx

class CepClientException(Exception):
    pass

class ViaCepClient:
    BASE_URL = "https://viacep.com.br/ws/{cep}/json/"

    @classmethod
    async def buscar(cls, cep: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(cls.BASE_URL.format(cep=cep), timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if "erro" in data:
                        return None
                    
                    return {
                        "cep": data.get("cep", "").replace("-", ""),
                        "logradouro": data.get("logradouro"),
                        "bairro": data.get("bairro"),
                        "localidade": data.get("localidade"),
                        "uf": data.get("uf")
                    }
                return None
            except httpx.RequestError as e:
                raise CepClientException(f"Erro ao comunicar com ViaCEP: {e}")

class BrasilApiClient:
    BASE_URL = "https://brasilapi.com.br/api/cep/v1/{cep}"

    @classmethod
    async def buscar(cls, cep: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(cls.BASE_URL.format(cep=cep), timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "cep": data.get("cep"),
                        "logradouro": data.get("street"),
                        "bairro": data.get("neighborhood"),
                        "localidade": data.get("city"),
                        "uf": data.get("state")
                    }
                elif response.status_code == 404:
                    return None
                response.raise_for_status()
            except httpx.RequestError as e:
                raise CepClientException(f"Erro ao comunicar com BrasilAPI: {e}")
