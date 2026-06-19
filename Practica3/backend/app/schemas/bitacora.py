from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BitacoraOut(BaseModel):
    id: int
    factura_id: Optional[int]
    usuario_id: Optional[int]
    fecha_hora: datetime
    documento: Optional[str]
    estado: Optional[str]
    resultado: Optional[str]
    accion: Optional[str]
    detalle_error: Optional[str]

    class Config:
        from_attributes = True
