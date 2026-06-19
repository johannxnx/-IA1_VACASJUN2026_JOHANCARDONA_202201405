from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

class FacturaOut(BaseModel):
    id: int
    proveedor_id: Optional[int]
    usuario_id: Optional[int]
    numero_factura: Optional[str]
    fecha_factura: Optional[date]
    subtotal: Optional[Decimal]
    impuestos: Optional[Decimal]
    total: Optional[Decimal]
    archivo_nombre: str
    archivo_tipo: Optional[str]
    nombre_proveedor_ocr: Optional[str]
    estado: str
    confianza_ocr: Optional[Decimal]
    creado_en: datetime
    procesado_en: Optional[datetime]

    class Config:
        from_attributes = True

class FacturaDetalle(FacturaOut):
    datos_crudos: Optional[str]
    archivo_ruta: str
