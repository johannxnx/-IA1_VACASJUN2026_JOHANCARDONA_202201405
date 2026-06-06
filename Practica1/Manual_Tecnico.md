# Manual Tecnico

## Practica 1 - Ruta mas corta entre ciudades

### Estudiante

Johan Moises Cardona Rosales - 202201405

## 1. Introduccion

Este manual describe la arquitectura implementada, la estructura del proyecto, la integracion entre Python y Prolog, los endpoints del backend y posibles mejoras futuras del sistema.

El proyecto resuelve el problema de busqueda de rutas entre ciudades utilizando programacion logica. La logica de busqueda, calculo de distancias y seleccion de ruta mas corta se mantiene en Prolog, mientras que Python funciona como capa de integracion.

## 2. Tecnologias utilizadas

### Frontend

- React.
- Vite.
- JavaScript.
- HTML5.
- CSS3.
- Lucide React para iconos.

### Backend

- Python 3.11.
- FastAPI.
- Uvicorn.
- Pydantic.

### Motor logico

- SWI-Prolog.

### Comunicacion Python-Prolog

- PySwip.

## 3. Arquitectura implementada

El sistema utiliza una arquitectura hibrida dividida en tres capas principales:

```text
Frontend (React + Vite)
        |
        | HTTP / JSON
        v
Backend API (FastAPI)
        |
        | PySwip
        v
Motor logico SWI-Prolog (.pl)
```

### 3.1 Frontend

El frontend es responsable de:

- Mostrar la interfaz grafica.
- Solicitar ciudad origen y destino.
- Enviar peticiones HTTP al backend.
- Mostrar rutas y distancias.
- Mostrar mensajes de exito o error.
- Permitir agregar ciudades y conexiones.

El frontend no calcula rutas.

### 3.2 Backend

El backend es responsable de:

- Exponer endpoints HTTP.
- Validar datos de entrada.
- Normalizar nombres de ciudades.
- Ejecutar consultas hacia Prolog.
- Convertir respuestas de Prolog a JSON.
- Enviar respuestas al frontend.

El backend no implementa el algoritmo de busqueda de rutas.

### 3.3 Prolog

Prolog es responsable de:

- Representar ciudades mediante hechos.
- Representar conexiones mediante hechos.
- Buscar rutas entre ciudades.
- Evitar ciclos.
- Calcular distancia total.
- Determinar la ruta mas corta.

## 4. Patron de arquitectura del backend

El backend implementa una arquitectura por capas.

```text
main.py
  |
  v
services/rutas_service.py
  |
  v
integrations/prolog_client.py
  |
  v
prolog/rutas.pl
```

### Capa de rutas

Archivo:

```text
backend/app/main.py
```

Define la aplicacion FastAPI, configura CORS y expone los endpoints del sistema.

### Capa de modelos

Archivo:

```text
backend/app/models.py
```

Define los modelos de entrada y salida usando Pydantic.

### Capa de servicios

Archivo:

```text
backend/app/services/rutas_service.py
```

Coordina las operaciones solicitadas por los endpoints y delega la comunicacion con Prolog.

### Capa de integracion Prolog

Archivo:

```text
backend/app/integrations/prolog_client.py
```

Carga el archivo Prolog, ejecuta consultas mediante PySwip y transforma los resultados al formato que espera el backend.

## 5. Estructura del proyecto

```text
Practica1/
|-- README
|-- Manual_Usuario.md
|-- Manual_Tecnico.md
|-- backend/
|   |-- requirements.txt
|   |-- README.md
|   |-- app/
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- models.py
|   |   |-- integrations/
|   |   |   |-- __init__.py
|   |   |   |-- prolog_client.py
|   |   |-- services/
|   |   |   |-- __init__.py
|   |   |   |-- rutas_service.py
|-- frontend/
|   |-- package.json
|   |-- index.html
|   |-- README.md
|   |-- src/
|   |   |-- api.js
|   |   |-- main.jsx
|   |   |-- styles.css
|-- prolog/
|   |-- rutas.pl
|   |-- README.md
|-- Evidencias/
|   |-- README.md
|   |-- 01_backend_ejecucion.png
|   |-- 02_frontend_ejecucion.png
|   |-- 03_ciudades_backend.png
|   |-- 04_ruta_mas_corta.png
|   |-- 05_todas_las_rutas.png
|   |-- 06_agregar_ciudad.png
|   |-- 07_agregar_conexion.png
```

## 6. Archivo Prolog

Archivo principal:

```text
prolog/rutas.pl
```

Contenido implementado:

- `ciudad/1`: define ciudades disponibles.
- `conexion/3`: define conexiones entre ciudades y distancia.
- `carretera/3`: permite tratar conexiones como bidireccionales.
- `ruta/4`: busca una ruta entre origen y destino.
- `buscar_ruta/5`: regla auxiliar recursiva para construir rutas sin ciclos.
- `todas_rutas/3`: obtiene todas las rutas ordenadas por distancia.
- `ruta_mas_corta/4`: obtiene la primera ruta de la lista ordenada.
- `agregar_ciudad/1`: agrega una ciudad dinamicamente.
- `agregar_conexion/3`: agrega una conexion dinamicamente.

Ejemplo de consulta Prolog:

```prolog
ruta_mas_corta(guatemala, puerto_barrios, Ruta, Distancia).
```

Resultado esperado:

```text
Ruta = [guatemala, zacapa, puerto_barrios]
Distancia = 320
```

## 7. Integracion Python-Prolog

La integracion se realiza con PySwip.

Fragmento base:

```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult("prolog/rutas.pl")
```

En el proyecto, esta logica se encuentra encapsulada en:

```text
backend/app/integrations/prolog_client.py
```

El backend convierte las entradas del usuario a atomos validos de Prolog. Por ejemplo:

```text
San Jose -> san_jose
Puerto Barrios -> puerto_barrios
```

Esto evita errores de consulta y reduce el riesgo de inyeccion de codigo Prolog.

## 8. Endpoints del backend

### GET `/`

Verifica que el backend este funcionando.

Respuesta:

```json
{
  "mensaje": "Backend de rutas funcionando."
}
```

### GET `/ciudades`

Obtiene la lista de ciudades cargadas en Prolog.

Respuesta:

```json
{
  "ciudades": ["guatemala", "antigua", "zacapa"]
}
```

### POST `/ruta-corta`

Consulta la ruta mas corta entre dos ciudades.

Cuerpo:

```json
{
  "origen": "guatemala",
  "destino": "puerto_barrios"
}
```

Respuesta:

```json
{
  "ruta": ["guatemala", "zacapa", "puerto_barrios"],
  "distancia": 320
}
```

### POST `/todas-rutas`

Consulta todas las rutas posibles entre dos ciudades.

Cuerpo:

```json
{
  "origen": "guatemala",
  "destino": "puerto_barrios"
}
```

Respuesta:

```json
{
  "rutas": [
    {
      "ruta": ["guatemala", "zacapa", "puerto_barrios"],
      "distancia": 320
    }
  ]
}
```

### POST `/agregar-ciudad`

Agrega una ciudad a la base de conocimiento en memoria.

Cuerpo:

```json
{
  "ciudad": "jalapa"
}
```

Respuesta:

```json
{
  "mensaje": "Ciudad agregada correctamente."
}
```

### POST `/agregar-conexion`

Agrega una conexion entre dos ciudades existentes.

Cuerpo:

```json
{
  "origen": "jalapa",
  "destino": "guatemala",
  "distancia": 100
}
```

Respuesta:

```json
{
  "mensaje": "Conexion agregada correctamente."
}
```

## 9. Configuracion CORS

El backend configura CORS para permitir peticiones desde Vite:

```text
http://127.0.0.1:5173
http://localhost:5173
```

Esto permite que el frontend consuma la API local sin bloqueos del navegador.

## 10. Instalacion tecnica

### Backend

```powershell
cd "C:\Users\jmcr3\Desktop\VacasJunio-26\LAB IA\-IA1_VACASJUN2026_JOHANCARDONA_202201405\Practica1"
pip install -r backend/requirements.txt
```

### Frontend

```powershell
cd "C:\Users\jmcr3\Desktop\VacasJunio-26\LAB IA\-IA1_VACASJUN2026_JOHANCARDONA_202201405\Practica1\frontend"
npm install
```

## 11. Ejecucion tecnica

### Backend

```powershell
cd "C:\Users\jmcr3\Desktop\VacasJunio-26\LAB IA\-IA1_VACASJUN2026_JOHANCARDONA_202201405\Practica1"
python -m uvicorn backend.app.main:app --reload
```

### Frontend

```powershell
cd "C:\Users\jmcr3\Desktop\VacasJunio-26\LAB IA\-IA1_VACASJUN2026_JOHANCARDONA_202201405\Practica1\frontend"
npm run dev
```

## 12. Validaciones implementadas

El sistema valida:

- Que la ciudad no este vacia.
- Que el origen y destino sean cadenas de texto.
- Que la distancia sea mayor a cero.
- Que los nombres se conviertan a atomos validos.
- Que una ciudad no se repita dentro de una ruta.
- Que Prolog sea el encargado de resolver la busqueda.

## 13. Restricciones cumplidas

- La logica de busqueda esta en Prolog.
- Python solo actua como integrador.
- No se usa base de datos.
- Las rutas evitan ciclos.
- La distancia total se calcula en Prolog.
- La ruta mas corta se selecciona desde los resultados generados en Prolog.

## 14. Evidencias relacionadas

Las capturas se encuentran en la carpeta:

```text
Evidencias/
```

Capturas principales:

- `01_backend_ejecucion.png`: backend ejecutandose.
- `02_frontend_ejecucion.png`: frontend ejecutandose.
- `03_ciudades_backend.png`: endpoint `/ciudades`.
- `04_ruta_mas_corta.png`: consulta de ruta mas corta.
- `05_todas_las_rutas.png`: consulta de todas las rutas.
- `06_agregar_ciudad.png`: registro de ciudad.
- `07_agregar_conexion.png`: registro de conexion.

## 15. Posibles mejoras futuras

- Guardar ciudades y conexiones en un archivo Prolog actualizado.
- Agregar pruebas automatizadas para endpoints.
- Agregar pruebas automatizadas para reglas Prolog.
- Mostrar graficamente el mapa de ciudades.
- Exportar resultados a PDF o CSV.
- Permitir eliminar ciudades o conexiones.
- Agregar autenticacion para administrar datos.
- Mejorar el manejo visual de errores.
- Agregar historial de consultas.
