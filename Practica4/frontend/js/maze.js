// ============================================================
// maze.js - Lógica de la cuadrícula del laberinto
// Gestiona el estado interno del laberinto, el renderizado
// de la cuadrícula y la visualización de resultados.
// ============================================================

// ===== ESTADO DEL LABERINTO =====
const MazeState = {
  rows: 8,          // Número de filas actual
  cols: 8,          // Número de columnas actual
  grid: [],         // Matriz 2D: 0=libre, 1=pared
  start: null,      // [fila, col] del punto de inicio
  end: null,        // [fila, col] del punto destino
  editMode: "wall", // Modo de edición activo del usuario
};

// ===== INICIALIZACIÓN DE LA CUADRÍCULA =====

/**
 * Inicializa el laberinto con una cuadrícula vacía de tamaño rows x cols.
 * Limpia el estado previo (inicio, destino, paredes).
 */
function initMaze(rows = MazeState.rows, cols = MazeState.cols) {
  MazeState.rows = rows;
  MazeState.cols = cols;
  MazeState.start = null;
  MazeState.end = null;

  // Crear matriz 2D llena de ceros (celdas libres)
  MazeState.grid = Array.from({ length: rows }, () => Array(cols).fill(0));

  renderGrid();
}

/**
 * Carga un laberinto predefinido en el estado y lo renderiza.
 *
 * @param {Object} maze - Objeto PredefinedMaze con grid, start y end
 */
function loadMaze(maze) {
  MazeState.rows = maze.grid.length;
  MazeState.cols = maze.grid[0].length;

  // Copia profunda de la cuadrícula para evitar mutar el original
  MazeState.grid = maze.grid.map(row => [...row]);
  MazeState.start = maze.start;
  MazeState.end = maze.end;

  renderGrid();
}

// ===== RENDERIZADO DE LA CUADRÍCULA =====

/**
 * Renderiza la cuadrícula completa en el DOM.
 * Crea un elemento <div class="cell"> por cada celda.
 */
function renderGrid() {
  const container = document.getElementById("maze-grid");
  container.innerHTML = ""; // Limpiar contenido previo

  // Definir columnas CSS dinámicamente según el número de columnas
  container.style.gridTemplateColumns = `repeat(${MazeState.cols}, 40px)`;

  for (let r = 0; r < MazeState.rows; r++) {
    for (let c = 0; c < MazeState.cols; c++) {
      const cell = document.createElement("div");
      cell.classList.add("cell");
      cell.dataset.row = r;
      cell.dataset.col = c;

      // Aplicar clase visual según el tipo de celda
      applyCellClass(cell, r, c);

      // Evento de clic: modificar celda según el modo activo
      cell.addEventListener("click", () => onCellClick(r, c));

      container.appendChild(cell);
    }
  }
}

/**
 * Aplica la clase CSS correcta a una celda según su estado actual.
 * El orden de prioridad es: start > end > wall > free.
 */
function applyCellClass(cell, r, c) {
  // Limpiar clases de estado anteriores
  cell.classList.remove("wall", "start", "end", "explored", "path");

  if (MazeState.start && MazeState.start[0] === r && MazeState.start[1] === c) {
    cell.classList.add("start");
  } else if (MazeState.end && MazeState.end[0] === r && MazeState.end[1] === c) {
    cell.classList.add("end");
  } else if (MazeState.grid[r][c] === 1) {
    cell.classList.add("wall");
  }
}

// ===== MANEJO DE CLICS EN CELDAS =====

/**
 * Procesa el clic del usuario sobre una celda según el modo activo.
 */
function onCellClick(r, c) {
  const mode = MazeState.editMode;

  if (mode === "wall") {
    // Alternar entre pared y libre (no afectar inicio/destino)
    if (isStartOrEnd(r, c)) return;
    MazeState.grid[r][c] = MazeState.grid[r][c] === 1 ? 0 : 1;

  } else if (mode === "start") {
    // Limpiar la celda anterior de inicio
    if (MazeState.start) {
      MazeState.grid[MazeState.start[0]][MazeState.start[1]] = 0;
    }
    MazeState.start = [r, c];
    MazeState.grid[r][c] = 0; // La celda de inicio no puede ser pared

  } else if (mode === "end") {
    // Limpiar la celda anterior de destino
    if (MazeState.end) {
      MazeState.grid[MazeState.end[0]][MazeState.end[1]] = 0;
    }
    MazeState.end = [r, c];
    MazeState.grid[r][c] = 0;

  } else if (mode === "clear") {
    // Limpiar la celda: si era inicio/destino, eliminar la referencia
    if (MazeState.start && MazeState.start[0] === r && MazeState.start[1] === c) {
      MazeState.start = null;
    } else if (MazeState.end && MazeState.end[0] === r && MazeState.end[1] === c) {
      MazeState.end = null;
    }
    MazeState.grid[r][c] = 0;
  }

  // Re-renderizar solo la celda modificada (más eficiente que renderizar todo)
  updateCell(r, c);
}

/**
 * Actualiza visualmente una celda específica sin re-renderizar toda la cuadrícula.
 */
function updateCell(r, c) {
  const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
  if (cell) applyCellClass(cell, r, c);
}

/**
 * Verifica si una celda [r, c] es la posición de inicio o destino.
 */
function isStartOrEnd(r, c) {
  return (
    (MazeState.start && MazeState.start[0] === r && MazeState.start[1] === c) ||
    (MazeState.end && MazeState.end[0] === r && MazeState.end[1] === c)
  );
}

// ===== VISUALIZACIÓN DE RESULTADOS =====

/**
 * Limpia las marcas visuales de exploración y ruta sin tocar paredes ni inicio/destino.
 */
function clearResultVisualization() {
  document.querySelectorAll(".cell.explored, .cell.path").forEach(cell => {
    const r = parseInt(cell.dataset.row);
    const c = parseInt(cell.dataset.col);
    applyCellClass(cell, r, c);
  });
}

/**
 * Muestra visualmente los nodos explorados y la ruta encontrada.
 * Usa un delay escalonado para animar la aparición celda por celda.
 *
 * @param {number[][]} explored - Celdas visitadas durante la búsqueda
 * @param {number[][]} path     - Celdas de la ruta final
 */
function visualizeResult(explored, path) {
  clearResultVisualization();

  const DELAY_EXPLORED = 30; // ms entre cada nodo explorado
  const DELAY_PATH = 60;     // ms entre cada nodo de la ruta

  // Primero mostrar nodos explorados (color morado)
  explored.forEach(([r, c], i) => {
    setTimeout(() => {
      const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
      if (cell && !isStartOrEnd(r, c)) {
        cell.classList.remove("wall", "free");
        cell.classList.add("explored");
      }
    }, i * DELAY_EXPLORED);
  });

  // Luego mostrar la ruta (color amarillo), después de que terminen los explorados
  const pathDelay = explored.length * DELAY_EXPLORED + 100;
  path.forEach(([r, c], i) => {
    setTimeout(() => {
      const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
      if (cell && !isStartOrEnd(r, c)) {
        cell.classList.remove("explored");
        cell.classList.add("path");
      }
    }, pathDelay + i * DELAY_PATH);
  });
}

/**
 * Resetea la cuadrícula por completo: elimina paredes, inicio, destino y resultados.
 */
function resetMaze() {
  initMaze(MazeState.rows, MazeState.cols);
}

/**
 * Retorna el estado actual del laberinto (para enviarlo a la API).
 */
function getMazeState() {
  return {
    grid: MazeState.grid,
    start: MazeState.start,
    end: MazeState.end,
  };
}

/**
 * Cambia el modo de edición activo.
 * @param {string} mode - "wall" | "start" | "end" | "clear"
 */
function setEditMode(mode) {
  MazeState.editMode = mode;
}
