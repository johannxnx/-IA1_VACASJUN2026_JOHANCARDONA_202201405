const BASE = '';

function getToken() { return localStorage.getItem('si_token'); }
function getUser()  { return JSON.parse(localStorage.getItem('si_user') || 'null'); }

async function apiFetch(path, opts = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...opts.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (opts.body instanceof FormData) delete headers['Content-Type'];

  const res = await fetch(BASE + path, { ...opts, headers });
  if (res.status === 401) { logout(); return null; }
  if (res.status === 204) return null;
  return res.json();
}

const API = {
  // Auth
  login: (email, password) =>
    apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  // Facturas
  getFacturas: () => apiFetch('/api/facturas/'),
  getFactura: (id) => apiFetch(`/api/facturas/${id}`),
  deleteFactura: (id) => apiFetch(`/api/facturas/${id}`, { method: 'DELETE' }),
  uploadFactura: (formData) =>
    apiFetch('/api/facturas/upload', { method: 'POST', body: formData, headers: {} }),

  // Proveedores
  getProveedores: () => apiFetch('/api/proveedores/'),
  createProveedor: (data) =>
    apiFetch('/api/proveedores/', { method: 'POST', body: JSON.stringify(data) }),
  updateProveedor: (id, data) =>
    apiFetch(`/api/proveedores/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProveedor: (id) =>
    apiFetch(`/api/proveedores/${id}`, { method: 'DELETE' }),

  // Bitácora
  getBitacora: () => apiFetch('/api/bitacora/'),

  // Reportes
  getReportes: () => apiFetch('/api/reportes/'),
  generarReporte: (tipo, email) =>
    apiFetch('/api/reportes/generar', { method: 'POST', body: JSON.stringify({ tipo, email_destino: email || null }) }),
};

function logout() {
  localStorage.removeItem('si_token');
  localStorage.removeItem('si_user');
  window.location.href = '/login.html';
}
