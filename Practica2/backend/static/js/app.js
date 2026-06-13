'use strict';

// ── State ──────────────────────────────────────────────────
let authToken = localStorage.getItem('sb_token');
let allCategories = [];
let allQuestions  = [];
let allAnswers    = [];
let editingId     = null;

const SECTION_TITLES = {
    dashboard:  'Dashboard',
    categories: 'Categorías',
    questions:  'Preguntas',
    answers:    'Respuestas',
    config:     'Configuración del Bot',
    logs:       'Historial de Consultas',
};

// ── API helper ─────────────────────────────────────────────
async function api(method, path, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (authToken) opts.headers['Authorization'] = `Bearer ${authToken}`;
    if (body)      opts.body = JSON.stringify(body);

    let res;
    try {
        res = await fetch('/api' + path, opts);
    } catch {
        throw new Error('No se pudo conectar con el servidor');
    }

    if (res.status === 401) { logout(); throw new Error('Sesión expirada'); }
    if (res.status === 204) return null;

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error en la solicitud');
    return data;
}

// ── Toast ──────────────────────────────────────────────────
function showToast(msg, type = 'success') {
    const el   = document.getElementById('toast');
    const body = document.getElementById('toast-body');
    el.className = `toast align-items-center text-white border-0 bg-${type === 'success' ? 'success' : 'danger'}`;
    body.textContent = msg;
    new bootstrap.Toast(el, { delay: 3000 }).show();
}

// ── Helpers ────────────────────────────────────────────────
function escapeHtml(s) {
    if (!s) return '';
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function truncate(s, n = 70) {
    if (!s) return '';
    return s.length > n ? s.slice(0, n) + '…' : s;
}

// ── Auth ───────────────────────────────────────────────────
function init() {
    if (authToken) {
        showAdmin();
        navigate('dashboard');
    } else {
        showLogin();
    }
}

function showLogin() {
    document.getElementById('login-section').classList.remove('d-none');
    document.getElementById('admin-section').classList.add('d-none');
}

function showAdmin() {
    document.getElementById('login-section').classList.add('d-none');
    document.getElementById('admin-section').classList.remove('d-none');
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const btn      = document.getElementById('login-btn');
    const err      = document.getElementById('login-error');

    btn.disabled    = true;
    btn.innerHTML   = '<span class="spinner-border spinner-border-sm me-2"></span>Ingresando…';
    err.classList.add('d-none');

    try {
        const data  = await api('POST', '/auth/login', { username, password });
        authToken   = data.access_token;
        localStorage.setItem('sb_token', authToken);
        showAdmin();
        navigate('dashboard');
    } catch (error) {
        err.textContent = error.message;
        err.classList.remove('d-none');
    } finally {
        btn.disabled  = false;
        btn.innerHTML = 'Ingresar';
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('sb_token');
    showLogin();
}

// ── Navigation ─────────────────────────────────────────────
function navigate(section) {
    document.querySelectorAll('.section-content').forEach(el => el.classList.add('d-none'));
    document.querySelectorAll('#sidebar .nav-link').forEach(el => el.classList.remove('active'));

    const el  = document.getElementById(`section-${section}`);
    if (el) el.classList.remove('d-none');

    const lnk = document.querySelector(`[data-section="${section}"]`);
    if (lnk) lnk.classList.add('active');

    document.getElementById('page-title').textContent = SECTION_TITLES[section] || section;

    switch (section) {
        case 'dashboard':  loadDashboard();  break;
        case 'categories': loadCategories(); break;
        case 'questions':  loadQuestions();  break;
        case 'answers':    loadAnswers();    break;
        case 'config':     loadConfig();     break;
        case 'logs':       loadLogs();       break;
    }
    return false;
}

// ── Dashboard ──────────────────────────────────────────────
async function loadDashboard() {
    try {
        const s = await api('GET', '/stats/');
        document.getElementById('stat-questions').textContent  = s.total_questions;
        document.getElementById('stat-answers').textContent    = s.total_answers;
        document.getElementById('stat-categories').textContent = s.total_categories;
        document.getElementById('stat-queries').textContent    = s.total_queries;
        document.getElementById('stat-answered').textContent   = s.queries_answered;
        document.getElementById('stat-unanswered').textContent = s.queries_unanswered;

        const tbody = document.getElementById('top-queries');
        if (s.top_queries && s.top_queries.length) {
            tbody.innerHTML = s.top_queries.map((q, i) => `
                <tr>
                    <td class="text-muted">${i + 1}</td>
                    <td>${escapeHtml(q.query || '(vacío)')}</td>
                    <td><span class="badge bg-primary">${q.count}</span></td>
                </tr>`).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-3">Sin consultas registradas</td></tr>';
        }
    } catch (e) {
        showToast('Error al cargar estadísticas: ' + e.message, 'error');
    }
}

// ── Categories ─────────────────────────────────────────────
async function loadCategories() {
    try {
        allCategories = await api('GET', '/categories/');
        const tbody   = document.getElementById('categories-tbody');
        if (!allCategories.length) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-3">No hay categorías</td></tr>';
            return;
        }
        tbody.innerHTML = allCategories.map(c => `
            <tr>
                <td class="text-muted">${c.id}</td>
                <td>
                    <strong>${escapeHtml(c.name)}</strong>
                    ${c.description ? `<br><small class="text-muted">${escapeHtml(c.description)}</small>` : ''}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="showCategoryForm(${c.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCategory(${c.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>`).join('');
    } catch (e) {
        showToast('Error al cargar categorías: ' + e.message, 'error');
    }
}

function showCategoryForm(id = null) {
    editingId = id;
    const lbl = document.getElementById('categoryModalLabel');
    if (id) {
        const c = allCategories.find(x => x.id === id);
        document.getElementById('cat-name').value = c.name;
        document.getElementById('cat-desc').value = c.description || '';
        lbl.textContent = 'Editar Categoría';
    } else {
        document.getElementById('cat-name').value = '';
        document.getElementById('cat-desc').value = '';
        lbl.textContent = 'Nueva Categoría';
    }
    new bootstrap.Modal(document.getElementById('categoryModal')).show();
}

async function saveCategory() {
    const name        = document.getElementById('cat-name').value.trim();
    const description = document.getElementById('cat-desc').value.trim();
    if (!name) { showToast('El nombre es requerido', 'error'); return; }
    try {
        if (editingId) {
            await api('PUT', `/categories/${editingId}`, { name, description: description || null });
            showToast('Categoría actualizada');
        } else {
            await api('POST', '/categories/', { name, description: description || null });
            showToast('Categoría creada');
        }
        bootstrap.Modal.getInstance(document.getElementById('categoryModal')).hide();
        loadCategories();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteCategory(id) {
    const c = allCategories.find(x => x.id === id);
    if (!confirm(`¿Eliminar la categoría "${c?.name}"? Las preguntas asociadas quedarán sin categoría.`)) return;
    try {
        await api('DELETE', `/categories/${id}`);
        showToast('Categoría eliminada');
        loadCategories();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// ── Questions ──────────────────────────────────────────────
async function loadQuestions() {
    try {
        const [qs, cs] = await Promise.all([
            api('GET', '/questions/'),
            api('GET', '/categories/'),
        ]);
        allQuestions  = qs;
        allCategories = cs;

        const tbody = document.getElementById('questions-tbody');
        if (!qs.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-3">No hay preguntas</td></tr>';
            return;
        }
        tbody.innerHTML = qs.map(q => `
            <tr>
                <td class="text-muted">${q.id}</td>
                <td>${escapeHtml(truncate(q.question_text, 80))}</td>
                <td>
                    ${q.category
                        ? `<span class="badge badge-category bg-secondary">${escapeHtml(q.category.name)}</span>`
                        : '<span class="text-muted small">—</span>'}
                </td>
                <td><span class="badge bg-info text-dark">${q.answers ? q.answers.length : 0}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="showQuestionForm(${q.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteQuestion(${q.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>`).join('');
    } catch (e) {
        showToast('Error al cargar preguntas: ' + e.message, 'error');
    }
}

function showQuestionForm(id = null) {
    editingId = id;
    const lbl     = document.getElementById('questionModalLabel');
    const catSel  = document.getElementById('q-category');
    catSel.innerHTML = '<option value="">Sin categoría</option>' +
        allCategories.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');

    if (id) {
        const q = allQuestions.find(x => x.id === id);
        document.getElementById('q-text').value = q.question_text;
        catSel.value = q.category_id || '';
        lbl.textContent = 'Editar Pregunta';
    } else {
        document.getElementById('q-text').value = '';
        catSel.value = '';
        lbl.textContent = 'Nueva Pregunta';
    }
    new bootstrap.Modal(document.getElementById('questionModal')).show();
}

async function saveQuestion() {
    const question_text = document.getElementById('q-text').value.trim();
    const catVal        = document.getElementById('q-category').value;
    const category_id   = catVal ? parseInt(catVal) : null;

    if (!question_text) { showToast('El texto de la pregunta es requerido', 'error'); return; }
    try {
        if (editingId) {
            await api('PUT', `/questions/${editingId}`, { question_text, category_id });
            showToast('Pregunta actualizada');
        } else {
            await api('POST', '/questions/', { question_text, category_id });
            showToast('Pregunta creada');
        }
        bootstrap.Modal.getInstance(document.getElementById('questionModal')).hide();
        loadQuestions();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteQuestion(id) {
    if (!confirm('¿Eliminar esta pregunta? Sus respuestas también serán eliminadas.')) return;
    try {
        await api('DELETE', `/questions/${id}`);
        showToast('Pregunta eliminada');
        loadQuestions();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// ── Answers ────────────────────────────────────────────────
async function loadAnswers() {
    try {
        const [as, qs] = await Promise.all([
            api('GET', '/answers/'),
            api('GET', '/questions/'),
        ]);
        allAnswers   = as;
        allQuestions = qs;

        const tbody = document.getElementById('answers-tbody');
        if (!as.length) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-3">No hay respuestas</td></tr>';
            return;
        }
        tbody.innerHTML = as.map(a => {
            const q = qs.find(x => x.id === a.question_id);
            return `
            <tr>
                <td class="text-muted">${a.id}</td>
                <td>
                    <small class="text-muted d-block mb-1">
                        <i class="fas fa-question-circle me-1"></i>${escapeHtml(truncate(q?.question_text || '(pregunta eliminada)', 60))}
                    </small>
                    ${escapeHtml(truncate(a.answer_text, 100))}
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="showAnswerForm(${a.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteAnswer(${a.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>`;
        }).join('');
    } catch (e) {
        showToast('Error al cargar respuestas: ' + e.message, 'error');
    }
}

function showAnswerForm(id = null) {
    editingId = id;
    const lbl   = document.getElementById('answerModalLabel');
    const qSel  = document.getElementById('a-question');
    qSel.innerHTML = '<option value="">Seleccionar pregunta…</option>' +
        allQuestions.map(q => `<option value="${q.id}">${escapeHtml(truncate(q.question_text, 60))}</option>`).join('');

    if (id) {
        const a = allAnswers.find(x => x.id === id);
        document.getElementById('a-text').value = a.answer_text;
        qSel.value  = a.question_id;
        qSel.disabled = true;            // can't change question when editing
        lbl.textContent = 'Editar Respuesta';
    } else {
        document.getElementById('a-text').value = '';
        qSel.value  = '';
        qSel.disabled = false;
        lbl.textContent = 'Nueva Respuesta';
    }
    new bootstrap.Modal(document.getElementById('answerModal')).show();
}

async function saveAnswer() {
    const answer_text = document.getElementById('a-text').value.trim();
    const qVal        = document.getElementById('a-question').value;
    const question_id = qVal ? parseInt(qVal) : null;

    if (!answer_text) { showToast('El texto de la respuesta es requerido', 'error'); return; }
    if (!question_id) { showToast('Debe seleccionar una pregunta', 'error'); return; }

    try {
        if (editingId) {
            await api('PUT', `/answers/${editingId}`, { answer_text });
            showToast('Respuesta actualizada');
        } else {
            await api('POST', '/answers/', { answer_text, question_id });
            showToast('Respuesta creada');
        }
        document.getElementById('a-question').disabled = false;
        bootstrap.Modal.getInstance(document.getElementById('answerModal')).hide();
        loadAnswers();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteAnswer(id) {
    if (!confirm('¿Eliminar esta respuesta?')) return;
    try {
        await api('DELETE', `/answers/${id}`);
        showToast('Respuesta eliminada');
        loadAnswers();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// ── Config ─────────────────────────────────────────────────
async function loadConfig() {
    try {
        const configs = await api('GET', '/config/');
        const item    = configs.find(c => c.key === 'telegram_chat_id');
        document.getElementById('config-chat-id').value = item?.value || '';
    } catch (e) {
        showToast('Error al cargar configuración: ' + e.message, 'error');
    }
}

async function saveConfig() {
    const chatId = document.getElementById('config-chat-id').value.trim();
    try {
        await api('POST', '/config/', { key: 'telegram_chat_id', value: chatId || null });
        showToast('Configuración guardada correctamente');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// ── Logs ───────────────────────────────────────────────────
async function loadLogs() {
    try {
        const logs  = await api('GET', '/logs/');
        const tbody = document.getElementById('logs-tbody');
        if (!logs.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-3">Sin consultas registradas</td></tr>';
            return;
        }
        tbody.innerHTML = logs.map(l => `
            <tr>
                <td class="text-nowrap">${new Date(l.timestamp + 'Z').toLocaleString('es-GT')}</td>
                <td>${escapeHtml(l.telegram_user || '—')}</td>
                <td>${escapeHtml(truncate(l.query_text, 50))}</td>
                <td class="text-muted">${escapeHtml(truncate(l.response_text, 60))}</td>
                <td>
                    <span class="badge ${l.found_answer ? 'bg-success' : 'bg-danger'}">
                        ${l.found_answer ? 'Respondida' : 'Sin respuesta'}
                    </span>
                </td>
            </tr>`).join('');
    } catch (e) {
        showToast('Error al cargar logs: ' + e.message, 'error');
    }
}

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
