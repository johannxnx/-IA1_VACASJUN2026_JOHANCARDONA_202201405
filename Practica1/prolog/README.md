# Prolog

Motor logico de la practica, desarrollado con SWI-Prolog.

## Responsabilidad

- Definir ciudades.
- Definir conexiones entre ciudades.
- Guardar distancias entre conexiones.
- Buscar rutas.
- Evitar ciclos.
- Calcular distancia total.
- Determinar la ruta mas corta.

## Requisito minimo

La base de conocimiento debe incluir al menos 10 ciudades.

## Archivo principal

```text
rutas.pl
```

## Consultas de ejemplo

Consultar la ruta mas corta:

```prolog
ruta_mas_corta(guatemala, puerto_barrios, Ruta, Distancia).
```

Consultar todas las rutas:

```prolog
todas_rutas(guatemala, puerto_barrios, Rutas).
```

Agregar una ciudad:

```prolog
agregar_ciudad(jalapa).
```

Agregar una conexion:

```prolog
agregar_conexion(jalapa, guatemala, 100).
```
