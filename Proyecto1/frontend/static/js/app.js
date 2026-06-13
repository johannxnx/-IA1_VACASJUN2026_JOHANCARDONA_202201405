// ============================================================
// Doctor Byte - Logica del frontend
// ============================================================

const API = "http://localhost:5000/api";

// Estado de la aplicacion
const state = {
  sintomas: [],          // Lista completa de sintomas del servidor
  seleccionados: new Set() // IDs de sintomas seleccionados por el usuario
};

// ============================================================
// INICIALIZACION
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
  initNav();
  cargarSintomas();
  initAdmin();

  document.getElementById("btn-diagnosticar").addEventListener("click", ejecutarDiagnostico);
  document.getElementById("btn-limpiar").addEventListener("click", limpiarSeleccion);
  document.getElementById("search-input").addEventListener("input", filtrarSintomas);
});

// ============================================================
// NAVEGACION ENTRE SECCIONES
// ============================================================

function initNav() {
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const seccion = btn.dataset.section;

      document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById(`section-${seccion}`).classList.add("active");

      if (seccion === "historial") cargarHistorial();
      if (seccion === "admin") cargarAdmin();
    });
  });
}

// ============================================================
// SINTOMAS
// ============================================================

async function cargarSintomas() {
  try {
    const res = await fetch(`${API}/sintomas`);
    const data = await res.json();

    if (!data.ok) throw new Error(data.error);

    state.sintomas = data.sintomas;
    renderSintomas(state.sintomas);
  } catch (err) {
    document.getElementById("sintomas-grid").innerHTML =
      `<div class="error-state">Error al cargar sintomas: ${err.message}</div>`;
  }
}

function renderSintomas(lista) {
  const grid = document.getElementById("sintomas-grid");

  if (lista.length === 0) {
    grid.innerHTML = `<div class="empty-state"><p>No se encontraron sintomas.</p></div>`;
    return;
  }

  grid.innerHTML = lista.map((s, idx) => `
    <div
      class="sintoma-card ${state.seleccionados.has(s.id) ? "selected" : ""}"
      data-id="${s.id}"
      style="animation-delay: ${idx * 30}ms"
      role="checkbox"
      aria-checked="${state.seleccionados.has(s.id)}"
      tabindex="0"
    >
      <div class="sintoma-check">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </div>
      <span class="sintoma-label">${s.descripcion}</span>
    </div>
  `).join("");

  // Attach events a cada tarjeta
  grid.querySelectorAll(".sintoma-card").forEach(card => {
    card.addEventListener("click", () => toggleSintoma(card.dataset.id));
    card.addEventListener("keydown", e => {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        toggleSintoma(card.dataset.id);
      }
    });
  });
}

function toggleSintoma(id) {
  if (state.seleccionados.has(id)) {
    state.seleccionados.delete(id);
  } else {
    state.seleccionados.add(id);
  }
  actualizarUI();
}

function actualizarUI() {
  // Actualiza estado visual de cada tarjeta
  document.querySelectorAll(".sintoma-card").forEach(card => {
    const sel = state.seleccionados.has(card.dataset.id);
    card.classList.toggle("selected", sel);
    card.setAttribute("aria-checked", sel);
  });

  // Contador y boton
  const n = state.seleccionados.size;
  document.getElementById("counter").textContent = n;
  document.getElementById("btn-diagnosticar").disabled = n === 0;
}

function limpiarSeleccion() {
  state.seleccionados.clear();
  actualizarUI();
  document.getElementById("resultado-container").classList.add("hidden");
  document.getElementById("search-input").value = "";
  filtrarSintomas();
}

function filtrarSintomas() {
  const termino = document.getElementById("search-input").value.toLowerCase().trim();
  const filtrados = state.sintomas.filter(s =>
    s.descripcion.toLowerCase().includes(termino)
  );
  renderSintomas(filtrados);
}

// ============================================================
// DIAGNOSTICO
// ============================================================

async function ejecutarDiagnostico() {
  const sintomas = Array.from(state.seleccionados);
  const btn = document.getElementById("btn-diagnosticar");

  // Estado de carga en el boton
  btn.classList.add("loading");
  btn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
    </svg>
    Analizando...
  `;

  try {
    const res = await fetch(`${API}/diagnostico`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sintomas })
    });

    const data = await res.json();
    if (!data.ok) throw new Error(data.error);

    mostrarResultado(data);
    mostrarToast("Diagnostico completado. Notificacion enviada a Telegram.");

  } catch (err) {
    mostrarToast(`Error: ${err.message}`, true);
  } finally {
    btn.classList.remove("loading");
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
      </svg>
      Analizar sintomas
    `;
  }
}

function mostrarResultado(data) {
  const container = document.getElementById("resultado-container");
  const body = document.getElementById("resultado-body");
  const ts = document.getElementById("resultado-timestamp");

  ts.textContent = formatearFecha(data.timestamp);

  if (!data.diagnosticos || data.diagnosticos.length === 0) {
    body.innerHTML = `
      <div class="no-diagnostico">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <p>No se encontro un diagnostico para la combinacion de sintomas seleccionada.</p>
        <p style="margin-top:8px; font-size:0.8rem;">Intenta agregar mas sintomas.</p>
      </div>
    `;
  } else {
    body.innerHTML = data.diagnosticos.map((d, i) => `
      <div class="diagnostico-card" style="animation-delay: ${i * 80}ms">
        <div class="diag-falla">${d.descripcion}</div>
        <div class="diag-recs-title">Recomendaciones</div>
        <ul class="diag-recs">
          ${d.recomendaciones.map(r => `<li>${r}</li>`).join("")}
        </ul>
      </div>
    `).join("");
  }

  container.classList.remove("hidden");
  // Scroll suave al resultado
  container.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ============================================================
// HISTORIAL
// ============================================================

async function cargarHistorial() {
  const container = document.getElementById("historial-container");
  container.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Cargando historial...</p></div>`;

  try {
    const res = await fetch(`${API}/historial`);
    const data = await res.json();

    if (!data.ok) throw new Error(data.error);

    if (data.historial.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"/>
          </svg>
          <p>Aun no hay diagnosticos en el historial.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = data.historial.map((entrada, i) =>
      renderHistorialItem(entrada, i)
    ).join("");

    // Colapsar/expandir
    container.querySelectorAll(".historial-item-header").forEach(header => {
      header.addEventListener("click", () => {
        header.parentElement.classList.toggle("open");
      });
    });

  } catch (err) {
    container.innerHTML = `<div class="error-state">Error al cargar historial: ${err.message}</div>`;
  }
}

function renderHistorialItem(entrada, idx) {
  const tieneDiag = entrada.diagnosticos && entrada.diagnosticos.length > 0;
  const badgeClass = tieneDiag ? "tiene-diag" : "sin-diag";
  const badgeText = tieneDiag
    ? `${entrada.diagnosticos.length} falla${entrada.diagnosticos.length > 1 ? "s" : ""} detectada${entrada.diagnosticos.length > 1 ? "s" : ""}`
    : "Sin diagnostico";

  const sintomaTags = entrada.sintomas
    .map(s => `<span class="sintoma-tag">${s.replace(/_/g, " ")}</span>`)
    .join("");

  const diagsHTML = tieneDiag
    ? entrada.diagnosticos.map(d => `
        <div class="diagnostico-card" style="margin-top: 12px;">
          <div class="diag-falla">${d.descripcion}</div>
          <ul class="diag-recs">
            ${d.recomendaciones.map(r => `<li>${r}</li>`).join("")}
          </ul>
        </div>
      `).join("")
    : `<p style="color:var(--text-secondary); font-size:0.875rem; padding-top:12px;">No se encontraron diagnosticos para estos sintomas.</p>`;

  return `
    <div class="historial-item" style="animation-delay: ${idx * 50}ms">
      <div class="historial-item-header">
        <div class="historial-meta">
          <span class="historial-ts">${formatearFecha(entrada.timestamp)}</span>
          <span class="historial-badge ${badgeClass}">${badgeText}</span>
          <div class="historial-sintomas">${sintomaTags}</div>
        </div>
        <svg class="historial-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>
      <div class="historial-body">${diagsHTML}</div>
    </div>
  `;
}

// ============================================================
// UTILIDADES
// ============================================================

function formatearFecha(isoString) {
  const d = new Date(isoString);
  return d.toLocaleString("es-GT", {
    year: "numeric", month: "short", day: "2-digit",
    hour: "2-digit", minute: "2-digit"
  });
}

let toastTimeout = null;

// ============================================================
// ADMIN
// ============================================================

const adminState = { sintomas: [], fallas: [], recomendaciones: {}, reglas: [], editingRuleId: null };

function initAdmin() {
  document.querySelectorAll(".admin-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".admin-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".admin-panel").forEach(p => { p.classList.remove("active"); p.classList.add("hidden"); });
      tab.classList.add("active");
      const panel = document.getElementById(`admin-tab-${tab.dataset.tab}`);
      panel.classList.remove("hidden");
      panel.classList.add("active");
    });
  });

  // SINTOMAS
  document.getElementById("btn-add-sintoma").addEventListener("click", () => {
    document.getElementById("sintoma-id").value = "";
    document.getElementById("sintoma-desc").value = "";
    document.getElementById("sintoma-id").removeAttribute("disabled");
    document.getElementById("form-sintoma").classList.remove("hidden");
  });
  document.getElementById("btn-cancel-sintoma").addEventListener("click", () =>
    document.getElementById("form-sintoma").classList.add("hidden"));
  document.getElementById("btn-save-sintoma").addEventListener("click", saveSintoma);

  // FALLAS
  document.getElementById("btn-add-falla").addEventListener("click", () => {
    document.getElementById("falla-id").value = "";
    document.getElementById("falla-desc").value = "";
    document.getElementById("falla-id").removeAttribute("disabled");
    document.getElementById("form-falla").classList.remove("hidden");
  });
  document.getElementById("btn-cancel-falla").addEventListener("click", () =>
    document.getElementById("form-falla").classList.add("hidden"));
  document.getElementById("btn-save-falla").addEventListener("click", saveFalla);

  // RECOMENDACIONES
  document.getElementById("rec-falla-select").addEventListener("change", renderRecLista);
  document.getElementById("btn-add-rec").addEventListener("click", addRecomendacion);

  // REGLAS
  document.getElementById("btn-add-regla").addEventListener("click", () => {
    adminState.editingRuleId = null;
    document.getElementById("form-regla").classList.remove("hidden");
    renderConditionsGrid([]);
  });
  document.getElementById("btn-cancel-regla").addEventListener("click", () =>
    document.getElementById("form-regla").classList.add("hidden"));
  document.getElementById("btn-save-regla").addEventListener("click", saveRegla);

  // BOT
  document.getElementById("btn-toggle-bot").addEventListener("click", toggleBot);
  document.getElementById("btn-save-bot").addEventListener("click", saveBotConfig);
}

// --- Carga cuando se entra al admin ---
async function cargarAdmin() {
  const [sRes, fRes, rRes, rgRes, bRes] = await Promise.all([
    fetch(`${API}/admin/sintomas`).then(r => r.json()),
    fetch(`${API}/admin/fallas`).then(r => r.json()),
    fetch(`${API}/admin/recomendaciones`).then(r => r.json()),
    fetch(`${API}/admin/reglas`).then(r => r.json()),
    fetch(`${API}/admin/bot-config`).then(r => r.json()),
  ]);
  adminState.sintomas = sRes.sintomas || [];
  adminState.fallas   = fRes.fallas   || [];
  adminState.recomendaciones = rRes.recomendaciones || {};
  adminState.reglas   = rgRes.reglas  || [];

  renderTablaSintomas();
  renderTablaFallas();
  renderRecSelect();
  renderTablaReglas();
  renderBotConfig(bRes.config || {});
}

// ---- SINTOMAS ----
function renderTablaSintomas() {
  const wrap = document.getElementById("tabla-sintomas");
  if (!adminState.sintomas.length) { wrap.innerHTML = "<p style='color:var(--text-secondary);padding:1rem'>No hay sintomas.</p>"; return; }
  wrap.innerHTML = `<table class="admin-table">
    <thead><tr><th>ID</th><th>Descripcion</th><th></th></tr></thead>
    <tbody>${adminState.sintomas.map(s => `
      <tr>
        <td class="id-cell">${s.id}</td>
        <td>${s.descripcion}</td>
        <td class="actions-cell">
          <button class="btn-icon" onclick="editSintoma('${s.id}','${s.descripcion.replace(/'/g,"\\'")}')">Editar</button>
          <button class="btn-icon danger" onclick="deleteSintoma('${s.id}')">Eliminar</button>
        </td>
      </tr>`).join("")}
    </tbody></table>`;
}

function editSintoma(id, desc) {
  document.getElementById("sintoma-id").value = id;
  document.getElementById("sintoma-id").setAttribute("disabled", true);
  document.getElementById("sintoma-desc").value = desc;
  document.getElementById("form-sintoma").classList.remove("hidden");
}

async function saveSintoma() {
  const id   = document.getElementById("sintoma-id").value.trim();
  const desc = document.getElementById("sintoma-desc").value.trim();
  if (!id || !desc) { mostrarToast("Completa los campos", true); return; }
  const esEdicion = document.getElementById("sintoma-id").disabled;
  const method = esEdicion ? "PUT" : "POST";
  const url = esEdicion ? `${API}/admin/sintomas/${id}` : `${API}/admin/sintomas`;
  const body = esEdicion ? { descripcion: desc } : { id, descripcion: desc };
  const res = await fetch(url, { method, headers: {"Content-Type":"application/json"}, body: JSON.stringify(body) }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  document.getElementById("form-sintoma").classList.add("hidden");
  mostrarToast("Sintoma guardado correctamente.");
  await cargarAdmin();
}

async function deleteSintoma(id) {
  if (!confirm(`Eliminar sintoma "${id}"?`)) return;
  const res = await fetch(`${API}/admin/sintomas/${id}`, { method: "DELETE" }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  mostrarToast("Sintoma eliminado.");
  await cargarAdmin();
}

// ---- FALLAS ----
function renderTablaFallas() {
  const wrap = document.getElementById("tabla-fallas");
  if (!adminState.fallas.length) { wrap.innerHTML = "<p style='color:var(--text-secondary);padding:1rem'>No hay fallas.</p>"; return; }
  wrap.innerHTML = `<table class="admin-table">
    <thead><tr><th>ID</th><th>Descripcion</th><th></th></tr></thead>
    <tbody>${adminState.fallas.map(f => `
      <tr>
        <td class="id-cell">${f.id}</td>
        <td>${f.descripcion}</td>
        <td class="actions-cell">
          <button class="btn-icon" onclick="editFalla('${f.id}','${f.descripcion.replace(/'/g,"\\'")}')">Editar</button>
          <button class="btn-icon danger" onclick="deleteFalla('${f.id}')">Eliminar</button>
        </td>
      </tr>`).join("")}
    </tbody></table>`;
}

function editFalla(id, desc) {
  document.getElementById("falla-id").value = id;
  document.getElementById("falla-id").setAttribute("disabled", true);
  document.getElementById("falla-desc").value = desc;
  document.getElementById("form-falla").classList.remove("hidden");
}

async function saveFalla() {
  const id   = document.getElementById("falla-id").value.trim();
  const desc = document.getElementById("falla-desc").value.trim();
  if (!id || !desc) { mostrarToast("Completa los campos", true); return; }
  const esEdicion = document.getElementById("falla-id").disabled;
  const method = esEdicion ? "PUT" : "POST";
  const url = esEdicion ? `${API}/admin/fallas/${id}` : `${API}/admin/fallas`;
  const body = esEdicion ? { descripcion: desc } : { id, descripcion: desc };
  const res = await fetch(url, { method, headers: {"Content-Type":"application/json"}, body: JSON.stringify(body) }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  document.getElementById("form-falla").classList.add("hidden");
  mostrarToast("Falla guardada correctamente.");
  await cargarAdmin();
}

async function deleteFalla(id) {
  if (!confirm(`Eliminar falla "${id}" y sus reglas asociadas?`)) return;
  const res = await fetch(`${API}/admin/fallas/${id}`, { method: "DELETE" }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  mostrarToast("Falla eliminada.");
  await cargarAdmin();
}

// ---- RECOMENDACIONES ----
function renderRecSelect() {
  const sel = document.getElementById("rec-falla-select");
  sel.innerHTML = adminState.fallas.map(f => `<option value="${f.id}">${f.id}</option>`).join("");
  renderRecLista();
}

function renderRecLista() {
  const faultId = document.getElementById("rec-falla-select").value;
  const lista = adminState.recomendaciones[faultId] || [];
  const wrap = document.getElementById("rec-lista");
  wrap.innerHTML = lista.map((r, i) => `
    <div class="rec-item">
      <span>${r}</span>
      <button class="btn-icon danger" onclick="deleteRec('${faultId}',${i})">x</button>
    </div>`).join("") || "<p style='color:var(--text-secondary);font-size:.85rem'>Sin recomendaciones.</p>";
}

async function addRecomendacion() {
  const faultId = document.getElementById("rec-falla-select").value;
  const texto   = document.getElementById("rec-nueva").value.trim();
  if (!texto) return;
  const lista = [...(adminState.recomendaciones[faultId] || []), texto];
  const res = await fetch(`${API}/admin/recomendaciones/${faultId}`, {
    method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ lista })
  }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  document.getElementById("rec-nueva").value = "";
  mostrarToast("Recomendacion agregada.");
  await cargarAdmin();
  document.getElementById("rec-falla-select").value = faultId;
  renderRecLista();
}

async function deleteRec(faultId, idx) {
  const lista = (adminState.recomendaciones[faultId] || []).filter((_, i) => i !== idx);
  const res = await fetch(`${API}/admin/recomendaciones/${faultId}`, {
    method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ lista })
  }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  mostrarToast("Recomendacion eliminada.");
  adminState.recomendaciones[faultId] = lista;
  renderRecLista();
}

// ---- REGLAS ----
function renderConditionsGrid(selectedConditions) {
  const wrap = document.getElementById("regla-conditions-wrap");
  const sel  = document.getElementById("regla-conclusion");
  sel.innerHTML = adminState.fallas.map(f => `<option value="${f.id}">${f.id}</option>`).join("");
  wrap.innerHTML = adminState.sintomas.map(s => `
    <label class="condition-check">
      <input type="checkbox" value="${s.id}" ${selectedConditions.includes(s.id) ? "checked" : ""} />
      ${s.id}
    </label>`).join("");
}

function renderTablaReglas() {
  const wrap = document.getElementById("tabla-reglas");
  if (!adminState.reglas.length) { wrap.innerHTML = "<p style='color:var(--text-secondary);padding:1rem'>No hay reglas.</p>"; return; }
  wrap.innerHTML = `<table class="admin-table">
    <thead><tr><th>ID</th><th>Si presentan</th><th>Diagnosticar</th><th></th></tr></thead>
    <tbody>${adminState.reglas.map(r => `
      <tr>
        <td class="id-cell">${r.id}</td>
        <td>${r.conditions.map(c => `<span class="sintoma-tag">${c}</span>`).join(" ")}</td>
        <td><span class="sintoma-tag" style="background:rgba(0,212,255,.1);border-color:rgba(0,212,255,.3);color:var(--accent)">${r.conclusion}</span></td>
        <td class="actions-cell">
          <button class="btn-icon" onclick="editRegla('${r.id}')">Editar</button>
          <button class="btn-icon danger" onclick="deleteRegla('${r.id}')">Eliminar</button>
        </td>
      </tr>`).join("")}
    </tbody></table>`;
}

function editRegla(id) {
  const regla = adminState.reglas.find(r => r.id === id);
  if (!regla) return;
  adminState.editingRuleId = id;
  renderConditionsGrid(regla.conditions);
  document.getElementById("regla-conclusion").value = regla.conclusion;
  document.getElementById("form-regla").classList.remove("hidden");
}

async function saveRegla() {
  const conclusion = document.getElementById("regla-conclusion").value;
  const conditions = Array.from(document.querySelectorAll("#regla-conditions-wrap input:checked")).map(cb => cb.value);
  if (!conditions.length) { mostrarToast("Selecciona al menos un sintoma", true); return; }

  const isEdit = !!adminState.editingRuleId;
  const url    = isEdit ? `${API}/admin/reglas/${adminState.editingRuleId}` : `${API}/admin/reglas`;
  const method = isEdit ? "PUT" : "POST";

  const res = await fetch(url, { method, headers: {"Content-Type":"application/json"}, body: JSON.stringify({ conclusion, conditions }) }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  document.getElementById("form-regla").classList.add("hidden");
  mostrarToast("Regla guardada.");
  await cargarAdmin();
}

async function deleteRegla(id) {
  if (!confirm("Eliminar esta regla?")) return;
  const res = await fetch(`${API}/admin/reglas/${id}`, { method: "DELETE" }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  mostrarToast("Regla eliminada.");
  await cargarAdmin();
}

// ---- BOT CONFIG ----
function renderBotConfig(cfg) {
  document.getElementById("bot-chat-id").value      = cfg.chat_id              || "";
  document.getElementById("bot-encabezado").value   = cfg.mensaje_encabezado  || "";
  document.getElementById("bot-msg-sin-diag").value = cfg.mensaje_sin_diagnostico || "";
  const enabled = cfg.enabled !== false;
  document.getElementById("bot-status-label").textContent = enabled ? "Activo" : "Inactivo";
  const btn = document.getElementById("btn-toggle-bot");
  btn.textContent = enabled ? "Desactivar" : "Activar";
  btn.classList.toggle("active", enabled);
  btn._enabled = enabled;
}

async function toggleBot() {
  const btn     = document.getElementById("btn-toggle-bot");
  const enabled = !btn._enabled;
  const res = await fetch(`${API}/admin/bot-config`, {
    method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ enabled })
  }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  renderBotConfig(res.config);
  mostrarToast(enabled ? "Bot activado." : "Bot desactivado.");
}

async function saveBotConfig() {
  const datos = {
    chat_id:                 document.getElementById("bot-chat-id").value.trim(),
    mensaje_encabezado:      document.getElementById("bot-encabezado").value.trim(),
    mensaje_sin_diagnostico: document.getElementById("bot-msg-sin-diag").value.trim(),
  };
  const res = await fetch(`${API}/admin/bot-config`, {
    method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(datos)
  }).then(r => r.json());
  if (!res.ok) { mostrarToast(res.error, true); return; }
  mostrarToast("Configuracion del bot guardada.");
}

function mostrarToast(mensaje, esError = false) {
  const toast = document.getElementById("toast");
  const msg = document.getElementById("toast-msg");

  msg.textContent = mensaje;
  toast.classList.remove("hidden", "error");
  if (esError) toast.classList.add("error");

  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.add("hidden"), 4000);
}
