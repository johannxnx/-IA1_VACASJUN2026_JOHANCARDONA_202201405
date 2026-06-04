# Backend

Backend propuesto para la practica, desarrollado con Python 3.11 y FastAPI.

## Responsabilidad

- Exponer endpoints HTTP.
- Validar datos recibidos desde el frontend.
- Ejecutar consultas hacia Prolog mediante PySwip.
- Retornar resultados al frontend.

## Endpoints propuestos

```text
GET  /ciudades
POST /ruta-corta
POST /todas-rutas
POST /agregar-ciudad
POST /agregar-conexion
```

## Instalacion

Desde la carpeta `Practica1`:

```bash
pip install -r backend/requirements.txt
```

## Ejecucion

Desde la carpeta `Practica1`:

```bash
uvicorn backend.app.main:app --reload
```

La documentacion automatica estara disponible en:

```text
http://127.0.0.1:8000/docs
```

## Estructura

```text
backend/
|-- app/
|   |-- main.py
|   |-- models.py
|   |-- integrations/
|   |   |-- prolog_client.py
|   |-- services/
|   |   |-- rutas_service.py
|-- requirements.txt
|-- README.md
```

## Restriccion principal

El backend no debe implementar la logica de busqueda de rutas. Esa logica debe permanecer en Prolog.
