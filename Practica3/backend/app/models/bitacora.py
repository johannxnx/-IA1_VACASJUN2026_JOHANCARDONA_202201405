# Modelo ORM para la bitacora de actividad del sistema
# Registra cada evento relevante: carga de archivo, procesamiento OCR, ejecucion RPA, errores

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Bitacora(Base):
    __tablename__ = "bitacora"

    id = Column(Integer, primary_key=True, index=True)

    # Factura a la que corresponde este evento (puede ser NULL si la factura fue eliminada)
    factura_id = Column(Integer, ForeignKey("facturas.id", ondelete="SET NULL"), nullable=True)

    # Usuario que desencadeno la accion
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    # Fecha y hora exacta del evento, gestionada por el servidor de base de datos
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())

    # Nombre del archivo de factura relacionado al evento
    documento = Column(String(255))

    # Estado resultante del proceso: Pendiente, Procesado, Error, Rechazado
    estado = Column(String(20))

    # Descripcion del resultado del proceso o mensaje informativo
    # Ejemplos: "Extraccion completada. Total: 5032.85", "Datos registrados mediante RPA exitosamente"
    resultado = Column(Text)

    # Tipo de accion registrada:
    # "upload"       -> el usuario cargo un archivo al sistema
    # "ocr_process"  -> el motor OCR analizo la factura
    # "rpa_registro" -> Playwright lleno el formulario RPA automaticamente
    accion = Column(String(100))

    # Informacion adicional: mensaje de error detallado o, para rpa_registro,
    # el nombre del screenshot de evidencia guardado en disco
    detalle_error = Column(Text)

    factura = relationship("Factura", back_populates="bitacoras")
    usuario = relationship("Usuario", back_populates="bitacoras")
