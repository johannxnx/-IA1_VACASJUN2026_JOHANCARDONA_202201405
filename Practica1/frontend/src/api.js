const API_URL = "http://127.0.0.1:8000";

// Funcion central para hacer peticiones HTTP al backend.
// Todas las llamadas reutilizan esta funcion para manejar JSON y errores igual.
async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(formatError(data.detail));
  }

  return data;
}

// Carga las ciudades que el backend obtiene desde Prolog.
export function getCiudades() {
  return request("/ciudades");
}

// Solicita al backend la ruta de menor distancia.
export function getRutaCorta(origen, destino) {
  return request("/ruta-corta", {
    method: "POST",
    body: JSON.stringify({ origen, destino }),
  });
}

// Solicita todas las rutas entre dos ciudades.
export function getTodasRutas(origen, destino) {
  return request("/todas-rutas", {
    method: "POST",
    body: JSON.stringify({ origen, destino }),
  });
}

// Envia una ciudad nueva al backend para que Prolog la agregue en memoria.
export function agregarCiudad(ciudad) {
  return request("/agregar-ciudad", {
    method: "POST",
    body: JSON.stringify({ ciudad: ciudad.trim() }),
  });
}

// Envia una conexion nueva. Number(distancia) asegura que llegue como numero.
export function agregarConexion(origen, destino, distancia) {
  return request("/agregar-conexion", {
    method: "POST",
    body: JSON.stringify({ origen, destino, distancia: Number(distancia) }),
  });
}

// FastAPI puede responder errores como texto o como lista de validaciones.
// Esta funcion los convierte a un mensaje simple para mostrarlo en pantalla.
function formatError(detail) {
  if (!detail) {
    return "No se pudo completar la solicitud.";
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(" ");
  }

  return "No se pudo completar la solicitud.";
}
