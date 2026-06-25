// ============================================================
// app.js - Controlador principal de la aplicación RoboMaze
// Conecta la interfaz de usuario con maze.js (cuadrícula)
// y api.js (backend). Maneja eventos y muestra resultados.
// ============================================================

// ===== REFERENCIAS A ELEMENTOS DEL DOM =====
const btnSearch      = document.getElementById("btn-search");
const btnCompare     = document.getElementById("btn-compare");
const btnClearResult = document.getElementById("btn-clear-result");
const btnReset       = document.getElementById("btn-reset");
const btnResize      = document.getElementById("btn-resize");
const algorithmSelect = document.getElementById("algorithm-select");
const inputRows      = document.getElementById("grid-rows");
const inputCols      = document.getElementById("grid-cols");
const loader         = document.getElementById("loader");
const resultsPanel   = document.getElementById("results-panel");
const comparisonTable = document.getElementById("comparison-table");

// ===== INICIALIZACIÓN =====

/**
 * Al cargar la página: inicializar la cuadrícula y cargar laberintos predefinidos.
 */
document.addEventListener("DOMContentLoaded", async () => {
  // Crear cuadrícula vacía inicial
  initMaze(8, 8);

  // Cargar lista de laberintos predefinidos desde el backend
  await loadPredefinedMazeList();

  // Configurar listeners de botones de modo de edición
  document.querySelectorAll(".btn-mode").forEach(btn => {
    btn.addEventListener("click", () => {
      // Quitar clase active de todos los botones de modo
      document.querySelectorAll(".btn-mode").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      setEditMode(btn.dataset.mode);
    });
  });
});

// ===== CARGA DE LABERINTOS PREDEFINIDOS =====

/**
 * Solicita los laberintos predefinidos al backend y genera botones para cada uno.
 */
async function loadPredefinedMazeList() {
  try {
    const mazes = await apiGetMazes();
    const container = document.getElementById("predefined-mazes");
    container.innerHTML = "";

    mazes.forEach(maze => {
      const btn = document.createElement("div");
      btn.classList.add("maze-list-item");
      btn.textContent = `#${maze.id} — ${maze.name}`;
      btn.title = `${maze.grid.length}x${maze.grid[0].length} | Inicio: ${maze.start} → Fin: ${maze.end}`;

      // Al hacer clic, cargar el laberinto en la cuadrícula
      btn.addEventListener("click", () => {
        loadMaze(maze);
        hideResults();
      });

      container.appendChild(btn);
    });
  } catch (err) {
    console.error("Error cargando laberintos:", err);
  }
}

// ===== EVENTO: EJECUTAR BÚSQUEDA =====

btnSearch.addEventListener("click", async () => {
  const { grid, start, end } = getMazeState();
  const algorithm = algorithmSelect.value;

  // Validar que el usuario haya definido inicio y destino
  if (!start || !end) {
    alert("Debes definir un punto de inicio y un punto de destino.");
    return;
  }

  showLoader();
  clearResultVisualization();
  hideResults();

  try {
    // Llamar al backend con el laberinto y el algoritmo seleccionado
    const result = await apiSearch(grid, start, end, algorithm);

    // Mostrar animación de exploración y ruta
    visualizeResult(result.explored, result.path);

    // Mostrar panel de métricas
    showSingleResult(algorithm.toUpperCase(), result);

  } catch (err) {
    alert("Error al conectar con el backend: " + err.message);
  } finally {
    hideLoader();
  }
});

// ===== EVENTO: COMPARAR BFS VS DFS =====

btnCompare.addEventListener("click", async () => {
  const { grid, start, end } = getMazeState();

  if (!start || !end) {
    alert("Debes definir un punto de inicio y un punto de destino.");
    return;
  }

  showLoader();
  clearResultVisualization();
  hideResults();

  try {
    // Ejecutar ambos algoritmos en paralelo
    const [bfsResult, dfsResult] = await Promise.all([
      apiSearch(grid, start, end, "bfs"),
      apiSearch(grid, start, end, "dfs"),
    ]);

    // Mostrar la ruta del algoritmo seleccionado en el selector
    const selected = algorithmSelect.value;
    const resultToShow = selected === "bfs" ? bfsResult : dfsResult;
    visualizeResult(resultToShow.explored, resultToShow.path);

    // Mostrar tabla comparativa
    showComparisonResult(bfsResult, dfsResult);

  } catch (err) {
    alert("Error al comparar algoritmos: " + err.message);
  } finally {
    hideLoader();
  }
});

// ===== EVENTO: LIMPIAR RESULTADO =====

btnClearResult.addEventListener("click", () => {
  clearResultVisualization();
  hideResults();
});

// ===== EVENTO: REINICIAR TODO =====

btnReset.addEventListener("click", () => {
  resetMaze();
  hideResults();
});

// ===== EVENTO: REDIMENSIONAR CUADRÍCULA =====

btnResize.addEventListener("click", () => {
  const rows = parseInt(inputRows.value);
  const cols = parseInt(inputCols.value);

  // Validar rango permitido
  if (rows < 3 || rows > 15 || cols < 3 || cols > 15) {
    alert("El tamaño debe estar entre 3 y 15.");
    return;
  }

  initMaze(rows, cols);
  hideResults();
});

// ===== FUNCIONES DE VISUALIZACIÓN DE RESULTADOS =====

/**
 * Muestra el panel de resultados para un solo algoritmo.
 * Oculta la tabla de comparación.
 */
function showSingleResult(algorithmName, result) {
  document.getElementById("result-title").textContent = `Resultado — ${algorithmName}`;
  document.getElementById("metric-algorithm").textContent = algorithmName;
  document.getElementById("metric-found").textContent = result.found ? "Sí" : "No";
  document.getElementById("metric-path-length").textContent = result.path_length;
  document.getElementById("metric-nodes").textContent = result.nodes_explored;
  // El backend ya retorna el tiempo en milisegundos
  document.getElementById("metric-time").textContent = `${result.execution_time.toFixed(4)} ms`;

  // Mensaje de estado con color según si se encontró ruta o no
  const msg = document.getElementById("result-message");
  msg.textContent = result.message;
  msg.className = "result-message " + (result.found ? "success" : "error");

  comparisonTable.classList.add("hidden");
  resultsPanel.classList.remove("hidden");
}

/**
 * Muestra el panel de resultados con la tabla comparativa BFS vs DFS.
 */
function showComparisonResult(bfs, dfs) {
  document.getElementById("result-title").textContent = "Comparación BFS vs DFS";

  // Ocultar métricas individuales (se usan las de la tabla)
  document.getElementById("metric-algorithm").textContent = "BFS y DFS";
  document.getElementById("metric-found").textContent = "—";
  document.getElementById("metric-path-length").textContent = "—";
  document.getElementById("metric-nodes").textContent = "—";
  document.getElementById("metric-time").textContent = "—";

  // Llenar la tabla comparativa
  document.getElementById("cmp-bfs-found").textContent  = bfs.found ? "Sí" : "No";
  document.getElementById("cmp-dfs-found").textContent  = dfs.found ? "Sí" : "No";
  document.getElementById("cmp-bfs-length").textContent = bfs.path_length;
  document.getElementById("cmp-dfs-length").textContent = dfs.path_length;
  document.getElementById("cmp-bfs-nodes").textContent  = bfs.nodes_explored;
  document.getElementById("cmp-dfs-nodes").textContent  = dfs.nodes_explored;
  document.getElementById("cmp-bfs-time").textContent   = `${bfs.execution_time.toFixed(4)} ms`;
  document.getElementById("cmp-dfs-time").textContent   = `${dfs.execution_time.toFixed(4)} ms`;

  const msg = document.getElementById("result-message");
  msg.textContent = `BFS exploró ${bfs.nodes_explored} nodos | DFS exploró ${dfs.nodes_explored} nodos`;
  msg.className = "result-message";

  comparisonTable.classList.remove("hidden");
  resultsPanel.classList.remove("hidden");
}

// ===== UTILIDADES DE UI =====

function showLoader()  { loader.classList.remove("hidden"); }
function hideLoader()  { loader.classList.add("hidden"); }
function hideResults() { resultsPanel.classList.add("hidden"); }
