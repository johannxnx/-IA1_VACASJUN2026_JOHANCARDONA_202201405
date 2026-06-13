# Casos de Prueba - Doctor Byte
**Universidad San Carlos de Guatemala - IA1 - 2026**
**Estudiante:** Johan Cardona - 202201405

---

## Ambiente de pruebas

| Parametro | Valor |
|---|---|
| Sistema operativo | Windows 11 |
| Python | 3.12.5 |
| SWI-Prolog | 10.0.2 |
| Navegador | Chrome/Edge |
| URL del sistema | http://localhost:5000 |

---

## CP-01: Carga de sintomas en el frontend

**Descripcion:** Verificar que el sistema carga y muestra todos los sintomas disponibles al abrir la pagina.

**Precondicion:** El servidor Flask esta corriendo.

**Pasos:**
1. Abrir http://localhost:5000 en el navegador.
2. Observar la cuadricula de sintomas.

**Resultado esperado:** Se muestran 18 tarjetas de sintomas, cada una con su descripcion legible.

**Resultado obtenido:** Se muestran los 18 sintomas correctamente.

**Estado:** APROBADO

---

## CP-02: Diagnostico con sintoma unico

**Descripcion:** Verificar que un solo sintoma genera un diagnostico.

**Precondicion:** El servidor esta activo.

**Pasos:**
1. Seleccionar unicamente "WiFi no conecta".
2. Hacer clic en "Analizar sintomas".

**Resultado esperado:** El sistema diagnostica "Fallo de red" con sus recomendaciones.

**Resultado obtenido:** Se muestra la falla "Fallo de red: el adaptador de red o sus controladores presentan problemas" con 4 recomendaciones.

**Estado:** APROBADO

---

## CP-03: Diagnostico con multiples sintomas (regla combinada)

**Descripcion:** Verificar que la combinacion de sintomas activa las reglas mas especificas.

**Precondicion:** El servidor esta activo.

**Pasos:**
1. Seleccionar "Ruido en el disco" y "Archivos corruptos".
2. Hacer clic en "Analizar sintomas".

**Resultado esperado:** El sistema diagnostica "Fallo en el disco duro".

**Resultado obtenido:** Se muestra "Fallo en el disco duro: el almacenamiento presenta danos fisicos o logicos" con 4 recomendaciones.

**Estado:** APROBADO

---

## CP-04: Diagnostico de RAM por pantalla azul

**Descripcion:** Verificar la regla que combina pantalla azul con errores de memoria.

**Pasos:**
1. Seleccionar "Pantalla azul (BSOD)" y "Errores de memoria".
2. Hacer clic en "Analizar sintomas".

**Resultado esperado:** Diagnostico de "Fallo en la memoria RAM".

**Resultado obtenido:** Se muestra "Fallo en la memoria RAM: uno o mas modulos estan danados o mal instalados".

**Estado:** APROBADO

---

## CP-05: Diagnostico de malware por multiples sintomas

**Descripcion:** Verificar la regla de infeccion por malware.

**Pasos:**
1. Seleccionar "Lentitud del sistema", "Aplicaciones cierran solas" y "Actualizaciones fallan".
2. Hacer clic en "Analizar sintomas".

**Resultado esperado:** Diagnostico de "Infeccion por malware".

**Resultado obtenido:** Se muestra "Infeccion por malware: software malicioso esta afectando el sistema".

**Estado:** APROBADO

---

## CP-06: Multiples diagnosticos para multiples sintomas

**Descripcion:** Verificar que el sistema puede retornar mas de un diagnostico cuando los sintomas apuntan a varias fallas.

**Pasos:**
1. Seleccionar "Pantalla negra", "WiFi no conecta" y "Ruido en el disco".
2. Hacer clic en "Analizar sintomas".

**Resultado esperado:** Se muestran multiples diagnosticos (tarjeta grafica, red y disco duro).

**Resultado obtenido:** Se muestran 3 diagnosticos independientes, uno por cada sintoma.

**Estado:** APROBADO

---

## CP-07: Buscador de sintomas

**Descripcion:** Verificar que el buscador filtra los sintomas en tiempo real.

**Pasos:**
1. Escribir "pantalla" en el campo de busqueda.
2. Observar las tarjetas mostradas.

**Resultado esperado:** Solo se muestran los sintomas que contienen "pantalla" en su descripcion.

**Resultado obtenido:** Se filtran y muestran unicamente "La pantalla no muestra imagen al encender" y "Aparece pantalla azul con codigo de error (BSOD)".

**Estado:** APROBADO

---

## CP-08: Persistencia del historial

**Descripcion:** Verificar que los diagnosticos se guardan y se pueden consultar en el historial.

**Pasos:**
1. Realizar al menos 2 diagnosticos.
2. Hacer clic en "Historial" en la barra de navegacion.
3. Verificar que aparecen los diagnosticos realizados.

**Resultado esperado:** El historial muestra todos los diagnosticos en orden del mas reciente al mas antiguo, con los sintomas y resultados de cada uno.

**Resultado obtenido:** Los diagnosticos aparecen correctamente con fecha, sintomas usados y fallas detectadas.

**Estado:** APROBADO

---

## CP-09: Notificacion a Telegram

**Descripcion:** Verificar que el sistema envia una notificacion a Telegram al completar un diagnostico.

**Precondicion:** El bot de Telegram esta configurado correctamente en el .env.

**Pasos:**
1. Seleccionar al menos un sintoma.
2. Hacer clic en "Analizar sintomas".
3. Revisar el chat de Telegram del bot.

**Resultado esperado:** Se recibe un mensaje en Telegram con los sintomas reportados, la falla detectada y las recomendaciones.

**Resultado obtenido:** El mensaje llega en formato HTML con los datos del diagnostico correctamente formateados.

**Estado:** APROBADO

---

## CP-10: Endpoint GET /api/sintomas

**Descripcion:** Verificar que el endpoint retorna la lista completa de sintomas en formato JSON.

**Pasos:**
1. Hacer una peticion GET a http://localhost:5000/api/sintomas.

**Resultado esperado:**
```json
{
  "ok": true,
  "sintomas": [ {"id": "...", "descripcion": "..."}, ... ]
}
```
18 sintomas en total.

**Resultado obtenido:** Response 200 con los 18 sintomas correctamente.

**Estado:** APROBADO

---

## CP-11: Endpoint POST /api/diagnostico con body invalido

**Descripcion:** Verificar que el sistema maneja correctamente peticiones mal formadas.

**Pasos:**
1. Hacer POST a /api/diagnostico con body `{}` (sin el campo sintomas).

**Resultado esperado:** Response 400 con mensaje de error descriptivo.

**Resultado obtenido:**
```json
{"ok": false, "error": "Se requiere el campo 'sintomas'"}
```
Response 400.

**Estado:** APROBADO

---

## CP-12: Limpiar seleccion

**Descripcion:** Verificar que el boton "Limpiar seleccion" resetea el estado correctamente.

**Pasos:**
1. Seleccionar varios sintomas.
2. Obtener un diagnostico.
3. Hacer clic en "Limpiar seleccion".

**Resultado esperado:** Todas las tarjetas se deseleccionan, el contador vuelve a 0, el boton "Analizar" se deshabilita y el panel de resultados desaparece.

**Resultado obtenido:** El estado de la pagina se resetea completamente como se esperaba.

**Estado:** APROBADO

---

## Resumen de resultados

| Total de casos | Aprobados | Fallidos |
|---|---|---|
| 12 | 12 | 0 |
