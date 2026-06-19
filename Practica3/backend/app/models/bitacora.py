from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Bitacora(Base):
    __tablename__ = "bitacora"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id", ondelete="SET NULL"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())
    documento = Column(String(255))
    estado = Column(String(20))
    resultado = Column(Text)
    accion = Column(String(100))
    detalle_error = Column(Text)

    factura = relationship("Factura", back_populates="bitacoras")
    usuario = relationship("Usuario", back_populates="bitacoras")
