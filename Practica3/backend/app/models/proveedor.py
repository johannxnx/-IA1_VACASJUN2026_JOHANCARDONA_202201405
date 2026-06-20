# Modelo ORM para la tabla de proveedores
# Los proveedores se vinculan a las facturas automaticamente por NIT o por nombre detectado via OCR

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)

    # Razon social o nombre comercial del proveedor
    nombre = Column(String(150), nullable=False)

    # NIT del proveedor: campo unico e indexado para busquedas rapidas
    # El OCR extrae el NIT de la factura y lo compara contra este campo
    nit = Column(String(20), unique=True, nullable=False, index=True)

    direccion = Column(String(255))
    telefono = Column(String(20))
    email = Column(String(150))

    # Baja logica: el proveedor se desactiva en lugar de eliminarse
    # Esto mantiene la integridad de las facturas historicas que ya lo referencian
    activo = Column(Boolean, default=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    # Se actualiza automaticamente cada vez que se modifica el registro
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacion con facturas: una factura puede tener un proveedor identificado
    facturas = relationship("Factura", back_populates="proveedor")
