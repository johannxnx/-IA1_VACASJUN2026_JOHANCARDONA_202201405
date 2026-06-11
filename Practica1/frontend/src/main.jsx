import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowRight,
  CirclePlus,
  GitBranch,
  Loader2,
  MapPin,
  RefreshCcw,
  Route,
  Search,
} from "lucide-react";
import {
  agregarCiudad,
  agregarConexion,
  getCiudades,
  getRutaCorta,
  getTodasRutas,
} from "./api";
import "./styles.css";

function App() {
  // Estados principales de la interfaz: datos cargados, formularios,
  // resultados y mensajes visibles para el usuario.
  const [ciudades, setCiudades] = useState([]);
  const [origen, setOrigen] = useState("");
  const [destino, setDestino] = useState("");
  const [nuevaCiudad, setNuevaCiudad] = useState("");
  const [conexionOrigen, setConexionOrigen] = useState("");
  const [conexionDestino, setConexionDestino] = useState("");
  const [distancia, setDistancia] = useState("");
  const [rutaCorta, setRutaCorta] = useState(null);
  const [rutas, setRutas] = useState([]);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const puedeBuscar = origen && destino && origen !== destino;

  // Al abrir la aplicacion se cargan las ciudades desde el backend.
  useEffect(() => {
    cargarCiudades();
  }, []);

  async function cargarCiudades() {
    setError("");

    try {
      const data = await getCiudades();
      setCiudades(data.ciudades);

      // Selecciona valores iniciales para que el usuario pueda probar rapido.
      if (!origen && data.ciudades.length > 0) {
        setOrigen(data.ciudades[0]);
      }

      if (!destino && data.ciudades.length > 1) {
        setDestino(data.ciudades[1]);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function consultarRutaCorta() {
    // Consulta principal de la practica: obtiene la mejor ruta desde Prolog.
    await ejecutarConsulta(async () => {
      const data = await getRutaCorta(origen, destino);
      setRutaCorta(data);
      setRutas([]);
      setMensaje("Ruta mas corta encontrada.");
    });
  }

  async function consultarTodasRutas() {
    // Obtiene todas las rutas; la primera tambien se muestra como mejor resultado.
    await ejecutarConsulta(async () => {
      const data = await getTodasRutas(origen, destino);
      setRutas(data.rutas);
      setRutaCorta(data.rutas[0] || null);
      setMensaje(`Se encontraron ${data.rutas.length} rutas posibles.`);
    });
  }

  async function ejecutarConsulta(callback) {
    // Wrapper para reutilizar manejo de carga, errores y limpieza de mensajes.
    setLoading(true);
    setError("");
    setMensaje("");

    try {
      await callback();
    } catch (err) {
      setRutaCorta(null);
      setRutas([]);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function guardarCiudad(event) {
    // Evita que el formulario recargue la pagina y envia la ciudad al backend.
    event.preventDefault();
    setError("");
    setMensaje("");

    if (!nuevaCiudad.trim()) {
      setError("Ingresa el nombre de la ciudad.");
      return;
    }

    try {
      const data = await agregarCiudad(nuevaCiudad);
      setMensaje(data.mensaje);
      setNuevaCiudad("");
      await cargarCiudades();
    } catch (err) {
      setError(err.message);
    }
  }

  async function guardarConexion(event) {
    // Envia origen, destino y distancia para crear una conexion nueva en Prolog.
    event.preventDefault();
    setError("");
    setMensaje("");

    try {
      const data = await agregarConexion(conexionOrigen, conexionDestino, distancia);
      setMensaje(data.mensaje);
      setConexionOrigen("");
      setConexionDestino("");
      setDistancia("");
    } catch (err) {
      setError(err.message);
    }
  }

  function limpiarBusqueda() {
    // Limpia resultados visibles sin borrar la base de conocimiento.
    setRutaCorta(null);
    setRutas([]);
    setMensaje("");
    setError("");
  }

  const resumen = useMemo(() => {
    // Calcula estadisticas simples solo cuando cambia el listado de rutas.
    if (rutas.length === 0) return null;

    const distancias = rutas.map((ruta) => ruta.distancia);
    return {
      total: rutas.length,
      menor: Math.min(...distancias),
      mayor: Math.max(...distancias),
    };
  }, [rutas]);

  return (
    <main className="app-shell">
      <section className="top-bar">
        <div>
          <p className="eyebrow">Inteligencia Artificial 1</p>
          <h1>Ruta mas corta entre ciudades</h1>
        </div>
        <div className="status-pill">
          <MapPin size={18} />
          <span>{ciudades.length} ciudades</span>
        </div>
      </section>

      <section className="workspace">
        {/* Panel izquierdo: controles de busqueda y formularios de administracion. */}
        <aside className="panel controls-panel">
          <div className="panel-header">
            <Route size={20} />
            <h2>Busqueda</h2>
          </div>

          <label>
            Ciudad origen
            <select value={origen} onChange={(event) => setOrigen(event.target.value)}>
              {ciudades.map((ciudad) => (
                <option key={ciudad} value={ciudad}>
                  {formatCiudad(ciudad)}
                </option>
              ))}
            </select>
          </label>

          <label>
            Ciudad destino
            <select value={destino} onChange={(event) => setDestino(event.target.value)}>
              {ciudades.map((ciudad) => (
                <option key={ciudad} value={ciudad}>
                  {formatCiudad(ciudad)}
                </option>
              ))}
            </select>
          </label>

          <div className="button-row">
            <button type="button" onClick={consultarRutaCorta} disabled={!puedeBuscar || loading}>
              {loading ? <Loader2 className="spin" size={18} /> : <Search size={18} />}
              Ruta corta
            </button>
            <button type="button" className="secondary" onClick={consultarTodasRutas} disabled={!puedeBuscar || loading}>
              <GitBranch size={18} />
              Todas
            </button>
            <button type="button" className="icon-button" onClick={limpiarBusqueda} aria-label="Limpiar busqueda">
              <RefreshCcw size={18} />
            </button>
          </div>

          <form onSubmit={guardarCiudad} className="stack-form">
            <div className="panel-header compact">
              <CirclePlus size={18} />
              <h3>Agregar ciudad</h3>
            </div>
            <input
              value={nuevaCiudad}
              onChange={(event) => setNuevaCiudad(event.target.value)}
              placeholder="Ejemplo: jalapa"
              required
            />
            <button type="submit" className="secondary">
              Guardar ciudad
            </button>
          </form>

          <form onSubmit={guardarConexion} className="stack-form">
            <div className="panel-header compact">
              <ArrowRight size={18} />
              <h3>Agregar conexion</h3>
            </div>
            <select value={conexionOrigen} onChange={(event) => setConexionOrigen(event.target.value)} required>
              <option value="">Origen</option>
              {ciudades.map((ciudad) => (
                <option key={ciudad} value={ciudad}>
                  {formatCiudad(ciudad)}
                </option>
              ))}
            </select>
            <select value={conexionDestino} onChange={(event) => setConexionDestino(event.target.value)} required>
              <option value="">Destino</option>
              {ciudades.map((ciudad) => (
                <option key={ciudad} value={ciudad}>
                  {formatCiudad(ciudad)}
                </option>
              ))}
            </select>
            <input
              type="number"
              min="1"
              value={distancia}
              onChange={(event) => setDistancia(event.target.value)}
              placeholder="Distancia"
              required
            />
            <button type="submit" className="secondary">
              Guardar conexion
            </button>
          </form>
        </aside>

        <section className="results">
          {(mensaje || error) && (
            <div className={error ? "notice error" : "notice success"}>
              {error || mensaje}
            </div>
          )}

          {/* Resultado principal: ruta mas corta o estado inicial cuando no hay busqueda. */}
          {rutaCorta ? (
            <article className="route-highlight">
              <div>
                <p className="eyebrow">Mejor resultado</p>
                <h2>{rutaCorta.distancia} km</h2>
              </div>
              <RoutePath ruta={rutaCorta.ruta} />
            </article>
          ) : (
            <article className="empty-state">
              <MapPin size={38} />
              <h2>Selecciona dos ciudades</h2>
              <p>Los calculos se realizan en Prolog y el backend devuelve los resultados.</p>
            </article>
          )}

          {/* Estadisticas visibles cuando se consultan todas las rutas. */}
          {resumen && (
            <div className="stats-grid">
              <Stat label="Rutas" value={resumen.total} />
              <Stat label="Menor distancia" value={`${resumen.menor} km`} />
              <Stat label="Mayor distancia" value={`${resumen.mayor} km`} />
            </div>
          )}

          {/* Tabla visible cuando el usuario solicita todas las rutas. */}
          {rutas.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Ruta</th>
                    <th>Distancia</th>
                  </tr>
                </thead>
                <tbody>
                  {rutas.map((ruta, index) => (
                    <tr key={`${ruta.ruta.join("-")}-${ruta.distancia}`}>
                      <td>{index + 1}</td>
                      <td>{ruta.ruta.map(formatCiudad).join(" -> ")}</td>
                      <td>{ruta.distancia} km</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function RoutePath({ ruta }) {
  // Muestra la ruta como una secuencia visual de ciudades separadas por flechas.
  return (
    <div className="route-path">
      {ruta.map((ciudad, index) => (
        <React.Fragment key={`${ciudad}-${index}`}>
          <span>{formatCiudad(ciudad)}</span>
          {index < ruta.length - 1 && <ArrowRight size={17} />}
        </React.Fragment>
      ))}
    </div>
  );
}

function Stat({ label, value }) {
  // Tarjeta pequena para mostrar estadisticas de las rutas encontradas.
  return (
    <article className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function formatCiudad(ciudad) {
  // Convierte atomos Prolog como puerto_barrios a texto legible: Puerto Barrios.
  return ciudad
    .split("_")
    .map((parte) => parte.charAt(0).toUpperCase() + parte.slice(1))
    .join(" ");
}

createRoot(document.getElementById("root")).render(<App />);
