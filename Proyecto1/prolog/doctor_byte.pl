% ============================================================
% Doctor Byte - Base de Conocimiento (generado por el admin)
% Inteligencia Artificial 1 - USAC 2026
% ============================================================

:- dynamic tiene_sintoma/1.

% --- Sintomas ---
sintoma(pantalla_negra).
sintoma(reinicio_inesperado).
sintoma(lentitud_sistema).
sintoma(sobrecalentamiento).
sintoma(ruido_disco).
sintoma(no_arranca).
sintoma(pantalla_azul).
sintoma(no_reconoce_dispositivos).
sintoma(errores_memoria).
sintoma(ventilador_ruidoso).
sintoma(bateria_no_carga).
sintoma(wifi_no_conecta).
sintoma(aplicaciones_cierran_solas).
sintoma(teclado_no_funciona).
sintoma(imagen_distorsionada).
sintoma(no_enciende).
sintoma(archivos_corruptos).
sintoma(actualizaciones_fallan).

% --- Descripciones de sintomas ---
descripcion_sintoma(pantalla_negra, 'La pantalla no muestra imagen al encender').
descripcion_sintoma(reinicio_inesperado, 'El equipo se reinicia solo sin razon aparente').
descripcion_sintoma(lentitud_sistema, 'El sistema responde muy lento').
descripcion_sintoma(sobrecalentamiento, 'El equipo se calienta demasiado al usarlo').
descripcion_sintoma(ruido_disco, 'Se escuchan ruidos mecanicos desde el disco duro').
descripcion_sintoma(no_arranca, 'El sistema operativo no carga correctamente').
descripcion_sintoma(pantalla_azul, 'Aparece pantalla azul con codigo de error (BSOD)').
descripcion_sintoma(no_reconoce_dispositivos, 'Los USB u otros perifericos no son detectados').
descripcion_sintoma(errores_memoria, 'Aparecen mensajes de error relacionados con la RAM').
descripcion_sintoma(ventilador_ruidoso, 'El ventilador hace ruido excesivo o inusual').
descripcion_sintoma(bateria_no_carga, 'La bateria no aumenta su carga aunque este conectada').
descripcion_sintoma(wifi_no_conecta, 'No es posible conectarse a redes inalambricas').
descripcion_sintoma(aplicaciones_cierran_solas, 'Los programas se cierran solos de manera inesperada').
descripcion_sintoma(teclado_no_funciona, 'Algunas teclas o todo el teclado no responde').
descripcion_sintoma(imagen_distorsionada, 'La imagen en pantalla aparece con artefactos o distorsion').
descripcion_sintoma(no_enciende, 'El equipo no da ninguna senal de vida al presionar el boton').
descripcion_sintoma(archivos_corruptos, 'Archivos se corrumpen o desaparecen sin razon').
descripcion_sintoma(actualizaciones_fallan, 'Las actualizaciones del sistema fallan o no se instalan').

% --- Fallas ---
falla(fallo_disco_duro).
falla(fallo_ram).
falla(sobrecalentamiento_cpu).
falla(fallo_tarjeta_grafica).
falla(infeccion_malware).
falla(fallo_sistema_operativo).
falla(fallo_fuente_poder).
falla(fallo_bateria).
falla(fallo_red).
falla(fallo_teclado).
falla(fallo_controladores).

% --- Descripciones de fallas ---
descripcion_falla(fallo_disco_duro, 'Fallo en el disco duro: el almacenamiento presenta danos fisicos o logicos').
descripcion_falla(fallo_ram, 'Fallo en la memoria RAM: uno o mas modulos estan danados o mal instalados').
descripcion_falla(sobrecalentamiento_cpu, 'Sobrecalentamiento de CPU: la temperatura excede niveles seguros de operacion').
descripcion_falla(fallo_tarjeta_grafica, 'Fallo en la tarjeta grafica: el procesador de video no funciona correctamente').
descripcion_falla(infeccion_malware, 'Infeccion por malware: software malicioso esta afectando el sistema').
descripcion_falla(fallo_sistema_operativo, 'Fallo del sistema operativo: archivos del SO estan corruptos o incompletos').
descripcion_falla(fallo_fuente_poder, 'Fallo en la fuente de poder: el suministro electrico es inestable o insuficiente').
descripcion_falla(fallo_bateria, 'Fallo de bateria: la bateria no retiene carga o esta danada').
descripcion_falla(fallo_red, 'Fallo de red: el adaptador de red o sus controladores presentan problemas').
descripcion_falla(fallo_teclado, 'Fallo de teclado: el dispositivo de entrada tiene danos fisicos o de conexion').
descripcion_falla(fallo_controladores, 'Fallo de controladores: los drivers del sistema estan desactualizados o corruptos').

% --- Recomendaciones ---
recomendaciones(fallo_disco_duro, ['Realizar respaldo inmediato de los datos mas importantes', 'Ejecutar CHKDSK o similar para verificar sectores danados', 'Reemplazar el disco duro por uno nuevo (HDD o SSD)', 'Considerar instalacion en SSD para mejor rendimiento']).
recomendaciones(fallo_ram, ['Ejecutar la herramienta MemTest86 para diagnostico detallado', 'Retirar y reinsertar los modulos de RAM asegurandose del encaje', 'Probar con un solo modulo de RAM a la vez para aislar el danado', 'Reemplazar el modulo de RAM defectuoso']).
recomendaciones(sobrecalentamiento_cpu, ['Limpiar el polvo acumulado en ventiladores y disipadores', 'Reemplazar la pasta termica entre CPU y disipador', 'Verificar que los ventiladores giren correctamente', 'Mejorar la ventilacion del gabinete o agregar ventiladores']).
recomendaciones(fallo_tarjeta_grafica, ['Actualizar los controladores de la tarjeta grafica', 'Verificar que la tarjeta este correctamente asentada en el slot PCIe', 'Limpiar los contactos dorados de la tarjeta grafica', 'Si el problema persiste, reemplazar la tarjeta grafica']).
recomendaciones(infeccion_malware, ['Ejecutar un analisis completo con antivirus actualizado', 'Usar herramientas especializadas como Malwarebytes', 'Evitar descargar software de fuentes no confiables', 'Cambiar contrasenas de cuentas importantes tras la limpieza']).
recomendaciones(fallo_sistema_operativo, ['Ejecutar reparacion del sistema operativo desde medio de arranque', 'Verificar y reparar archivos del sistema con SFC /scannow', 'Como ultima opcion, reinstalar el sistema operativo', 'Realizar respaldo de datos antes de reinstalar']).
recomendaciones(fallo_fuente_poder, ['Verificar que todos los cables de alimentacion esten bien conectados', 'Probar con otra fuente de poder si es posible', 'Medir los voltajes de salida con multimetro', 'Reemplazar la fuente de poder si entrega voltajes inestables']).
recomendaciones(fallo_bateria, ['Calibrar la bateria: descargar completamente y cargar al 100%', 'Verificar que el cargador entrega el voltaje correcto', 'Reemplazar la bateria por una original o compatible certificada', 'Evitar cargar la bateria en ambientes de alta temperatura']).
recomendaciones(fallo_red, ['Actualizar los controladores del adaptador de red', 'Verificar la configuracion de red en el sistema operativo', 'Reiniciar el adaptador de red desde el administrador de dispositivos', 'Usar adaptador USB-WiFi externo como alternativa temporal']).
recomendaciones(fallo_teclado, ['Verificar la conexion del teclado (USB o interna en laptops)', 'Probar con un teclado externo para descartar problema de software', 'Limpiar el teclado con aire comprimido', 'Reemplazar el teclado si el dano es fisico']).
recomendaciones(fallo_controladores, ['Actualizar todos los controladores desde el administrador de dispositivos', 'Desinstalar y reinstalar el controlador del dispositivo con problemas', 'Usar herramientas del fabricante para actualizacion automatica', 'Restaurar el sistema a un punto anterior si el problema inicio tras una actualizacion']).

% --- Reglas de inferencia ---
diagnosticar(fallo_disco_duro) :-
    tiene_sintoma(ruido_disco),
    tiene_sintoma(archivos_corruptos).
diagnosticar(fallo_disco_duro) :-
    tiene_sintoma(no_arranca),
    tiene_sintoma(lentitud_sistema),
    tiene_sintoma(archivos_corruptos).
diagnosticar(fallo_ram) :-
    tiene_sintoma(pantalla_azul),
    tiene_sintoma(errores_memoria).
diagnosticar(fallo_ram) :-
    tiene_sintoma(reinicio_inesperado),
    tiene_sintoma(aplicaciones_cierran_solas),
    tiene_sintoma(errores_memoria).
diagnosticar(sobrecalentamiento_cpu) :-
    tiene_sintoma(sobrecalentamiento),
    tiene_sintoma(ventilador_ruidoso),
    tiene_sintoma(reinicio_inesperado).
diagnosticar(fallo_tarjeta_grafica) :-
    tiene_sintoma(imagen_distorsionada),
    tiene_sintoma(pantalla_negra).
diagnosticar(infeccion_malware) :-
    tiene_sintoma(lentitud_sistema),
    tiene_sintoma(aplicaciones_cierran_solas),
    tiene_sintoma(actualizaciones_fallan).
diagnosticar(fallo_sistema_operativo) :-
    tiene_sintoma(no_arranca),
    tiene_sintoma(archivos_corruptos),
    tiene_sintoma(actualizaciones_fallan).
diagnosticar(fallo_fuente_poder) :-
    tiene_sintoma(no_enciende),
    tiene_sintoma(reinicio_inesperado).
diagnosticar(fallo_bateria) :-
    tiene_sintoma(bateria_no_carga),
    tiene_sintoma(sobrecalentamiento).
diagnosticar(fallo_red) :-
    tiene_sintoma(wifi_no_conecta),
    tiene_sintoma(no_reconoce_dispositivos).
diagnosticar(fallo_controladores) :-
    tiene_sintoma(no_reconoce_dispositivos),
    tiene_sintoma(actualizaciones_fallan).
diagnosticar(fallo_teclado) :-
    tiene_sintoma(teclado_no_funciona).
diagnosticar(fallo_red) :-
    tiene_sintoma(wifi_no_conecta).
diagnosticar(fallo_bateria) :-
    tiene_sintoma(bateria_no_carga).
diagnosticar(fallo_disco_duro) :-
    tiene_sintoma(ruido_disco).
diagnosticar(fallo_tarjeta_grafica) :-
    tiene_sintoma(imagen_distorsionada).
diagnosticar(fallo_ram) :-
    tiene_sintoma(errores_memoria).
diagnosticar(sobrecalentamiento_cpu) :-
    tiene_sintoma(sobrecalentamiento).
diagnosticar(fallo_sistema_operativo) :-
    tiene_sintoma(no_arranca).
diagnosticar(fallo_fuente_poder) :-
    tiene_sintoma(no_enciende).
diagnosticar(fallo_tarjeta_grafica) :-
    tiene_sintoma(pantalla_negra).
diagnosticar(fallo_ram) :-
    tiene_sintoma(reinicio_inesperado).
diagnosticar(infeccion_malware) :-
    tiene_sintoma(lentitud_sistema).
diagnosticar(fallo_ram) :-
    tiene_sintoma(pantalla_azul).
diagnosticar(fallo_controladores) :-
    tiene_sintoma(no_reconoce_dispositivos).
diagnosticar(sobrecalentamiento_cpu) :-
    tiene_sintoma(ventilador_ruidoso).
diagnosticar(infeccion_malware) :-
    tiene_sintoma(aplicaciones_cierran_solas).
diagnosticar(fallo_disco_duro) :-
    tiene_sintoma(archivos_corruptos).
diagnosticar(fallo_sistema_operativo) :-
    tiene_sintoma(actualizaciones_fallan).

% --- Predicados auxiliares ---

cargar_sintomas([]).
cargar_sintomas([H|T]) :-
    assertz(tiene_sintoma(H)),
    cargar_sintomas(T).

eliminar_duplicados(Lista, SinDuplicados) :-
    eliminar_duplicados(Lista, [], SinDuplicados).

eliminar_duplicados([], Acum, Acum).
eliminar_duplicados([diagnostico(Falla, _, _)|Resto], Acum, Resultado) :-
    member(diagnostico(Falla, _, _), Acum),
    !,
    eliminar_duplicados(Resto, Acum, Resultado).
eliminar_duplicados([H|Resto], Acum, Resultado) :-
    eliminar_duplicados(Resto, [H|Acum], Resultado).

obtener_todos_los_sintomas(Lista) :-
    findall(sintoma(Id, Desc),
        (sintoma(Id), descripcion_sintoma(Id, Desc)),
        Lista).

obtener_diagnostico(SintomasUsuario, Resultados) :-
    retractall(tiene_sintoma(_)),
    cargar_sintomas(SintomasUsuario),
    findall(diagnostico(Falla, Desc, Recs),
        (diagnosticar(Falla),
         descripcion_falla(Falla, Desc),
         recomendaciones(Falla, Recs)),
        ResultadosDuplicados),
    eliminar_duplicados(ResultadosDuplicados, Resultados).

:- use_module(library(http/json)).

cmd_sintomas :-
    findall(json([id=Id, descripcion=Desc]),
        (sintoma(Id), descripcion_sintoma(Id, Desc)),
        Lista),
    json_write(current_output, Lista, [width(0)]), nl.

cmd_diagnostico(SintomasAtom) :-
    term_to_atom(Sintomas, SintomasAtom),
    retractall(tiene_sintoma(_)),
    cargar_sintomas(Sintomas),
    findall(Falla-json([falla=Falla, descripcion=Desc, recomendaciones=Recs]),
        (diagnosticar(Falla),
         descripcion_falla(Falla, Desc),
         recomendaciones(Falla, Recs)),
        Pares),
    quitar_pares_duplicados(Pares, [], ParesSinDup),
    pairs_values(ParesSinDup, Resultado),
    json_write(current_output, Resultado, [width(0)]), nl.

quitar_pares_duplicados([], Acum, Acum).
quitar_pares_duplicados([K-_|Resto], Acum, Resultado) :-
    member(K-_, Acum), !,
    quitar_pares_duplicados(Resto, Acum, Resultado).
quitar_pares_duplicados([Par|Resto], Acum, Resultado) :-
    quitar_pares_duplicados(Resto, [Par|Acum], Resultado).
