from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    nombre = Column(String(150), nullable=False)
    tipo = Column(String(10), nullable=False)
    archivo_ruta = Column(String(500), nullable=False)
    enviado_email = Column(Boolean, default=False)
    email_destino = Column(String(150))
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="reportes")
