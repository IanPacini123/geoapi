from pydantic import BaseModel
from typing import List, Optional

class BatchValidationRequest(BaseModel):
    municipiosIbge: Optional[List[int]] = []
    ufsIbge: Optional[List[int]] = []
    paisesIbge: Optional[List[int]] = []

class BatchValidationResponse(BaseModel):
    valido: bool
    mensagensErro: List[str]
