from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from . import models  # noqa: F401 – importar models registra todas las tablas en Base.metadata
from .seed import seed_data
from .routers import auth_router, categories, questions, answers, config, logs, stats, bot_query

# Crea todas las tablas en PostgreSQL si no existen todavía
# Usa los modelos importados arriba para saber qué tablas generar
Base.metadata.create_all(bind=engine)

# Instancia principal de FastAPI
# docs_url="/api/docs" → la documentación Swagger estará en http://localhost:8000/api/docs
app = FastAPI(title="SmartBot API", version="1.0.0", docs_url="/api/docs")

# Middleware CORS: permite que el frontend (JS en el navegador) llame a la API
# allow_origins=["*"] → acepta peticiones desde cualquier origen (apto para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],   # Authorization, Content-Type, etc.
)

# Sirve los archivos estáticos (CSS, JS, imágenes) desde la carpeta "static/"
# Accesibles en http://localhost:8000/static/js/app.js, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Motor de plantillas Jinja2 para renderizar el HTML del panel admin
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    # Se ejecuta una sola vez cuando el servidor arranca
    # Llama a seed_data() para insertar datos iniciales si la BD está vacía
    seed_data()


@app.get("/")
def admin_panel(request: Request):
    # Ruta raíz: devuelve el HTML del panel administrativo
    # El objeto "request" es requerido por Jinja2 para construir la respuesta
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    # Endpoint de salud usado por Docker y herramientas de monitoreo
    # Si responde 200 {"status": "ok"} el servicio está funcionando
    return {"status": "ok"}


# Registra cada router con su prefijo de URL y etiqueta para Swagger
app.include_router(auth_router.router, prefix="/api/auth",       tags=["auth"])
app.include_router(categories.router,  prefix="/api/categories", tags=["categories"])
app.include_router(questions.router,   prefix="/api/questions",  tags=["questions"])
app.include_router(answers.router,     prefix="/api/answers",    tags=["answers"])
app.include_router(config.router,      prefix="/api/config",     tags=["config"])
app.include_router(logs.router,        prefix="/api/logs",       tags=["logs"])
app.include_router(stats.router,       prefix="/api/stats",      tags=["stats"])
app.include_router(bot_query.router,   prefix="/api/bot",        tags=["bot"])
