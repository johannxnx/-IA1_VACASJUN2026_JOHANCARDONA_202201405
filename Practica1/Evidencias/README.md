# Evidencias de Ejecucion

En esta carpeta se deben guardar capturas de pantalla o registros de consola que demuestren el funcionamiento del sistema.

## Formato recomendado

Guardar las imagenes con nombres numerados para que sea facil revisarlas:

```text
01_backend_ejecucion.png
02_frontend_ejecucion.png
03_ciudades_backend.png
04_ruta_mas_corta.png
05_todas_las_rutas.png
06_agregar_ciudad.png
07_agregar_conexion.png
08_validacion_sin_ruta.png
```

## Checklist de evidencias

| No. | Archivo sugerido | Que debe mostrar | Por que es importante |
| --- | --- | --- | --- |
| 1 | `01_backend_ejecucion.png` | Terminal con FastAPI ejecutandose en `http://127.0.0.1:8000` | Demuestra que el backend funciona |
| 2 | `02_frontend_ejecucion.png` | Terminal con Vite ejecutandose en `http://127.0.0.1:5173` | Demuestra que el frontend funciona |
| 3 | `03_ciudades_backend.png` | Navegador en `/ciudades` mostrando la lista de ciudades | Demuestra conexion Python-Prolog |
| 4 | `04_ruta_mas_corta.png` | Interfaz mostrando ruta mas corta y distancia total | Demuestra la funcionalidad principal |
| 5 | `05_todas_las_rutas.png` | Interfaz mostrando varias rutas posibles ordenadas por distancia | Demuestra busqueda multiple de rutas |
| 6 | `06_agregar_ciudad.png` | Interfaz mostrando mensaje de ciudad agregada | Demuestra administracion de ciudades |
| 7 | `07_agregar_conexion.png` | Interfaz mostrando mensaje de conexion agregada | Demuestra administracion de conexiones |
| 8 | `08_validacion_sin_ruta.png` | Mensaje cuando no existe ruta o cuando hay datos invalidos | Demuestra manejo de errores |

## Descripcion sugerida para el informe

Se recomienda acompanar cada captura con una descripcion breve como esta:

```text
Evidencia 01 - Ejecucion del backend
Se muestra la terminal ejecutando FastAPI mediante Uvicorn en el puerto 8000.
Esto confirma que el backend esta disponible para recibir solicitudes desde el frontend.
```

```text
Evidencia 02 - Ejecucion del frontend
Se muestra la terminal ejecutando Vite en el puerto 5173.
Esto confirma que la interfaz grafica esta disponible para el usuario.
```

```text
Evidencia 03 - Listado de ciudades
Se muestra el endpoint /ciudades respondiendo con las ciudades definidas en Prolog.
Esto confirma la comunicacion entre Python y el archivo .pl mediante PySwip.
```

```text
Evidencia 04 - Ruta mas corta
Se muestra la consulta de una ciudad origen y una ciudad destino.
El sistema devuelve la ruta recomendada y la distancia total recorrida.
```

```text
Evidencia 05 - Todas las rutas
Se muestra el listado de rutas posibles entre dos ciudades.
Cada ruta incluye su distancia total y se presenta ordenada de menor a mayor distancia.
```

```text
Evidencia 06 - Agregar ciudad
Se muestra el registro exitoso de una nueva ciudad desde la interfaz.
Esto confirma que el sistema permite administrar la base de conocimiento.
```

```text
Evidencia 07 - Agregar conexion
Se muestra el registro exitoso de una nueva conexion con distancia.
Esto confirma que el sistema permite agregar nuevas relaciones entre ciudades.
```

```text
Evidencia 08 - Manejo de errores
Se muestra un caso donde el sistema informa claramente que no puede completar una operacion.
Esto confirma que existen validaciones y mensajes para el usuario.
```

## Comandos utiles para generar evidencias

Levantar backend:

```powershell
cd "C:\Users\jmcr3\Desktop\VacasJunio-26\LAB IA\-IA1_VACASJUN2026_JOHANCARDONA_202201405\Practica1"
python -m uvicorn backend.app.main:app --reload
```

Levantar frontend:

```powershell
cd "C:\Users\jmcr3\Desktop\VacasJunio-26\LAB IA\-IA1_VACASJUN2026_JOHANCARDONA_202201405\Practica1\frontend"
npm run dev
```

Endpoints utiles:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/ciudades
http://127.0.0.1:5173/
```
