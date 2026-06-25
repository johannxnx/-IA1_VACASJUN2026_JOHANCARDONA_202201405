// ============================================================
// api.js - Capa de comunicación con el backend FastAPI
// Contiene todas las funciones que hacen peticiones HTTP.
// El resto de la app no llama a fetch() directamente.
// ============================================================

// URL base del backend. Cambiar si el servidor corre en otro puerto.
const API_BASE = "http://localhost:8000/api";

/**
 * Ejecuta un algoritmo de búsqueda (BFS o DFS) en el backend.
 *
 * @param {number[][]} grid      - Matriz 2D del laberinto (0=libre, 1=pared)
 * @param {number[]}   start     - Posición de inicio [fila, col]
 * @param {number[]}   end       - Posición destino [fila, col]
 * @param {string}     algorithm - "bfs" o "dfs"
 * @returns {Promise<Object>}    - Respuesta del backend con resultados
 */
async function apiSearch(grid, start, end, algorithm) {
  const response = await fetch(`${API_BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid, start, end, algorithm }),
  });

  // Si el servidor retorna un error HTTP, lanzar excepción con el detalle
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Error desconocido en el servidor.");
  }

  return response.json();
}

/**
 * Obtiene la lista completa de laberintos predefinidos del servidor.
 *
 * @returns {Promise<Array>} - Array de objetos PredefinedMaze
 */
async function apiGetMazes() {
  const response = await fetch(`${API_BASE}/mazes`);

  if (!response.ok) {
    throw new Error("No se pudieron cargar los laberintos predefinidos.");
  }

  return response.json();
}

/**
 * Obtiene un laberinto predefinido específico por su ID.
 *
 * @param {number} id - ID del laberinto
 * @returns {Promise<Object>} - Objeto PredefinedMaze
 */
async function apiGetMazeById(id) {
  const response = await fetch(`${API_BASE}/mazes/${id}`);

  if (!response.ok) {
    throw new Error(`Laberinto con ID ${id} no encontrado.`);
  }

  return response.json();
}
