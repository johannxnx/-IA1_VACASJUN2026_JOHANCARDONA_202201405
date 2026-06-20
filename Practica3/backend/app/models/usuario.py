# Modelo ORM para la tabla de usuarios del sistema
# Define la estructura de la tabla "usuarios" en PostgreSQL mediante SQLAlchemy

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    # Nombre completo del usuario para mostrar en el panel
    nombre = Column(String(100), nullable=False)

    # Email unico que funciona como nombre de usuario para el login
    email = Column(String(150), unique=True, nullable=False, index=True)

    # La contrasena nunca se guarda en texto plano, siempre como hash bcrypt
    password_hash = Column(String(255), nullable=False)

    # Rol del usuario en el sistema, por defecto "admin"
    rol = Column(String(20), default="admin")

    # Baja logica: desactivar un usuario en lugar de eliminarlo preserva la integridad referencial
    activo = Column(Boolean, default=True)

    # Fecha de registro gestionada automaticamente por el servidor de base de datos
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones ORM: permiten acceder a las facturas, registros y reportes del usuario
    facturas = relationship("Factura", back_populates="usuario")
    bitacoras = relationship("Bitacora", back_populates="usuario")
    reportes = relationship("Reporte", back_populates="usuario")
