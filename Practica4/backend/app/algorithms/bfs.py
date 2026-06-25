# ============================================================
# bfs.py - Algoritmo Breadth-First Search (BFS)
# Búsqueda en anchura: explora nivel por nivel desde el origen.
# Garantiza encontrar el camino más corto en grafos no ponderados.
# ============================================================

from collections import deque
import time


def bfs(grid: list[list[int]], start: list[int], end: list[int]) -> dict:
    # perf_counter tiene resolución de nanosegundos, time.time() no es suficiente
    # para operaciones que duran microsegundos
    """
    Ejecuta BFS sobre una cuadrícula 2D para encontrar la ruta más corta.

    Estrategia:
        Usa una cola (FIFO) para procesar nodos nivel a nivel.
        Cada nodo recuerda su padre para reconstruir la ruta al final.

    Args:
        grid  : Matriz 2D (0 = libre, 1 = obstáculo)
        start : [fila, columna] del punto de inicio
        end   : [fila, columna] del punto destino

    Returns:
        dict con: found, path, explored, path_length, nodes_explored, execution_time
    """

    # --- Inicio de medición de tiempo (alta resolución) ---
    start_time = time.perf_counter()

    filas = len(grid)
    columnas = len(grid[0])

    inicio = tuple(start)
    destino = tuple(end)

    # Cola BFS: cada elemento es la posición actual
    cola = deque()
    cola.append(inicio)

    # Registro de celdas visitadas (evita procesar el mismo nodo dos veces)
    visitados = set()
    visitados.add(inicio)

    # Mapa de padres: clave = celda actual, valor = celda desde donde llegamos
    # Sirve para reconstruir la ruta al final
    padres = {inicio: None}

    # Lista de nodos explorados en orden (para visualización en el frontend)
    explorados = []

    encontrado = False

    while cola:
        actual = cola.popleft()
        explorados.append(list(actual))

        # Si llegamos al destino, terminamos
        if actual == destino:
            encontrado = True
            break

        # Explorar los 4 vecinos posibles: arriba, abajo, izquierda, derecha
        fila, col = actual
        vecinos = [
            (fila - 1, col),  # arriba
            (fila + 1, col),  # abajo
            (fila, col - 1),  # izquierda
            (fila, col + 1),  # derecha
        ]

        for nfila, ncol in vecinos:
            vecino = (nfila, ncol)

            # Validar que el vecino esté dentro de los límites del laberinto
            if not (0 <= nfila < filas and 0 <= ncol < columnas):
                continue

            # Ignorar obstáculos (valor 1 en la cuadrícula)
            if grid[nfila][ncol] == 1:
                continue

            # Ignorar celdas ya visitadas
            if vecino in visitados:
                continue

            # Marcar como visitado y agregar a la cola
            visitados.add(vecino)
            padres[vecino] = actual
            cola.append(vecino)

    # --- Fin de medición: convertir a milisegundos ---
    execution_time = (time.perf_counter() - start_time) * 1000

    # Reconstruir la ruta si se encontró el destino
    ruta = []
    if encontrado:
        ruta = _reconstruir_ruta(padres, destino)

    return {
        "found": encontrado,
        "path": ruta,
        "explored": explorados,
        "path_length": len(ruta),
        "nodes_explored": len(explorados),
        "execution_time": round(execution_time, 4),  # en milisegundos
        "message": "Ruta encontrada con BFS." if encontrado else "No existe ruta entre el origen y el destino."
    }


def _reconstruir_ruta(padres: dict, destino: tuple) -> list[list[int]]:
    """
    Reconstruye la ruta desde el destino hasta el origen usando el mapa de padres.
    Luego la invierte para obtener el orden correcto origen -> destino.
    """
    ruta = []
    actual = destino

    # Retroceder desde destino hasta origen siguiendo los padres
    while actual is not None:
        ruta.append(list(actual))
        actual = padres[actual]

    # Invertir para obtener origen -> destino
    ruta.reverse()
    return ruta
