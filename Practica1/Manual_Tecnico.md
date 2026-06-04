# Manual Tecnico

## Practica 1 - Ruta mas corta entre ciudades

Este documento describe la arquitectura tecnica propuesta para el sistema, la estructura del proyecto y la integracion entre Python y Prolog.

## Arquitectura

El sistema utiliza una arquitectura hibrida:

```text
Frontend (React + Vite)
        |
        | HTTP
        v
Backend API (FastAPI)
        |
        | PySwip
        v
SWI-Prolog (.pl)
```

## Patron de arquitectura del backend

Se propone una arquitectura por capas:

- Rutas: endpoints expuestos con FastAPI.
- Servicios: validacion de datos y coordinacion de operaciones.
- Integracion Prolog: ejecucion de consultas mediante PySwip.

Esta estructura permite separar responsabilidades y mantener la logica de busqueda exclusivamente en Prolog.

## Estructura del proyecto

```text
Practica1/
|-- README
|-- Manual_Usuario.md
|-- Manual_Tecnico.md
|-- backend/
|-- frontend/
|-- prolog/
|-- Evidencias/
```

## Backend

El backend debe encargarse de:

- Recibir solicitudes HTTP desde el frontend.
- Validar datos de entrada.
- Consultar el archivo Prolog mediante PySwip.
- Retornar respuestas en formato JSON.

Endpoints propuestos:

```text
GET  /ciudades
POST /ruta-corta
POST /todas-rutas
POST /agregar-ciudad
POST /agregar-conexion
```

## Frontend

El frontend debe encargarse de:

- Mostrar formularios de seleccion o ingreso de ciudades.
- Enviar solicitudes HTTP al backend.
- Mostrar rutas encontradas.
- Mostrar distancias calculadas.
- Permitir agregar ciudades y conexiones.

## Prolog

El archivo Prolog debe contener:

- Hechos para representar ciudades.
- Hechos para representar conexiones y distancias.
- Reglas para encontrar rutas.
- Reglas para evitar ciclos.
- Reglas para calcular distancia total.
- Regla para determinar la ruta mas corta.

La logica de busqueda y optimizacion no debe implementarse en Python.

## Integracion Python - Prolog

La comunicacion se realizara mediante PySwip.

Ejemplo base:

```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult("prolog/rutas.pl")
```

## Mejoras futuras

- Mostrar estadisticas de rutas.
- Ordenar rutas de menor a mayor distancia.
- Mejorar la visualizacion de resultados.
- Agregar validaciones mas completas.
- Exportar resultados de busqueda.
- Agregar pruebas automatizadas para backend y reglas Prolog.
