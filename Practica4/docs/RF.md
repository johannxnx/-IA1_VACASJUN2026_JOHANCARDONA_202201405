# Requerimientos Funcionales — RoboMaze
**Práctica 4 | Inteligencia Artificial 1**  
**Universidad San Carlos de Guatemala — Facultad de Ingeniería**  
**Estudiante:** Johan Cardona | **Carné:** 202201405

---

## Descripción

Los requerimientos funcionales describen las funcionalidades concretas que el sistema RoboMaze debe realizar. Cada requerimiento define un comportamiento esperado del sistema desde la perspectiva del usuario o del sistema mismo.

---

## Listado de Requerimientos Funcionales

| ID | Nombre | Descripción | Módulo |
|----|--------|-------------|--------|
| RF-01 | Representación del laberinto | El sistema debe representar el laberinto como una cuadrícula bidimensional donde cada celda puede ser libre (0) u obstáculo (1). | Frontend / Backend |
| RF-02 | Definición de punto de inicio | El usuario debe poder seleccionar una celda de la cuadrícula como posición inicial del agente. | Frontend |
| RF-03 | Definición de punto de destino | El usuario debe poder seleccionar una celda de la cuadrícula como posición objetivo del agente. | Frontend |
| RF-04 | Colocación de obstáculos | El usuario debe poder marcar y desmarcar celdas como obstáculos que bloqueen el paso del agente. | Frontend |
| RF-05 | Ejecución de BFS | El sistema debe ejecutar el algoritmo Breadth-First Search sobre el laberinto configurado y retornar la ruta más corta si existe. | Backend |
| RF-06 | Ejecución de DFS | El sistema debe ejecutar el algoritmo Depth-First Search sobre el laberinto configurado y retornar una ruta válida si existe. | Backend |
| RF-07 | Ejecución independiente de algoritmos | El usuario debe poder ejecutar BFS o DFS de forma independiente mediante un selector en la interfaz. | Frontend |
| RF-08 | Visualización de nodos explorados | El sistema debe mostrar gráficamente, mediante color diferenciado, todas las celdas visitadas durante la búsqueda. | Frontend |
| RF-09 | Visualización de la ruta encontrada | El sistema debe destacar visualmente la ruta final encontrada desde el origen hasta el destino. | Frontend |
| RF-10 | Métricas de búsqueda | El sistema debe mostrar la cantidad de nodos explorados, la longitud de la ruta encontrada y el tiempo de ejecución del algoritmo. | Frontend / Backend |
| RF-11 | Comparación de algoritmos | El sistema debe permitir ejecutar BFS y DFS sobre el mismo laberinto simultáneamente y presentar una tabla comparativa de métricas. | Frontend / Backend |
| RF-12 | Manejo de ruta inexistente | El sistema debe informar al usuario cuando no exista una ruta válida entre el punto de inicio y el punto de destino. | Backend / Frontend |
| RF-13 | Laberintos predefinidos | El sistema debe incluir al menos 5 laberintos predefinidos que el usuario pueda cargar con un clic para realizar pruebas. | Backend |
| RF-14 | Redimensionamiento del laberinto | El usuario debe poder modificar el tamaño de la cuadrícula entre 3x3 y 15x15 celdas. | Frontend |
| RF-15 | Limpieza de resultados | El usuario debe poder limpiar la visualización de la búsqueda sin perder la configuración del laberinto. | Frontend |
| RF-16 | Reinicio completo | El usuario debe poder reiniciar completamente la cuadrícula, eliminando obstáculos, inicio, destino y resultados. | Frontend |
| RF-17 | API REST de búsqueda | El sistema debe exponer un endpoint REST que reciba la configuración del laberinto y el algoritmo, y retorne los resultados de búsqueda en formato JSON. | Backend |
| RF-18 | API REST de laberintos | El sistema debe exponer endpoints REST para listar todos los laberintos predefinidos y obtener uno por su ID. | Backend |
| RF-19 | Validación de algoritmo | El backend debe validar que el algoritmo solicitado sea "bfs" o "dfs" y retornar un error descriptivo si no lo es. | Backend |
| RF-20 | Modos de edición de la cuadrícula | La interfaz debe ofrecer modos de edición claramente diferenciados: Obstáculo, Inicio, Destino y Limpiar. | Frontend |

---

