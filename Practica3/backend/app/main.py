import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app import models
from app.routers import auth, proveedores, facturas, bitacora, reportes
from app.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartInvoice API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas API primero (antes del mount de estáticos)
@app.get("/health")
def health():
    return {"status": "ok", "service": "SmartInvoice"}

app.include_router(auth.router)
app.include_router(proveedores.router)
app.include_router(facturas.router)
app.include_router(bitacora.router)
app.include_router(reportes.router)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)

# Servir archivos de uploads (evidencia RPA, etc.)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Static files al final para no interceptar rutas API
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
elif os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
