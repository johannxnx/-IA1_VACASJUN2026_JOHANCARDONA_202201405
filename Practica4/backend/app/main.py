# ============================================================
# main.py - Punto de entrada de la aplicación FastAPI
# RoboMaze - Práctica 4 IA1
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.maze_routes import router

# Inicialización de la aplicación FastAPI con metadata descriptiva
app = FastAPI(
    title="RoboMaze API",
    description="API REST para resolución de laberintos con algoritmos BFS y DFS",
    version="1.0.0"
)

# Configuración de CORS para permitir peticiones desde el frontend
# (el frontend corre en un origen distinto al backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # En producción se limitaría al dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],       # Permite GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# Registro del router con prefijo /api
# Todas las rutas del laberinto quedan bajo /api/...
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    """Ruta raíz para verificar que el servidor está activo."""
    return {"message": "RoboMaze API activa", "docs": "/docs"}
