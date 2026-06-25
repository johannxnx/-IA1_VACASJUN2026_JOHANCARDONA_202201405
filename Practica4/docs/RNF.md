# Requerimientos No Funcionales — RoboMaze
**Práctica 4 | Inteligencia Artificial 1**  
**Universidad San Carlos de Guatemala — Facultad de Ingeniería**  
**Estudiante:** Johan Cardona | **Carné:** 202201405

---

## Descripción

Los requerimientos no funcionales describen los atributos de calidad del sistema RoboMaze. No definen qué hace el sistema, sino **cómo** lo hace: su rendimiento, facilidad de uso, mantenibilidad, seguridad y capacidad de crecimiento.

---

## Rendimiento

| ID | Descripción | Criterio de aceptación |
|----|-------------|----------------------|
| RNF-01 | El backend debe responder a las peticiones de búsqueda en un tiempo razonable. | Tiempo de respuesta menor a 500 ms para laberintos de hasta 15x15 celdas. |
| RNF-02 | La medición del tiempo de ejecución de los algoritmos debe ser de alta precisión. | Se utiliza `time.perf_counter()` con resolución de nanosegundos, resultado expresado en milisegundos con 4 decimales. |
| RNF-03 | La visualización de nodos explorados y ruta no debe bloquear la interfaz. | Las animaciones usan `setTimeout` escalonado para no congelar el hilo principal del navegador. |
| RNF-04 | Las comparaciones BFS y DFS deben ejecutarse en paralelo. | El frontend usa `Promise.all()` para lanzar ambas peticiones simultáneamente, reduciendo el tiempo de espera total. |

---

## Usabilidad

| ID | Descripción | Criterio de aceptación |
|----|-------------|----------------------|
| RNF-05 | La interfaz debe ser intuitiva y no requerir documentación para operaciones básicas. | Un usuario puede crear un laberinto, ejecutar una búsqueda y ver resultados en menos de 2 minutos sin leer el manual. |
| RNF-06 | Los modos de edición de la cuadrícula deben ser visualmente distinguibles. | El botón de modo activo resalta con color diferente al resto. |
| RNF-07 | El estado de la búsqueda debe comunicarse claramente al usuario. | Se muestra un loader durante la petición al backend y un mensaje de color verde (éxito) o rojo (sin ruta) al finalizar. |
| RNF-08 | La leyenda de colores debe estar visible en todo momento. | La leyenda permanece fija en el panel lateral durante toda la sesión. |
| RNF-09 | Los resultados numéricos deben presentarse con unidades claras. | El tiempo se muestra en "ms", la longitud en "celdas" y los nodos en cantidad entera. |

---

## Mantenibilidad

| ID | Descripción | Criterio de aceptación |
|----|-------------|----------------------|
| RNF-10 | El código debe seguir el patrón de arquitectura por capas. | Las responsabilidades están separadas en: rutas (routes), servicios (services) y algoritmos (algorithms), sin mezcla de lógica entre capas. |
| RNF-11 | Cada archivo debe tener una responsabilidad única y bien definida. | Ningún archivo supera las 200 líneas de código. Cada módulo tiene una función específica documentada. |
| RNF-12 | El código debe estar comentado para facilitar su comprensión. | Cada función cuenta con docstring descriptivo. Los bloques no evidentes tienen comentarios de línea. |
| RNF-13 | Agregar un nuevo algoritmo de búsqueda no debe requerir modificar el frontend ni las rutas. | Solo se necesita crear un nuevo archivo en `algorithms/` y registrarlo en `maze_service.py`. |

---

## Escalabilidad

| ID | Descripción | Criterio de aceptación |
|----|-------------|----------------------|
| RNF-14 | El sistema debe soportar laberintos de distintos tamaños sin cambios en el código. | La cuadrícula acepta cualquier tamaño entre 3x3 y 15x15 sin modificaciones al backend. |
| RNF-15 | La lista de laberintos predefinidos debe ser extensible sin afectar otros módulos. | Agregar un nuevo laberinto predefinido solo requiere añadir un objeto a la lista `LABERINTOS_PREDEFINIDOS` en `maze_service.py`. |
| RNF-16 | La API REST debe poder extenderse con nuevos endpoints sin reestructurar el proyecto. | FastAPI usa routers modulares; un nuevo grupo de endpoints se registra añadiendo un router en `main.py`. |

---

## Seguridad

| ID | Descripción | Criterio de aceptación |
|----|-------------|----------------------|
| RNF-17 | El backend debe validar los datos de entrada antes de procesarlos. | Pydantic valida automáticamente el esquema del request. El servicio valida que el algoritmo sea "bfs" o "dfs". |
| RNF-18 | El sistema no debe exponer información interna en errores al usuario. | Los errores retornan mensajes descriptivos genéricos vía HTTPException, sin stack traces al cliente. |
| RNF-19 | El sistema no debe depender de servicios externos de inteligencia artificial. | Toda la lógica de búsqueda se ejecuta localmente en el backend Python. |

---

## Portabilidad

| ID | Descripción | Criterio de aceptación |
|----|-------------|----------------------|
| RNF-20 | El sistema debe funcionar en los principales sistemas operativos. | Probado y funcional en Windows 10/11, con compatibilidad declarada para Linux y macOS mediante Python 3.11+. |
| RNF-21 | El frontend no debe requerir instalación de herramientas adicionales. | Solo requiere un navegador web actualizado. No depende de Node.js, bundlers ni frameworks de JS. |
| RNF-22 | Las dependencias del backend deben estar declaradas explícitamente. | El archivo `requirements.txt` lista todas las dependencias con versión fija para garantizar reproducibilidad. |

---

## Disponibilidad

| ID | Descripción | Criterio de aceptación |
|----|-------------|----------------------|
| RNF-23 | El sistema no debe depender de bases de datos para funcionar. | Todo el estado del laberinto se gestiona en memoria durante la sesión. No se usa ningún motor de base de datos. |
| RNF-24 | El sistema debe manejar errores de conexión entre frontend y backend de forma controlada. | Si el backend no responde, el frontend muestra un mensaje de error descriptivo al usuario en lugar de fallar silenciosamente. |
