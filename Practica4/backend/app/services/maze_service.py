# ============================================================
# maze_service.py - Capa de servicios (lógica de negocio)
# Coordina la ejecución de algoritmos y gestiona laberintos predefinidos.
# Patrón de arquitectura: Capas (Routes → Services → Algorithms)
# ============================================================

from app.algorithms.bfs import bfs
from app.algorithms.dfs import dfs
from app.models.maze_model import MazeRequest, MazeResponse, PredefinedMaze


# ============================================================
# Laberintos predefinidos del sistema (mínimo 5 requeridos)
# Cada laberinto es una matriz 2D: 0 = libre, 1 = obstáculo
# ============================================================
LABERINTOS_PREDEFINIDOS = [
    PredefinedMaze(
        id=1,
        name="Laberinto Simple",
        grid=[
            [0, 0, 0, 0, 0],
            [1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ],
        start=[0, 0],
        end=[4, 4]
    ),
    PredefinedMaze(
        id=2,
        name="Laberinto Serpentín",
        grid=[
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ],
        start=[0, 0],
        end=[6, 6]
    ),
    PredefinedMaze(
        id=3,
        name="Laberinto Difícil",
        grid=[
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 1, 1],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
        ],
        start=[0, 0],
        end=[7, 7]
    ),
    PredefinedMaze(
        id=4,
        name="Laberinto Sin Salida Aparente",
        grid=[
            [0, 0, 0, 1, 0, 0],
            [1, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 0],
            [1, 1, 0, 0, 0, 0],
        ],
        start=[0, 0],
        end=[5, 5]
    ),
    PredefinedMaze(
        id=5,
        name="Laberinto Grande",
        grid=[
            [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 1, 1, 1, 1, 0],
        ],
        start=[0, 0],
        end=[9, 9]
    ),
    PredefinedMaze(
        id=6,
        name="Laberinto Sin Ruta",
        grid=[
            [0, 0, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0],
        ],
        start=[0, 0],
        end=[0, 4]
    ),
]


def ejecutar_busqueda(request: MazeRequest) -> MazeResponse:
    """
    Servicio principal: valida la petición y delega la búsqueda
    al algoritmo correspondiente (BFS o DFS).

    Args:
        request: Objeto MazeRequest con grid, start, end y algorithm

    Returns:
        MazeResponse con los resultados de la búsqueda
    """

    # Validar que el algoritmo solicitado sea válido
    algoritmo = request.algorithm.lower()
    if algoritmo not in ("bfs", "dfs"):
        return MazeResponse(
            found=False,
            path=[],
            explored=[],
            path_length=0,
            nodes_explored=0,
            execution_time=0.0,
            message=f"Algoritmo '{request.algorithm}' no soportado. Use 'bfs' o 'dfs'."
        )

    # Seleccionar y ejecutar el algoritmo correspondiente
    if algoritmo == "bfs":
        resultado = bfs(request.grid, request.start, request.end)
    else:
        resultado = dfs(request.grid, request.start, request.end)

    # Construir y retornar el modelo de respuesta
    return MazeResponse(**resultado)


def obtener_laberintos_predefinidos() -> list[PredefinedMaze]:
    """
    Retorna la lista completa de laberintos predefinidos del sistema.
    """
    return LABERINTOS_PREDEFINIDOS


def obtener_laberinto_por_id(maze_id: int) -> PredefinedMaze | None:
    """
    Busca y retorna un laberinto predefinido por su ID.
    Retorna None si no se encuentra.
    """
    for laberinto in LABERINTOS_PREDEFINIDOS:
        if laberinto.id == maze_id:
            return laberinto
    return None
