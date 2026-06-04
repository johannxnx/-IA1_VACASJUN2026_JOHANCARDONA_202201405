from functools import lru_cache

from backend.app.integrations.prolog_client import PrologClient
from backend.app.models import ConexionRequest, RutaRequest


@lru_cache
def get_prolog_client() -> PrologClient:
    # Se reutiliza una unica instancia para no recargar el archivo Prolog en cada peticion.
    return PrologClient()


class RutasService:
    def __init__(self, prolog_client: PrologClient | None = None) -> None:
        self.prolog_client = prolog_client or get_prolog_client()

    def obtener_ciudades(self) -> list[str]:
        return self.prolog_client.obtener_ciudades()

    def obtener_ruta_mas_corta(self, data: RutaRequest) -> dict:
        return self.prolog_client.ruta_mas_corta(data.origen, data.destino)

    def obtener_todas_rutas(self, data: RutaRequest) -> list[dict]:
        return self.prolog_client.todas_rutas(data.origen, data.destino)

    def agregar_ciudad(self, ciudad: str) -> None:
        self.prolog_client.agregar_ciudad(ciudad)

    def agregar_conexion(self, data: ConexionRequest) -> None:
        self.prolog_client.agregar_conexion(data.origen, data.destino, data.distancia)
