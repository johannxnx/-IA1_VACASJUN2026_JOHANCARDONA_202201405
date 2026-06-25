# ============================================================
# maze_routes.py - Rutas (endpoints) de la API REST
# Define los endpoints que el frontend puede consumir.
# Patrón de capas: esta capa solo recibe y responde peticiones HTTP,
# delegando la lógica al servicio correspondiente.
# ============================================================

from fastapi import APIRouter, HTTPException
from app.models.maze_model import MazeRequest, MazeResponse, PredefinedMaze
from app.services.maze_service import (
    ejecutar_busqueda,
    obtener_laberintos_predefinidos,
    obtener_laberinto_por_id
)

# Router de FastAPI agrupa todas las rutas relacionadas con laberintos
router = APIRouter(tags=["Laberinto"])


@router.post("/search", response_model=MazeResponse)
def buscar_ruta(request: MazeRequest):
    """
    Endpoint principal: ejecuta BFS o DFS sobre el laberinto enviado.

    Body JSON esperado:
        {
            "grid": [[0,0,1,...], ...],
            "start": [fila, columna],
            "end": [fila, columna],
            "algorithm": "bfs" | "dfs"
        }

    Retorna:
        MazeResponse con ruta, nodos explorados y tiempo de ejecución.
    """
    try:
        resultado = ejecutar_busqueda(request)
        return resultado
    except Exception as e:
        # Si ocurre un error inesperado, retornar HTTP 500
        raise HTTPException(status_code=500, detail=f"Error al ejecutar la búsqueda: {str(e)}")


@router.get("/mazes", response_model=list[PredefinedMaze])
def listar_laberintos():
    """
    Retorna la lista completa de laberintos predefinidos disponibles.
    El frontend los usa para cargar laberintos de prueba con un clic.
    """
    return obtener_laberintos_predefinidos()


@router.get("/mazes/{maze_id}", response_model=PredefinedMaze)
def obtener_laberinto(maze_id: int):
    """
    Retorna un laberinto predefinido específico por su ID.

    Args:
        maze_id: ID numérico del laberinto

    Retorna:
        PredefinedMaze o HTTP 404 si no existe.
    """
    laberinto = obtener_laberinto_por_id(maze_id)
    if laberinto is None:
        raise HTTPException(
            status_code=404,
            detail=f"Laberinto con ID {maze_id} no encontrado."
        )
    return laberinto
