from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.models import (
    CiudadRequest,
    ConexionRequest,
    MensajeResponse,
    RutaRequest,
    RutaResponse,
    TodasRutasResponse,
)
from backend.app.services.rutas_service import RutasService

# Instancia principal de FastAPI. Desde aqui se exponen todos los endpoints.
app = FastAPI(
    title="Practica 1 - Ruta mas corta",
    description="API para consultar rutas entre ciudades usando Prolog como motor logico.",
    version="1.0.0",
)

# CORS permite que el frontend de Vite, que corre en el puerto 5173,
# pueda consumir el backend local en el puerto 8000 desde el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_service() -> RutasService:
    # Punto unico para construir el servicio; facilita cambiar dependencias despues.
    return RutasService()


# Endpoint de prueba para verificar que el backend esta levantado.
@app.get("/")
def health_check() -> MensajeResponse:
    return MensajeResponse(mensaje="Backend de rutas funcionando.")


# Devuelve las ciudades cargadas en Prolog.
@app.get("/ciudades")
def obtener_ciudades() -> dict[str, list[str]]:
    service = get_service()
    return {"ciudades": service.obtener_ciudades()}


# Consulta a Prolog la ruta de menor distancia entre dos ciudades.
@app.post("/ruta-corta", response_model=RutaResponse)
def ruta_corta(data: RutaRequest) -> RutaResponse:
    service = get_service()
    return RutaResponse(**service.obtener_ruta_mas_corta(data))


# Consulta todas las rutas posibles y las devuelve con su distancia.
@app.post("/todas-rutas", response_model=TodasRutasResponse)
def todas_rutas(data: RutaRequest) -> TodasRutasResponse:
    service = get_service()
    rutas = service.obtener_todas_rutas(data)
    return TodasRutasResponse(rutas=[RutaResponse(**ruta) for ruta in rutas])


# Registra una ciudad nueva en la base de conocimiento Prolog en memoria.
@app.post("/agregar-ciudad", response_model=MensajeResponse)
def agregar_ciudad(data: CiudadRequest) -> MensajeResponse:
    service = get_service()
    service.agregar_ciudad(data.ciudad)
    return MensajeResponse(mensaje="Ciudad agregada correctamente.")


# Registra una conexion nueva entre dos ciudades existentes.
@app.post("/agregar-conexion", response_model=MensajeResponse)
def agregar_conexion(data: ConexionRequest) -> MensajeResponse:
    service = get_service()
    service.agregar_conexion(data)
    return MensajeResponse(mensaje="Conexion agregada correctamente.")
