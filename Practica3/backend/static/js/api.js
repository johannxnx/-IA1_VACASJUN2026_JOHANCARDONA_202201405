// Modulo de comunicacion con la API REST del backend
// Centraliza todas las llamadas HTTP y el manejo del token JWT

const BASE = '';  // La API corre en el mismo servidor que el frontend

// Lee el token JWT almacenado en localStorage despues del login
function getToken() { return localStorage.getItem('si_token'); }

// Lee los datos del usuario guardados en localStorage al iniciar sesion
function getUser()  { return JSON.parse(localStorage.getItem('si_user') || 'null'); }

// Funcion generica para todas las peticiones HTTP a la API
// Agrega automaticamente el token JWT en el encabezado Authorization
async function apiFetch(path, opts = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...opts.headers };

  // Agrega el token Bearer en cada peticion a la API
  if (token) headers['Authorization'] = `Bearer ${token}`;

  // Para FormData (carga de archivos), elimina Content-Type para que el navegador lo establezca
  // con el boundary correcto del multipart/form-data
  if (opts.body instanceof FormData) delete headers['Content-Type'];

  const res = await fetch(BASE + path, { ...opts, headers });

  // Si el servidor responde 401, el token expiro o es invalido: redirige al login
  if (res.status === 401) { logout(); return null; }

  // HTTP 204 (No Content) no tiene cuerpo, retorna null directamente
  if (res.status === 204) return null;

  return res.json();
}

// Objeto API: agrupa todos los metodos de comunicacion con el backend por dominio funcional
const API = {
  // Autenticacion
  login: (email, password) =>
    apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  // Facturas: listar, obtener detalle, eliminar y subir archivo
  getFacturas: () => apiFetch('/api/facturas/'),
  getFactura: (id) => apiFetch(`/api/facturas/${id}`),
  deleteFactura: (id) => apiFetch(`/api/facturas/${id}`, { method: 'DELETE' }),
  uploadFactura: (formData) =>
    // headers:{} vacio para que apiFetch no sobreescriba el Content-Type del FormData
    apiFetch('/api/facturas/upload', { method: 'POST', body: formData, headers: {} }),

  // Proveedores: CRUD completo
  getProveedores: () => apiFetch('/api/proveedores/'),
  createProveedor: (data) =>
    apiFetch('/api/proveedores/', { method: 'POST', body: JSON.stringify(data) }),
  updateProveedor: (id, data) =>
    apiFetch(`/api/proveedores/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProveedor: (id) =>
    apiFetch(`/api/proveedores/${id}`, { method: 'DELETE' }),

  // Bitacora: solo lectura
  getBitacora: () => apiFetch('/api/bitacora/'),

  // Reportes: listar y generar
  getReportes: () => apiFetch('/api/reportes/'),
  generarReporte: (tipo, email) =>
    apiFetch('/api/reportes/generar', { method: 'POST', body: JSON.stringify({ tipo, email_destino: email || null }) }),
};

// Cierra la sesion eliminando el token y los datos del usuario del localStorage
// Redirige al usuario a la pagina de login
function logout() {
  localStorage.removeItem('si_token');
  localStorage.removeItem('si_user');
  window.location.href = '/login.html';
}
