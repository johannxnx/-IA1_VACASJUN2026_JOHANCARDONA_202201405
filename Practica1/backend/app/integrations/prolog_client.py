from pathlib import Path
import re
import unicodedata

from fastapi import HTTPException

try:
    from pyswip import Prolog
except ImportError:
    Prolog = None


class PrologClient:
    def __init__(self) -> None:
        if Prolog is None:
            raise RuntimeError(
                "PySwip no esta instalado. Ejecuta: pip install -r backend/requirements.txt"
            )

        self.prolog = Prolog()
        self.prolog_file = self._get_prolog_file()
        self.prolog.consult(str(self.prolog_file))

    def obtener_ciudades(self) -> list[str]:
        resultados = self.prolog.query("ciudad(Ciudad)")
        ciudades = [str(resultado["Ciudad"]) for resultado in resultados]
        return sorted(ciudades)

    def ruta_mas_corta(self, origen: str, destino: str) -> dict:
        origen_atom = self._to_atom(origen)
        destino_atom = self._to_atom(destino)
        consulta = f"ruta_mas_corta({origen_atom}, {destino_atom}, Ruta, Distancia)"

        resultados = list(self.prolog.query(consulta, maxresult=1))
        if not resultados:
            raise HTTPException(status_code=404, detail="No existe una ruta disponible.")

        return self._convertir_ruta(resultados[0])

    def todas_rutas(self, origen: str, destino: str) -> list[dict]:
        origen_atom = self._to_atom(origen)
        destino_atom = self._to_atom(destino)
        consulta = f"ruta({origen_atom}, {destino_atom}, Ruta, Distancia)"

        resultados = list(self.prolog.query(consulta))
        rutas = [self._convertir_ruta(resultado) for resultado in resultados]
        rutas.sort(key=lambda item: item["distancia"])
        return rutas

    def agregar_ciudad(self, ciudad: str) -> None:
        ciudad_atom = self._to_atom(ciudad)
        consulta = f"agregar_ciudad({ciudad_atom})"

        if not list(self.prolog.query(consulta, maxresult=1)):
            raise HTTPException(status_code=409, detail="La ciudad ya existe.")

    def agregar_conexion(self, origen: str, destino: str, distancia: int) -> None:
        origen_atom = self._to_atom(origen)
        destino_atom = self._to_atom(destino)
        consulta = f"agregar_conexion({origen_atom}, {destino_atom}, {distancia})"

        if not list(self.prolog.query(consulta, maxresult=1)):
            raise HTTPException(
                status_code=400,
                detail="No se pudo agregar la conexion. Verifica que las ciudades existan.",
            )

    def _convertir_ruta(self, resultado: dict) -> dict:
        # PySwip devuelve listas Prolog como objetos iterables; aqui las pasamos a JSON simple.
        ruta = [str(ciudad) for ciudad in resultado["Ruta"]]
        return {
            "ruta": ruta,
            "distancia": int(resultado["Distancia"]),
        }

    def _to_atom(self, valor: str) -> str:
        # Normalizamos el texto para evitar inyeccion de consultas Prolog desde la API.
        # Tambien convertimos acentos para que "San Jose" y "San José" puedan trabajarse igual.
        texto = unicodedata.normalize("NFD", valor.strip().lower())
        texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
        atom = re.sub(r"\s+", "_", texto)

        if not re.fullmatch(r"[a-z_][a-z0-9_]*", atom):
            raise HTTPException(
                status_code=422,
                detail="Usa nombres de ciudad con letras, numeros, espacios o guion bajo.",
            )

        return atom

    def _get_prolog_file(self) -> Path:
        backend_dir = Path(__file__).resolve().parents[2]
        practica_dir = backend_dir.parent
        prolog_file = practica_dir / "prolog" / "rutas.pl"

        if not prolog_file.exists():
            raise FileNotFoundError(f"No se encontro el archivo Prolog: {prolog_file}")

        return prolog_file
