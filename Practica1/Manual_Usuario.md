# Manual de Usuario

## Practica 1 - Ruta mas corta entre ciudades

Este manual explica como utilizar el sistema para consultar rutas entre ciudades.

## Requisitos previos

Antes de utilizar el sistema se debe contar con:

- Python 3.11 o superior.
- SWI-Prolog instalado.
- Node.js instalado.
- Backend ejecutandose correctamente.
- Frontend ejecutandose correctamente.

## Inicio del sistema

1. Ejecutar el backend desarrollado con FastAPI.
2. Ejecutar el frontend desarrollado con React y Vite.
3. Abrir la aplicacion web en el navegador.

## Consulta de ruta mas corta

1. Seleccionar o ingresar la ciudad de origen.
2. Seleccionar o ingresar la ciudad destino.
3. Presionar la opcion para consultar la ruta mas corta.
4. Revisar la ruta recomendada y la distancia total mostrada por el sistema.

## Consulta de todas las rutas

1. Seleccionar o ingresar la ciudad de origen.
2. Seleccionar o ingresar la ciudad destino.
3. Presionar la opcion para mostrar todas las rutas.
4. Revisar el listado de rutas disponibles y sus distancias.

## Agregar una ciudad

1. Ingresar el nombre de la nueva ciudad.
2. Enviar el formulario.
3. Verificar que la ciudad aparezca disponible para futuras consultas.

## Agregar una conexion

1. Seleccionar o ingresar la ciudad de origen.
2. Seleccionar o ingresar la ciudad destino.
3. Ingresar la distancia entre ambas ciudades.
4. Enviar el formulario.
5. Verificar que la nueva conexion pueda ser utilizada en las busquedas.

## Mensajes del sistema

El sistema debe mostrar mensajes claros en los siguientes casos:

- Cuando no exista una ruta entre las ciudades seleccionadas.
- Cuando una ciudad ingresada no exista.
- Cuando falten datos obligatorios.
- Cuando la distancia ingresada no sea valida.

## Evidencias sugeridas

Para documentar el funcionamiento se recomienda capturar:

- Pantalla inicial del sistema.
- Consulta exitosa de ruta mas corta.
- Consulta de todas las rutas.
- Registro de una nueva ciudad.
- Registro de una nueva conexion.
- Caso donde no exista una ruta disponible.
