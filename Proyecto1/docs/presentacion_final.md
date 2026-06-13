# Presentacion Final - Doctor Byte
## Estructura y contenido para las diapositivas

---

## DIAPOSITIVA 1 - Portada

**Titulo:** Doctor Byte
**Subtitulo:** Sistema Experto para Diagnostico de Fallas en Computadoras

Universidad San Carlos de Guatemala
Facultad de Ingenieria - Ingenieria en Ciencias y Sistemas
Inteligencia Artificial 1 - Vacaciones Primer Semestre 2026

**Presentado por:** Johan Cardona - 202201405

---

## DIAPOSITIVA 2 - El Problema

**Titulo:** El Problema

El diagnostico de fallas en computadoras requiere conocimiento tecnico especializado que la mayoria de usuarios no tiene.

- Los usuarios no saben interpretar sintomas tecnicos.
- Buscar en internet da resultados genericos y confusos.
- Contratar soporte tecnico tiene costo y demora.
- Errores de diagnostico pueden empeorar el problema.

**Imagen sugerida:** Persona confundida frente a una computadora con pantalla de error.

---

## DIAPOSITIVA 3 - La Solucion

**Titulo:** Doctor Byte - La Solucion

Sistema experto que simula el razonamiento de un tecnico para diagnosticar fallas de forma automatica.

- El usuario describe lo que ve (sintomas).
- El sistema razona y entrega un diagnostico.
- Se entregan recomendaciones especificas para resolver la falla.
- Los resultados llegan tambien por Telegram.

**Imagen sugerida:** Captura de pantalla de la interfaz con un diagnostico visible.

---

## DIAPOSITIVA 4 - Arquitectura del Sistema

**Titulo:** Arquitectura

Mostrar el diagrama con los 4 componentes principales:

```
[Frontend Web] <---> [Backend Flask] <---> [Motor Prolog]
                            |
                     [Bot Telegram]
                            |
                     [Historial JSON]
```

Descripcion breve de cada componente:
- **Frontend:** Interfaz donde el usuario selecciona sintomas
- **Backend:** API REST en Python que coordina todo
- **Prolog:** Motor de inferencia con las reglas del experto
- **Telegram:** Canal de notificacion automatica

---

## DIAPOSITIVA 5 - Base de Conocimiento en Prolog

**Titulo:** Motor de Inferencia - Prolog

Mostrar un ejemplo real de una regla:

```prolog
% Si el disco hace ruido Y los archivos se corrumpen
% => el disco duro esta fallando
diagnosticar(fallo_disco_duro) :-
    tiene_sintoma(ruido_disco),
    tiene_sintoma(archivos_corruptos).
```

Numeros clave:
- 18 sintomas implementados
- 11 fallas diagnosticables
- 31 reglas de inferencia (13 combinadas + 18 de sintoma unico)
- 11 conjuntos de recomendaciones
- Uso de hechos, reglas, listas y corte (!)

---

## DIAPOSITIVA 6 - Demostracion en Vivo

**Titulo:** Demostracion del Sistema

(Esta diapositiva acompana la demostracion en vivo)

Casos a demostrar:
1. Seleccionar "Ruido en el disco" + "Archivos corruptos" => Fallo de disco duro
2. Seleccionar "Pantalla azul" + "Errores de memoria" => Fallo de RAM
3. Seleccionar "WiFi no conecta" solo => Fallo de red
4. Ver la notificacion llegar a Telegram
5. Revisar el historial de diagnosticos

---

## DIAPOSITIVA 7 - Tecnologias Utilizadas

**Titulo:** Stack Tecnologico

| Componente | Tecnologia |
|---|---|
| Motor de inferencia | SWI-Prolog 10 |
| Backend | Python 3.12 + Flask |
| Frontend | HTML5 + CSS3 + JavaScript |
| Notificaciones | Telegram Bot API |
| Control de versiones | Git + GitHub |

**Punto clave:** Python llama a Prolog como subproceso y lee el resultado en JSON, lo que hace la integracion robusta y compatible con cualquier version de SWI-Prolog.

---

## DIAPOSITIVA 8 - Resultados y Conclusiones

**Titulo:** Resultados

Lo que se logro:
- Sistema funcional que diagnostica 11 tipos de fallas de hardware y software.
- Interfaz web moderna e intuitiva con busqueda y seleccion visual de sintomas.
- Integracion completa con Telegram para notificaciones en tiempo real.
- Historial persistente de todos los diagnosticos realizados.
- Base de conocimiento extensible: agregar nuevas fallas solo requiere editar el archivo .pl.

**Aprendizajes:**
- Implementacion practica de logica declarativa con Prolog.
- Integracion de tecnologias heterogeneas (Python + Prolog + Telegram).
- Diseno de sistemas expertos basados en reglas.

---

## DIAPOSITIVA 9 - Cierre

**Titulo:** Doctor Byte

**Frase de cierre:** "Democratizando el soporte tecnico mediante inteligencia artificial basada en reglas."

Repositorio del proyecto: [URL de GitHub]

Preguntas y respuestas.

---

## Consejos para la presentacion

- Tiempo estimado por diapositiva: 1 a 2 minutos.
- Tiempo total aproximado: 15 a 20 minutos incluyendo demostracion.
- Tener el sistema corriendo antes de empezar.
- Abrir el historial para mostrar diagnosticos previos.
- Tener el chat de Telegram visible en otra pantalla o pestaña para mostrar que llega la notificacion en tiempo real.
