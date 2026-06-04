const API_URL = "http://127.0.0.1:8000";

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

export function getCiudades() {
  return request("/ciudades");
}

export function getRutaCorta(origen, destino) {
  return request("/ruta-corta", {
    method: "POST",
    body: JSON.stringify({ origen, destino }),
  });
}

export function getTodasRutas(origen, destino) {
  return request("/todas-rutas", {
    method: "POST",
    body: JSON.stringify({ origen, destino }),
  });
}

export function agregarCiudad(ciudad) {
  return request("/agregar-ciudad", {
    method: "POST",
    body: JSON.stringify({ ciudad: ciudad.trim() }),
  });
}

export function agregarConexion(origen, destino, distancia) {
  return request("/agregar-conexion", {
    method: "POST",
    body: JSON.stringify({ origen, destino, distancia: Number(distancia) }),
  });
}

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
