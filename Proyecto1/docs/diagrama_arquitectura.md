# Diagrama de Arquitectura - Doctor Byte

---

## Diagrama General del Sistema

```
                          DOCTOR BYTE - ARQUITECTURA
+=========================================================================+

  USUARIO
    |
    | Abre navegador en localhost:5000
    v
+-------------------+
|   FRONTEND WEB    |
|-------------------|
|  HTML / CSS / JS  |       Peticiones HTTP/REST
|                   |--------------------------------------------+
|  - Seleccion de   |  GET  /api/sintomas                        |
|    sintomas       |  POST /api/diagnostico                     |
|  - Panel de       |  GET  /api/historial                       |
|    resultados     |                                            |
|  - Historial      |                                            |
+-------------------+                                            |
                                                                 v
                                                    +-------------------+
                                                    |   BACKEND FLASK   |
                                                    |-------------------|
                                                    |     Python        |
                                                    |                   |
                                          +---------| app.py            |
                                          |         | config.py         |
                          subprocess      |         | prolog_interface  |
                          (swipl --quiet) |         | history_manager   |
                                          |         | telegram_service  |
                                          |         +--------+----------+
                                          |                  |
                                          v                  |  Escribe/Lee
                            +-------------------+            v
                            |   MOTOR PROLOG    |  +-------------------+
                            |-------------------|  |     HISTORIAL     |
                            |   SWI-Prolog      |  |-------------------|
                            |   10.0.2          |  |  history.json     |
                            |                   |  |                   |
                            |  doctor_byte.pl   |  |  - ID diagnostico |
                            |  - Sintomas       |  |  - Timestamp      |
                            |  - Fallas         |  |  - Sintomas       |
                            |  - Reglas         |  |  - Resultados     |
                            |  - Hechos         |  +-------------------+
                            |  - Cortes (!)     |
                            |                   |
                            |  Salida: JSON     |
                            +-------------------+

                            +-------------------+
                            |   TELEGRAM API    |
                            |-------------------|
                            |  api.telegram.org |
                            |                   |
                            |  sendMessage      |<--- Backend HTTP POST
                            |  (HTML format)    |
                            |                   |
                            +--------+----------+
                                     |
                                     | Notificacion
                                     v
                            +-------------------+
                            |  CHAT TELEGRAM    |
                            |  del usuario      |
                            +-------------------+

+=========================================================================+
```

---

## Diagrama de Flujo de un Diagnostico

```
  Usuario                Frontend              Backend              Prolog
    |                       |                     |                    |
    |-- selecciona         |                     |                    |
    |   sintomas  -------> |                     |                    |
    |                       |                     |                    |
    |-- click              |                     |                    |
    |   "Analizar" ------> |                     |                    |
    |                       |-- POST             |                    |
    |                       |   /api/diagnostico  |                    |
    |                       |   {sintomas:[...]} ->                   |
    |                       |                     |-- subprocess      |
    |                       |                     |   swipl           |
    |                       |                     |   cmd_diagnostico ->
    |                       |                     |                    |
    |                       |                     |                    |-- evalua
    |                       |                     |                    |   reglas
    |                       |                     |                    |
    |                       |                     |      JSON output <-+
    |                       |                     |-- guarda en        |
    |                       |                     |   historial        |
    |                       |                     |-- envia a          |
    |                       |                     |   Telegram         |
    |                       |     response JSON <-+                    |
    |                       |-- muestra           |                    |
    |                       |   resultado         |                    |
    |<-- ve diagnostico ----|                     |                    |
    |    y recibe msg       |                     |                    |
    |    en Telegram        |                     |                    |
```

---

## Diagrama de Componentes del Archivo Prolog

```
  doctor_byte.pl
  +===========================================================+
  |                                                           |
  |  SECCION 1: Hechos - Sintomas                             |
  |  sintoma(pantalla_negra).                                 |
  |  sintoma(ruido_disco).  ... (18 sintomas)                 |
  |                                                           |
  |  SECCION 2: Descripciones de sintomas                     |
  |  descripcion_sintoma(pantalla_negra, 'texto...').         |
  |                                                           |
  |  SECCION 3: Hechos - Fallas                               |
  |  falla(fallo_disco_duro).  ... (11 fallas)                |
  |                                                           |
  |  SECCION 4: Descripciones de fallas                       |
  |  descripcion_falla(fallo_disco_duro, 'texto...').         |
  |                                                           |
  |  SECCION 5: Recomendaciones (listas)                      |
  |  recomendaciones(fallo_disco_duro, [rec1, rec2, ...]).    |
  |                                                           |
  |  SECCION 6: Reglas de inferencia                          |
  |  diagnosticar(Falla) :- tiene_sintoma(A), ...             |
  |  (13 reglas combinadas + 18 reglas de sintoma unico)      |
  |                                                           |
  |  SECCION 7-8: Predicados auxiliares                       |
  |  cargar_sintomas/1, eliminar_duplicados/3 con corte (!)   |
  |                                                           |
  |  SECCION 9: Salida JSON para la API                       |
  |  cmd_sintomas/0, cmd_diagnostico/1                        |
  |  usa library(http/json) de SWI-Prolog                    |
  |                                                           |
  +===========================================================+
```
