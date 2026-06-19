from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: str = "admin"

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str
