# ============================================================
# maze_model.py - Modelos de datos con Pydantic
# Define la estructura de las peticiones y respuestas de la API
# ============================================================

from pydantic import BaseModel
from typing import List, Tuple


class MazeRequest(BaseModel):
    """
    Modelo de la petición para ejecutar un algoritmo de búsqueda.

    Campos:
        grid    : Matriz 2D donde 0 = celda libre, 1 = obstáculo
        start   : Posición inicial del agente [fila, columna]
        end     : Posición objetivo del agente [fila, columna]
        algorithm: Algoritmo a ejecutar ("bfs" o "dfs")
    """
    grid: List[List[int]]
    start: List[int]
    end: List[int]
    algorithm: str  # "bfs" o "dfs"


class MazeResponse(BaseModel):
    """
    Modelo de la respuesta tras ejecutar un algoritmo de búsqueda.

    Campos:
        found          : True si se encontró una ruta, False si no existe
        path           : Lista de celdas que conforman la ruta encontrada
        explored       : Lista de celdas visitadas durante la búsqueda
        path_length    : Cantidad de celdas en la ruta final
        nodes_explored : Total de nodos explorados por el algoritmo
        execution_time : Tiempo de ejecución en segundos
        message        : Mensaje descriptivo del resultado
    """
    found: bool
    path: List[List[int]]
    explored: List[List[int]]
    path_length: int
    nodes_explored: int
    execution_time: float
    message: str


class PredefinedMaze(BaseModel):
    """
    Modelo para representar un laberinto predefinido del sistema.

    Campos:
        id    : Identificador único del laberinto
        name  : Nombre descriptivo
        grid  : Matriz 2D del laberinto
        start : Posición inicial sugerida
        end   : Posición objetivo sugerida
    """
    id: int
    name: str
    grid: List[List[int]]
    start: List[int]
    end: List[int]
