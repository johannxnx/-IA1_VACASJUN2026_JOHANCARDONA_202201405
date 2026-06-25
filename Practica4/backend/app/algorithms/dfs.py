# ============================================================
# dfs.py - Algoritmo Depth-First Search (DFS)
# Búsqueda en profundidad: explora tan lejos como sea posible
# antes de retroceder. NO garantiza el camino más corto.
# ============================================================

import time


def dfs(grid: list[list[int]], start: list[int], end: list[int]) -> dict:
    """
    Ejecuta DFS sobre una cuadrícula 2D para encontrar una ruta al destino.

    Estrategia:
        Usa una pila (LIFO) para explorar en profundidad primero.
        Puede encontrar rutas más largas que BFS pero usa menos memoria
        en promedio al no almacenar todos los niveles simultáneamente.

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

    # Pila DFS: cada elemento es la posición actual (comportamiento LIFO)
    pila = [inicio]

    # Registro de celdas visitadas
    visitados = set()
    visitados.add(inicio)

    # Mapa de padres para reconstruir la ruta al encontrar el destino
    padres = {inicio: None}

    # Lista de nodos explorados en orden de visita (para visualización)
    explorados = []

    encontrado = False

    while pila:
        # Sacar el último elemento (LIFO = profundidad primero)
        actual = pila.pop()
        explorados.append(list(actual))

        # Si llegamos al destino, terminamos
        if actual == destino:
            encontrado = True
            break

        # Explorar los 4 vecinos: arriba, abajo, izquierda, derecha
        fila, col = actual
        vecinos = [
            (fila - 1, col),  # arriba
            (fila + 1, col),  # abajo
            (fila, col - 1),  # izquierda
            (fila, col + 1),  # derecha
        ]

        for nfila, ncol in vecinos:
            vecino = (nfila, ncol)

            # Validar límites del laberinto
            if not (0 <= nfila < filas and 0 <= ncol < columnas):
                continue

            # Ignorar obstáculos
            if grid[nfila][ncol] == 1:
                continue

            # Ignorar celdas ya visitadas
            if vecino in visitados:
                continue

            # Marcar como visitado y agregar a la pila
            visitados.add(vecino)
            padres[vecino] = actual
            pila.append(vecino)

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
        "message": "Ruta encontrada con DFS." if encontrado else "No existe ruta entre el origen y el destino."
    }


def _reconstruir_ruta(padres: dict, destino: tuple) -> list[list[int]]:
    """
    Reconstruye la ruta desde el destino hasta el origen usando el mapa de padres.
    """
    ruta = []
    actual = destino

    while actual is not None:
        ruta.append(list(actual))
        actual = padres[actual]

    ruta.reverse()
    return ruta
