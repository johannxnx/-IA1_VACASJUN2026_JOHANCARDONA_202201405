% Permite modificar la base de conocimiento en tiempo de ejecucion
% cuando el usuario agrega ciudades o conexiones desde la interfaz.
:- dynamic ciudad/1.
:- dynamic conexion/3.

% Hechos: ciudades disponibles en la base de conocimiento.
% La practica pide minimo 10 ciudades; aqui se definen 12.
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

% Hechos: conexion(Origen, Destino, Distancia).
% Cada hecho representa una carretera conocida y su distancia.
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

% Regla para consultar una conexion directa en el sentido registrado.
carretera(Origen, Destino, Distancia) :-
    conexion(Origen, Destino, Distancia).

% Regla para tratar las carreteras como bidireccionales.
% Asi no es necesario duplicar conexion(a, b, d) y conexion(b, a, d).
carretera(Origen, Destino, Distancia) :-
    conexion(Destino, Origen, Distancia).

% ruta/4 es la regla publica para buscar un camino entre dos ciudades.
% Valida que ambas ciudades existan, llama a la busqueda recursiva y
% luego invierte la ruta porque se construye de atras hacia adelante.
ruta(Origen, Destino, Ruta, DistanciaTotal) :-
    ciudad(Origen),
    ciudad(Destino),
    buscar_ruta(Origen, Destino, [Origen], RutaInvertida, DistanciaTotal),
    reverse(RutaInvertida, Ruta).

% Caso base: cuando la ciudad actual ya es el destino, la ruta esta completa
% y la distancia que falta por recorrer es 0.
buscar_ruta(Destino, Destino, Visitadas, Visitadas, 0).

% Caso recursivo: avanza a una ciudad vecina que no haya sido visitada.
% member/2 evita repetir ciudades, por lo tanto evita ciclos.
buscar_ruta(Actual, Destino, Visitadas, Ruta, DistanciaTotal) :-
    carretera(Actual, Siguiente, Distancia),
    \+ member(Siguiente, Visitadas),
    buscar_ruta(Siguiente, Destino, [Siguiente | Visitadas], Ruta, DistanciaRestante),
    DistanciaTotal is Distancia + DistanciaRestante.

% Obtiene todas las rutas posibles entre origen y destino.
% findall/3 recolecta las soluciones y sort/4 las ordena por distancia.
todas_rutas(Origen, Destino, RutasOrdenadas) :-
    findall(
        ruta(Ruta, Distancia),
        ruta(Origen, Destino, Ruta, Distancia),
        Rutas
    ),
    sort(2, @=<, Rutas, RutasOrdenadas).

% Como todas_rutas/3 devuelve la lista ordenada, la primera solucion
% corresponde a la ruta con menor distancia total.
ruta_mas_corta(Origen, Destino, Ruta, Distancia) :-
    todas_rutas(Origen, Destino, [ruta(Ruta, Distancia) | _]).

% Agrega una ciudad nueva si todavia no existe.
% assertz/1 inserta el hecho al final de la base de conocimiento en memoria.
agregar_ciudad(Ciudad) :-
    \+ ciudad(Ciudad),
    assertz(ciudad(Ciudad)).

% Agrega una conexion si ambas ciudades existen, la distancia es positiva
% y no hay una conexion identica registrada en ningun sentido.
agregar_conexion(Origen, Destino, Distancia) :-
    ciudad(Origen),
    ciudad(Destino),
    number(Distancia),
    Distancia > 0,
    \+ conexion(Origen, Destino, Distancia),
    \+ conexion(Destino, Origen, Distancia),
    assertz(conexion(Origen, Destino, Distancia)).
