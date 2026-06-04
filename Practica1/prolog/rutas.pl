:- dynamic ciudad/1.
:- dynamic conexion/3.

ciudad(guatemala).
ciudad(antigua).
ciudad(escuintla).
ciudad(chimaltenango).
ciudad(quetzaltenango).
ciudad(retalhuleu).
ciudad(mazatenango).
ciudad(coban).
ciudad(flores).
ciudad(zacapa).
ciudad(chiquimula).
ciudad(puerto_barrios).

conexion(guatemala, antigua, 40).
conexion(guatemala, escuintla, 60).
conexion(guatemala, chimaltenango, 55).
conexion(guatemala, coban, 210).
conexion(guatemala, zacapa, 150).
conexion(antigua, chimaltenango, 35).
conexion(escuintla, mazatenango, 160).
conexion(chimaltenango, quetzaltenango, 145).
conexion(quetzaltenango, retalhuleu, 80).
conexion(retalhuleu, mazatenango, 45).
conexion(coban, flores, 250).
conexion(flores, puerto_barrios, 320).
conexion(zacapa, chiquimula, 45).
conexion(zacapa, puerto_barrios, 170).
conexion(chiquimula, puerto_barrios, 210).
conexion(mazatenango, quetzaltenango, 95).

carretera(Origen, Destino, Distancia) :-
    conexion(Origen, Destino, Distancia).

carretera(Origen, Destino, Distancia) :-
    conexion(Destino, Origen, Distancia).

ruta(Origen, Destino, Ruta, DistanciaTotal) :-
    ciudad(Origen),
    ciudad(Destino),
    buscar_ruta(Origen, Destino, [Origen], RutaInvertida, DistanciaTotal),
    reverse(RutaInvertida, Ruta).

buscar_ruta(Destino, Destino, Visitadas, Visitadas, 0).

buscar_ruta(Actual, Destino, Visitadas, Ruta, DistanciaTotal) :-
    carretera(Actual, Siguiente, Distancia),
    \+ member(Siguiente, Visitadas),
    buscar_ruta(Siguiente, Destino, [Siguiente | Visitadas], Ruta, DistanciaRestante),
    DistanciaTotal is Distancia + DistanciaRestante.

todas_rutas(Origen, Destino, RutasOrdenadas) :-
    findall(
        ruta(Ruta, Distancia),
        ruta(Origen, Destino, Ruta, Distancia),
        Rutas
    ),
    sort(2, @=<, Rutas, RutasOrdenadas).

ruta_mas_corta(Origen, Destino, Ruta, Distancia) :-
    todas_rutas(Origen, Destino, [ruta(Ruta, Distancia) | _]).

agregar_ciudad(Ciudad) :-
    \+ ciudad(Ciudad),
    assertz(ciudad(Ciudad)).

agregar_conexion(Origen, Destino, Distancia) :-
    ciudad(Origen),
    ciudad(Destino),
    number(Distancia),
    Distancia > 0,
    \+ conexion(Origen, Destino, Distancia),
    \+ conexion(Destino, Origen, Distancia),
    assertz(conexion(Origen, Destino, Distancia)).
