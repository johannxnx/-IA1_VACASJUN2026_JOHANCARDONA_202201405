# Punto de entrada principal de la aplicacion SmartInvoice
# Define la instancia FastAPI, registra los routers y monta los archivos estaticos del frontend

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app import models
from app.routers import auth, proveedores, facturas, bitacora, reportes
from app.config import settings

# Crea automaticamente todas las tablas en PostgreSQL si todavia no existen
# En produccion se usaria Alembic para migraciones controladas
Base.metadata.create_all(bind=engine)

# Instancia principal de la aplicacion con metadata para la documentacion automatica /docs
app = FastAPI(title="SmartInvoice API", version="1.0.0")

# Middleware CORS: permite que el navegador consuma la API desde el mismo servidor
# En produccion, allow_origins se limitaria al dominio real del sistema
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de salud: util para verificar que el servidor esta corriendo correctamente
@app.get("/health")
def health():
    return {"status": "ok", "service": "SmartInvoice"}

# Registro de cada grupo de endpoints organizados por dominio funcional
# El prefijo /api/... esta definido dentro de cada router individualmente
app.include_router(auth.router)           # Autenticacion: login y registro
app.include_router(proveedores.router)    # CRUD de proveedores
app.include_router(facturas.router)       # Carga, OCR y gestion de facturas
app.include_router(bitacora.router)       # Consulta del historial de actividad
app.include_router(reportes.router)       # Generacion y descarga de reportes

# Crear las carpetas de almacenamiento si no existen al iniciar el servidor
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)

# Exponer la carpeta de uploads bajo la ruta /uploads para que el navegador
# pueda acceder a los screenshots de evidencia RPA directamente por URL
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Montar el frontend SPA (HTML, CSS, JS) en la ruta raiz /
# Debe ir al final para no interferir con las rutas de la API registradas arriba
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
elif os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
