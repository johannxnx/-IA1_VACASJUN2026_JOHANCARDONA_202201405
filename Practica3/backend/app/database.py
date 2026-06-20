# Configuracion de la conexion a la base de datos PostgreSQL usando SQLAlchemy ORM
# SQLAlchemy actua como capa de abstraccion entre Python y la base de datos relacional

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Motor de base de datos: gestiona internamente el pool de conexiones a PostgreSQL
# La URL viene del archivo .env para no exponer credenciales en el codigo
engine = create_engine(settings.DATABASE_URL)

# Fabrica de sesiones: cada solicitud HTTP del cliente recibe su propia sesion independiente
# autocommit=False: los cambios no se guardan hasta llamar db.commit() explicitamente
# autoflush=False: evita sincronizaciones automaticas que podrian causar comportamientos inesperados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredan todos los modelos ORM del proyecto
# SQLAlchemy usa esta clase para registrar y relacionar las tablas
Base = declarative_base()

# Funcion generadora usada como dependencia en FastAPI
# Garantiza que la sesion siempre se cierre al finalizar la peticion, incluso si hay error
def get_db():
    db = SessionLocal()
    try:
        yield db       # Entrega la sesion al endpoint que la solicita
    finally:
        db.close()     # Se ejecuta siempre, liberando la conexion al pool
