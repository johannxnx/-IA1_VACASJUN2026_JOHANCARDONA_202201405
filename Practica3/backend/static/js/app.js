// Logica principal del panel administrativo SmartInvoice
// Maneja la navegacion, carga de datos desde la API y renderizado de tablas y modales

// ─── INICIALIZACION ──────────────────────────────────────────────────────
// Se ejecuta cuando el DOM termina de cargar
document.addEventListener('DOMContentLoaded', () => {
  // Si no hay token en localStorage, redirige al login inmediatamente
  if (!getToken()) { logout(); return; }

  // Muestra el nombre, rol e inicial del usuario en la barra lateral
  const user = getUser();
  if (user) {
    document.getElementById('user-name').textContent = user.nombre || user.email;
    document.getElementById('user-role').textContent = user.rol || 'Admin';
    document.getElementById('user-avatar').textContent = (user.nombre || user.email)[0].toUpperCase();
  }

  // Muestra el contenedor principal (estaba oculto para evitar flash antes de autenticar)
  document.getElementById('app').style.display = 'flex';

  // Navega a la seccion de inicio por defecto
  navigate('home');
});

// ─── NAVEGACION ──────────────────────────────────────────────────────────
function navigate(section) {
  // Oculta todas las secciones y desactiva todos los items del menu
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  // Activa la seccion y el item de menu correspondiente
  document.getElementById(`sec-${section}`)?.classList.add('active');
  document.querySelector(`[data-nav="${section}"]`)?.classList.add('active');

  // Actualiza el titulo en la barra superior
  document.getElementById('topbar-title').textContent = {
    home: 'Panel Principal', facturas: 'Facturas', proveedores: 'Proveedores',
    bitacora: 'Bitacora', reportes: 'Reportes',
  }[section] || '';

  // Dispara la carga de datos de la seccion activa
  const loaders = { home: loadHome, facturas: loadFacturas, proveedores: loadProveedores, bitacora: loadBitacora, reportes: loadReportes };
  loaders[section]?.();
}

// ─── PANEL PRINCIPAL ─────────────────────────────────────────────────────
async function loadHome() {
  // Obtiene todas las facturas y calcula las estadisticas del panel
  const facturas = await API.getFacturas() || [];
  const total    = facturas.length;
  const proc     = facturas.filter(f => f.estado === 'Procesado').length;
  const pend     = facturas.filter(f => f.estado === 'Pendiente').length;
  const err      = facturas.filter(f => f.estado === 'Error' || f.estado === 'Rechazado').length;
  const monto    = facturas.reduce((a, f) => a + parseFloat(f.total || 0), 0);

  // Actualiza las tarjetas de estadisticas en el panel
  document.getElementById('stat-total').textContent = total;
  document.getElementById('stat-proc').textContent  = proc;
  document.getElementById('stat-pend').textContent  = pend;
  document.getElementById('stat-err').textContent   = err;
  document.getElementById('stat-monto').textContent = `Q ${monto.toLocaleString('es-GT', {minimumFractionDigits:2})}`;

  // Muestra las 6 facturas mas recientes en la tabla de actividad
  const tb = document.getElementById('home-recent');
  const recent = facturas.slice(0, 6);
  tb.innerHTML = recent.length ? recent.map(f => `
    <tr>
      <td><span class="badge badge-${f.estado.toLowerCase()}">${f.estado}</span></td>
      <td>${f.archivo_nombre}</td>
      <td>${f.numero_factura || '<span style="color:var(--text3)">—</span>'}</td>
      <td>${f.total ? 'Q ' + parseFloat(f.total).toFixed(2) : '<span style="color:var(--text3)">—</span>'}</td>
      <td style="color:var(--text3);font-size:12px">${fmtDate(f.creado_en)}</td>
    </tr>`).join('') : `<tr><td colspan="5" class="empty"><i class="fa-solid fa-inbox"></i><p>Sin facturas</p></td></tr>`;
}

// ─── FACTURAS ────────────────────────────────────────────────────────────
async function loadFacturas() {
  // Carga la lista completa de facturas desde la API
  const facturas = await API.getFacturas() || [];
  renderFacturasTable(facturas);
}

function renderFacturasTable(facturas) {
  // Construye dinamicamente las filas de la tabla de facturas
  const tb = document.getElementById('facturas-table');
  tb.innerHTML = facturas.length ? facturas.map(f => `
    <tr>
      <td style="color:var(--text3);font-size:12px">#${f.id}</td>
      <td>
        <div style="font-size:13px;font-weight:500">${f.archivo_nombre}</div>
        <div style="font-size:11px;color:var(--text3)">${f.archivo_tipo?.toUpperCase() || ''}</div>
      </td>
      <td>${f.numero_factura || '<span style="color:var(--text3)">—</span>'}</td>
      <td>${f.fecha_factura || '<span style="color:var(--text3)">—</span>'}</td>
      <td style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px" title="${f.nombre_proveedor_ocr || ''}">${f.nombre_proveedor_ocr || '<span style="color:var(--text3)">—</span>'}</td>
      <td>${f.total ? '<span style="color:var(--green);font-weight:600">Q ' + parseFloat(f.total).toFixed(2) + '</span>' : '<span style="color:var(--text3)">—</span>'}</td>
      <td><span class="badge badge-${f.estado.toLowerCase()}">${f.estado}</span></td>
      <td style="color:var(--text3);font-size:12px">${fmtDate(f.creado_en)}</td>
      <td>
        <button class="btn-icon" onclick="verFactura(${f.id})" title="Ver detalle"><i class="fa-solid fa-eye"></i></button>
        <button class="btn-icon" onclick="eliminarFactura(${f.id})" title="Eliminar" style="margin-left:4px"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>`).join('') : `<tr><td colspan="9"><div class="empty"><i class="fa-solid fa-file-invoice"></i><p>No hay facturas cargadas</p></div></td></tr>`;
}

// Zona de carga de archivos: soporta clic y arrastrar y soltar (drag & drop)
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

dropZone?.addEventListener('click', () => fileInput.click());
dropZone?.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag'); });
dropZone?.addEventListener('dragleave', () => dropZone.classList.remove('drag'));
dropZone?.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag');
  if (e.dataTransfer.files[0]) uploadFile(e.dataTransfer.files[0]);
});
fileInput?.addEventListener('change', () => { if (fileInput.files[0]) uploadFile(fileInput.files[0]); });

async function uploadFile(file) {
  // Valida el tipo MIME del archivo en el cliente antes de enviarlo al servidor
  const allowed = ['application/pdf','image/jpeg','image/jpg','image/png'];
  if (!allowed.includes(file.type)) { toast('Formato no permitido. Use PDF, JPG o PNG', 'err'); return; }

  // Muestra la barra de progreso animada mientras se envia el archivo
  const prog = document.getElementById('upload-progress');
  const fill = document.getElementById('progress-fill');
  const res  = document.getElementById('upload-result');
  prog.style.display = 'block'; res.style.display = 'none';
  fill.style.width = '0%';

  // Simula avance de progreso hasta 85% mientras espera la respuesta del servidor
  let w = 0;
  const iv = setInterval(() => { w = Math.min(w + 8, 85); fill.style.width = w + '%'; }, 120);

  // Envia el archivo al endpoint de carga usando multipart/form-data
  const fd = new FormData();
  fd.append('file', file);
  const data = await API.uploadFactura(fd);

  clearInterval(iv);
  fill.style.width = '100%';
  setTimeout(() => {
    prog.style.display = 'none';
    res.style.display = 'block';
    if (data?.id) {
      res.className = 'upload-result ok';
      res.innerHTML = `<i class="fa-solid fa-circle-check"></i> Factura #${data.id} cargada. Procesando con OCR...`;
      fileInput.value = '';
      toast('Factura enviada para procesamiento', 'ok');
      // Recarga la tabla de facturas despues de 3 segundos para mostrar el resultado del OCR
      setTimeout(loadFacturas, 3000);
    } else {
      res.className = 'upload-result err';
      res.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Error al cargar. Intenta de nuevo.`;
    }
  }, 400);
}

async function verFactura(id) {
  // Obtiene el detalle completo de la factura incluyendo el texto crudo del OCR
  const f = await API.getFactura(id);
  if (!f) return;

  // Construye el contenido del modal con todos los campos extraidos
  document.getElementById('detail-content').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
      ${field('Archivo', f.archivo_nombre)}
      ${field('Tipo', f.archivo_tipo?.toUpperCase())}
      ${field('N Factura', f.numero_factura)}
      ${field('Fecha', f.fecha_factura)}
      ${field('Proveedor', f.nombre_proveedor_ocr)}
      ${field('Subtotal', f.subtotal ? 'Q ' + parseFloat(f.subtotal).toFixed(2) : null)}
      ${field('Impuestos', f.impuestos ? 'Q ' + parseFloat(f.impuestos).toFixed(2) : null)}
      ${field('Total', f.total ? 'Q ' + parseFloat(f.total).toFixed(2) : null)}
      ${field('Confianza OCR', f.confianza_ocr ? f.confianza_ocr + '%' : null)}
      ${field('Estado', `<span class="badge badge-${f.estado.toLowerCase()}">${f.estado}</span>`)}
      ${field('Procesado', fmtDate(f.procesado_en))}
    </div>
    ${f.datos_crudos ? `<div style="margin-top:16px">
      <div class="field-label">Texto extraido (OCR)</div>
      <pre style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:12px;
        font-size:11px;color:var(--text2);white-space:pre-wrap;max-height:160px;overflow-y:auto">${f.datos_crudos}</pre>
    </div>` : ''}`;
  openModal('modal-detail');
}

// Genera un elemento HTML de campo etiqueta-valor para el modal de detalle
function field(label, val) {
  return `<div><div class="field-label">${label}</div>
    <div style="font-size:13px;color:${val ? 'var(--text)' : 'var(--text3)'}">${val || '—'}</div></div>`;
}

async function eliminarFactura(id) {
  if (!confirm('Eliminar esta factura?')) return;
  await API.deleteFactura(id);
  toast('Factura eliminada', 'ok');
  loadFacturas();
}

// Busqueda en tiempo real: filtra las facturas por nombre de archivo, numero o estado
document.getElementById('search-facturas')?.addEventListener('input', async function() {
  const q = this.value.toLowerCase();
  const facturas = (await API.getFacturas() || []).filter(f =>
    f.archivo_nombre?.toLowerCase().includes(q) || f.numero_factura?.toLowerCase().includes(q) || f.estado?.toLowerCase().includes(q)
  );
  renderFacturasTable(facturas);
});

// ─── PROVEEDORES ─────────────────────────────────────────────────────────
let editProveedor = null;  // Almacena el proveedor en edicion; null cuando se crea uno nuevo

async function loadProveedores() {
  const list = await API.getProveedores() || [];
  renderProveedoresTable(list);
}

function renderProveedoresTable(list) {
  // Construye la tabla de proveedores con botones de edicion y eliminacion
  const tb = document.getElementById('proveedores-table');
  tb.innerHTML = list.length ? list.map(p => `
    <tr>
      <td style="color:var(--text3);font-size:12px">#${p.id}</td>
      <td><div style="font-weight:500">${p.nombre}</div></td>
      <td style="font-family:monospace;font-size:12px;color:var(--accent)">${p.nit}</td>
      <td style="color:var(--text2);font-size:12px">${p.email || '—'}</td>
      <td style="color:var(--text2);font-size:12px">${p.telefono || '—'}</td>
      <td><span style="font-size:11px;padding:3px 10px;border-radius:20px;background:${p.activo?'rgba(16,185,129,.12)':'rgba(239,68,68,.12)'};color:${p.activo?'var(--green)':'var(--red)'}">${p.activo?'Activo':'Inactivo'}</span></td>
      <td>
        <button class="btn-icon" onclick="abrirEditarProveedor(${p.id})" title="Editar"><i class="fa-solid fa-pen"></i></button>
        <button class="btn-icon" onclick="eliminarProveedor(${p.id})" title="Eliminar" style="margin-left:4px"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>`).join('') : `<tr><td colspan="7"><div class="empty"><i class="fa-solid fa-building"></i><p>No hay proveedores registrados</p></div></td></tr>`;
}

function abrirCrearProveedor() {
  // Limpia el formulario del modal para ingresar un nuevo proveedor
  editProveedor = null;
  document.getElementById('prov-modal-title').textContent = 'Nuevo Proveedor';
  document.getElementById('form-proveedor').reset();
  openModal('modal-proveedor');
}

async function abrirEditarProveedor(id) {
  // Precarga los datos del proveedor en el formulario del modal para edicion
  const list = await API.getProveedores() || [];
  const p = list.find(x => x.id === id);
  if (!p) return;
  editProveedor = p;
  document.getElementById('prov-modal-title').textContent = 'Editar Proveedor';
  document.getElementById('prov-nombre').value   = p.nombre || '';
  document.getElementById('prov-nit').value      = p.nit || '';
  document.getElementById('prov-email').value    = p.email || '';
  document.getElementById('prov-telefono').value = p.telefono || '';
  document.getElementById('prov-direccion').value= p.direccion || '';
  openModal('modal-proveedor');
}

// Manejo del envio del formulario de proveedor: crea o actualiza segun editProveedor
document.getElementById('form-proveedor')?.addEventListener('submit', async e => {
  e.preventDefault();
  const data = {
    nombre:    document.getElementById('prov-nombre').value,
    nit:       document.getElementById('prov-nit').value,
    email:     document.getElementById('prov-email').value || null,
    telefono:  document.getElementById('prov-telefono').value || null,
    direccion: document.getElementById('prov-direccion').value || null,
  };
  // Si editProveedor tiene valor, actualiza; si es null, crea uno nuevo
  const result = editProveedor
    ? await API.updateProveedor(editProveedor.id, data)
    : await API.createProveedor(data);

  if (result?.id || result) {
    closeModal('modal-proveedor');
    toast(editProveedor ? 'Proveedor actualizado' : 'Proveedor creado', 'ok');
    loadProveedores();
  } else {
    toast('Error al guardar proveedor', 'err');
  }
});

async function eliminarProveedor(id) {
  // Realiza baja logica del proveedor (se desactiva, no se elimina fisicamente)
  if (!confirm('Desactivar este proveedor?')) return;
  await API.deleteProveedor(id);
  toast('Proveedor desactivado', 'ok');
  loadProveedores();
}

// Busqueda en tiempo real de proveedores por nombre o NIT
document.getElementById('search-proveedores')?.addEventListener('input', async function() {
  const q = this.value.toLowerCase();
  const list = (await API.getProveedores() || []).filter(p =>
    p.nombre?.toLowerCase().includes(q) || p.nit?.toLowerCase().includes(q)
  );
  renderProveedoresTable(list);
});

// ─── BITACORA ────────────────────────────────────────────────────────────
async function loadBitacora() {
  const logs = await API.getBitacora() || [];
  const tb = document.getElementById('bitacora-table');
  tb.innerHTML = logs.length ? logs.map(l => {
    // Para registros de RPA que tienen screenshot guardado, muestra un enlace "Ver evidencia"
    // El nombre del screenshot esta en detalle_error para rpa_registro
    const evidenciaBtn = (l.accion === 'rpa_registro' && l.detalle_error)
      ? `<a href="/uploads/${l.detalle_error}" target="_blank"
           style="margin-left:8px;font-size:11px;color:var(--accent);text-decoration:none;
                  border:1px solid var(--accent);border-radius:4px;padding:1px 6px">
           <i class="fa-solid fa-image"></i> Ver evidencia
         </a>`
      : '';
    return `
    <tr>
      <td style="color:var(--text3);font-size:12px">${fmtDate(l.fecha_hora)}</td>
      <td><code style="font-size:12px;background:var(--bg);padding:2px 7px;border-radius:4px;color:var(--accent)">${l.accion || '—'}</code></td>
      <td style="font-size:12px;color:var(--text2)">${l.documento || '—'}</td>
      <td><span class="badge badge-${(l.estado||'').toLowerCase()}">${l.estado || '—'}</span></td>
      <td style="font-size:12px;color:var(--text2);max-width:260px;overflow:hidden;text-overflow:ellipsis">
        ${l.resultado || '—'}${evidenciaBtn}
      </td>
      <td style="color:var(--text3);font-size:12px">${l.usuario_id ? '#' + l.usuario_id : '—'}</td>
    </tr>`;
  }).join('') : `<tr><td colspan="6"><div class="empty"><i class="fa-solid fa-list-check"></i><p>Sin registros en bitacora</p></div></td></tr>`;
}

// ─── REPORTES ────────────────────────────────────────────────────────────
// Variable que almacena el tipo de reporte seleccionado por el usuario: pdf, excel o csv
let selectedReportType = 'pdf';

// Manejo de la seleccion visual de tipo de reporte en el panel
document.querySelectorAll('.report-opt').forEach(opt => {
  opt.addEventListener('click', () => {
    document.querySelectorAll('.report-opt').forEach(o => o.classList.remove('selected'));
    opt.classList.add('selected');
    selectedReportType = opt.dataset.type;
  });
});

async function loadReportes() {
  // Carga y renderiza la lista de reportes generados con botones de descarga
  const list = await API.getReportes() || [];
  const tb = document.getElementById('reportes-table');
  tb.innerHTML = list.length ? list.map(r => `
    <tr>
      <td style="color:var(--text3);font-size:12px">#${r.id}</td>
      <td style="font-size:13px">${r.nombre}</td>
      <td><span style="font-size:11px;padding:3px 10px;border-radius:20px;font-weight:600;
        background:${r.tipo==='pdf'?'rgba(239,68,68,.12)':r.tipo==='excel'?'rgba(16,185,129,.12)':'rgba(245,158,11,.12)'};
        color:${r.tipo==='pdf'?'var(--red)':r.tipo==='excel'?'var(--green)':'var(--yellow)'}">
        ${r.tipo.toUpperCase()}</span></td>
      <td style="color:var(--text3);font-size:12px">${fmtDate(r.creado_en)}</td>
      <td><span style="font-size:11px;padding:3px 10px;border-radius:20px;
        background:${r.enviado_email?'rgba(16,185,129,.12)':'rgba(100,116,139,.1)'};
        color:${r.enviado_email?'var(--green)':'var(--text3)'}">
        ${r.enviado_email?'<i class="fa-solid fa-check"></i> Enviado':'Pendiente'}</span></td>
      <td>
        <button class="btn btn-ghost btn-sm" onclick="descargarReporte(${r.id}, '${r.nombre}')">
          <i class="fa-solid fa-download"></i> Descargar
        </button>
      </td>
    </tr>`).join('') : `<tr><td colspan="6"><div class="empty"><i class="fa-solid fa-chart-bar"></i><p>No se han generado reportes</p></div></td></tr>`;
}

// Envia la solicitud de generacion de reporte con el tipo seleccionado y el email opcional
document.getElementById('btn-generar-reporte')?.addEventListener('click', async () => {
  const email = document.getElementById('report-email').value || null;
  const btn = document.getElementById('btn-generar-reporte');
  btn.disabled = true;
  btn.innerHTML = '<span class="loader"></span> Generando...';
  const r = await API.generarReporte(selectedReportType, email);
  btn.disabled = false;
  btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Generar Reporte';
  if (r?.mensaje) {
    toast(r.mensaje, 'ok');
    // Recarga la lista de reportes despues de 3 segundos para que aparezca el nuevo
    setTimeout(loadReportes, 3000);
  } else {
    toast('Error al generar reporte', 'err');
  }
});

// ─── MODALES ─────────────────────────────────────────────────────────────
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

// Cierra el modal al hacer clic fuera del contenido del modal
document.querySelectorAll('.modal-overlay').forEach(m => {
  m.addEventListener('click', e => { if (e.target === m) m.classList.remove('open'); });
});
document.querySelectorAll('.modal-close').forEach(btn => {
  btn.addEventListener('click', () => btn.closest('.modal-overlay')?.classList.remove('open'));
});

// ─── TOASTS ──────────────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  // Muestra una notificacion temporal en la esquina inferior de la pantalla
  // type: 'ok' para exito (verde), 'err' para error (rojo), 'info' para informacion (azul)
  const wrap = document.getElementById('toast-wrap');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<i class="fa-solid ${type==='ok'?'fa-circle-check':type==='err'?'fa-circle-xmark':'fa-circle-info'}"></i> ${msg}`;
  wrap.appendChild(el);
  // Elimina el toast despues de 3.5 segundos con animacion de salida
  setTimeout(() => { el.classList.add('removing'); setTimeout(() => el.remove(), 250); }, 3500);
}

async function descargarReporte(id, nombre) {
  // Descarga un reporte enviando el token JWT en el encabezado Authorization
  // No se puede usar un enlace <a href> directo porque el endpoint requiere autenticacion
  const token = localStorage.getItem('si_token');
  const resp = await fetch(`/api/reportes/${id}/descargar`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!resp.ok) { toast('Error al descargar reporte', 'err'); return; }

  // Convierte la respuesta a Blob y crea una URL temporal para forzar la descarga
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = nombre;
  a.click();
  // Libera la URL temporal del objeto Blob despues de usarla
  URL.revokeObjectURL(url);
}

// ─── UTILIDADES ──────────────────────────────────────────────────────────
function fmtDate(iso) {
  // Formatea una fecha ISO a formato legible en locale guatemalteco
  // Ejemplo: "19 jun 2026, 05:38 p. m."
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('es-GT', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
}
