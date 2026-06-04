from pydantic import BaseModel, Field


class RutaRequest(BaseModel):
    origen: str = Field(..., min_length=1)
    destino: str = Field(..., min_length=1)


class CiudadRequest(BaseModel):
    ciudad: str = Field(..., min_length=1)


class ConexionRequest(BaseModel):
    origen: str = Field(..., min_length=1)
    destino: str = Field(..., min_length=1)
    distancia: int = Field(..., gt=0)


class RutaResponse(BaseModel):
    ruta: list[str]
    distancia: int


class TodasRutasResponse(BaseModel):
    rutas: list[RutaResponse]


class MensajeResponse(BaseModel):
    mensaje: str
