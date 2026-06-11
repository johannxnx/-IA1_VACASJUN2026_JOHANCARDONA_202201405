from pydantic import BaseModel, Field


# Modelo de entrada para consultas que necesitan origen y destino.
class RutaRequest(BaseModel):
    origen: str = Field(..., min_length=1)
    destino: str = Field(..., min_length=1)


# Modelo de entrada para registrar una ciudad nueva.
class CiudadRequest(BaseModel):
    ciudad: str = Field(..., min_length=1)


# Modelo de entrada para registrar una conexion con distancia positiva.
class ConexionRequest(BaseModel):
    origen: str = Field(..., min_length=1)
    destino: str = Field(..., min_length=1)
    distancia: int = Field(..., gt=0)


# Respuesta comun para una ruta: listado de ciudades y distancia total.
class RutaResponse(BaseModel):
    ruta: list[str]
    distancia: int


# Respuesta para el endpoint que devuelve varias rutas.
class TodasRutasResponse(BaseModel):
    rutas: list[RutaResponse]


# Respuesta simple para mensajes de confirmacion.
class MensajeResponse(BaseModel):
    mensaje: str
