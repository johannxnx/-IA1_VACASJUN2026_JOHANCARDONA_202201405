import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lee la URL de conexión desde variable de entorno; si no existe usa el valor local por defecto
# Formato: postgresql://usuario:contraseña@host:puerto/nombre_bd
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://smartbot_user:smartbot_pass@localhost:5432/smartbot_db"
)

# Crea el "motor" de SQLAlchemy: el objeto que gestiona la conexión real con PostgreSQL
engine = create_engine(DATABASE_URL)

# Fábrica de sesiones: cada llamada a SessionLocal() abre una nueva sesión de base de datos
# autocommit=False → los cambios no se guardan solos, hay que llamar db.commit() explícitamente
# autoflush=False  → SQLAlchemy no envía cambios pendientes a la BD antes de cada consulta
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredan todos los modelos ORM (Category, Question, Answer, etc.)
# SQLAlchemy usa esta clase para detectar qué tablas crear en la BD
Base = declarative_base()


def get_db():
    # Generador que abre una sesión de BD y la cierra automáticamente al terminar la petición
    # FastAPI inyecta esta función como dependencia con Depends(get_db)
    db = SessionLocal()
    try:
        yield db          # entrega la sesión al endpoint que la solicitó
    finally:
        db.close()        # se ejecuta siempre, aunque haya error, para liberar la conexión
