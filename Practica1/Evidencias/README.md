# Evidencias de Ejecucion

En esta carpeta se guardan capturas de pantalla o registros de consola que demuestran el funcionamiento del sistema.

## Descripcion de evidencias

### Evidencia 01 - Ejecucion del backend

Se muestra la terminal ejecutando FastAPI mediante Uvicorn en el puerto 8000.
Esto confirma que el backend esta disponible para recibir solicitudes desde el frontend.

![Ejecucion del backend](01_backend_ejecucion.png)

### Evidencia 02 - Ejecucion del frontend

Se muestra la terminal ejecutando Vite en el puerto 5173.
Esto confirma que la interfaz grafica esta disponible para el usuario.

![Ejecucion del frontend](02_frontend_ejecucion.png)

### Evidencia 03 - Listado de ciudades

Se muestra el endpoint `/ciudades` respondiendo con las ciudades definidas en Prolog.
Esto confirma la comunicacion entre Python y el archivo `.pl` mediante PySwip.

![Listado de ciudades](03_ciudades_backend.png)

### Evidencia 04 - Ruta mas corta

Se muestra la consulta de una ciudad origen y una ciudad destino.
El sistema devuelve la ruta recomendada y la distancia total recorrida.

![Ruta mas corta](04_ruta_mas_corta.png)

### Evidencia 05 - Todas las rutas

Se muestra el listado de rutas posibles entre dos ciudades.
Cada ruta incluye su distancia total y se presenta ordenada de menor a mayor distancia.

![Todas las rutas](05_todas_las_rutas.png)

### Evidencia 06 - Agregar ciudad

Se muestra el registro exitoso de una nueva ciudad desde la interfaz.
Esto confirma que el sistema permite administrar la base de conocimiento.

![Agregar ciudad](06_agregar_ciudad.png)

### Evidencia 07 - Agregar conexion

Se muestra el registro exitoso de una nueva conexion con distancia.
Esto confirma que el sistema permite agregar nuevas relaciones entre ciudades.

![Agregar conexion](07_agregar_conexion.png)

## Comandos

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
