from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.banco_dados import obter_bd
from api.schemas.cep_schema import CepResponse
from api.services.servico_cep import ServicoCep
from core.limitador import limiter
from core.configuracoes import settings

router = APIRouter(prefix="/api/localidades", tags=["Localidades"])

@router.get("/cep/{cep}", response_model=CepResponse)
@limiter.limit(settings.RATE_LIMIT_CEP)
async def consultar_cep(request: Request, cep: str, db: Session = Depends(obter_bd)):
    service = ServicoCep(db)
    try:
        resultado = await service.buscar_cep(cep)
        if not resultado:
            raise HTTPException(status_code=404, detail="CEP nao encontrado")
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
