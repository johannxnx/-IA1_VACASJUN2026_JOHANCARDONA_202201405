# Modelo ORM para la tabla de reportes generados
# Cada vez que el usuario solicita un reporte, se registra aqui con su ubicacion en disco

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True)

    # Usuario que solicito la generacion del reporte desde el panel
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    # Nombre del archivo generado, incluye timestamp para garantizar nombres unicos
    # Ejemplo: reporte_20260619_153045.pdf
    nombre = Column(String(150), nullable=False)

    # Tipo de reporte generado: pdf, excel o csv
    tipo = Column(String(10), nullable=False)

    # Ruta absoluta en disco donde se guardo el archivo del reporte
    archivo_ruta = Column(String(500), nullable=False)

    # Indica si el reporte fue enviado exitosamente por correo electronico
    enviado_email = Column(Boolean, default=False)

    # Direccion de correo a la que se envio el reporte, si el usuario la proporciono
    email_destino = Column(String(150))

    # Fecha y hora de creacion del reporte
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="reportes")
