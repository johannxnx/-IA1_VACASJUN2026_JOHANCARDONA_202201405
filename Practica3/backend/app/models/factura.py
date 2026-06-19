from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id", ondelete="SET NULL"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    numero_factura = Column(String(50))
    fecha_factura = Column(Date)
    subtotal = Column(Numeric(12, 2))
    impuestos = Column(Numeric(12, 2))
    total = Column(Numeric(12, 2))
    archivo_nombre = Column(String(255), nullable=False)
    archivo_ruta = Column(String(500), nullable=False)
    archivo_tipo = Column(String(10))
    nombre_proveedor_ocr = Column(String(200))
    estado = Column(String(20), default="Pendiente")
    datos_crudos = Column(Text)
    confianza_ocr = Column(Numeric(5, 2))
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    procesado_en = Column(DateTime(timezone=True))

    proveedor = relationship("Proveedor", back_populates="facturas")
    usuario = relationship("Usuario", back_populates="facturas")
    bitacoras = relationship("Bitacora", back_populates="factura")
