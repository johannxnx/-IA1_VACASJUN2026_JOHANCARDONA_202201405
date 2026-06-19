from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProveedorCreate(BaseModel):
    nombre: str
    nit: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    activo: Optional[bool] = None

class ProveedorOut(BaseModel):
    id: int
    nombre: str
    nit: str
    direccion: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True
