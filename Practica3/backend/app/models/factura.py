# Modelo ORM para la tabla de facturas
# Almacena tanto la referencia al archivo fisico como todos los datos extraidos por el motor OCR

from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)

    # Proveedor identificado: se llena si el NIT o nombre del OCR coincide con un proveedor registrado
    proveedor_id = Column(Integer, ForeignKey("proveedores.id", ondelete="SET NULL"), nullable=True)

    # Usuario que cargo la factura al sistema
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    # Campos extraidos automaticamente por el motor OCR (EasyOCR)
    numero_factura = Column(String(50))       # Numero o codigo de la factura detectado
    fecha_factura = Column(Date)              # Fecha de emision detectada
    subtotal = Column(Numeric(12, 2))         # Monto antes de impuestos
    impuestos = Column(Numeric(12, 2))        # IVA u otros impuestos detectados
    total = Column(Numeric(12, 2))            # Monto total de la factura

    # Metadatos del archivo original subido por el usuario
    archivo_nombre = Column(String(255), nullable=False)   # Nombre original del archivo
    archivo_ruta = Column(String(500), nullable=False)     # Ruta en disco donde se guardo
    archivo_tipo = Column(String(10))                      # Extension: pdf, jpg, png

    # Nombre del proveedor tal como lo detecto el OCR, antes de buscarlo en la tabla proveedores
    nombre_proveedor_ocr = Column(String(200))

    # Estado del ciclo de vida de la factura:
    # Pendiente -> en espera de procesamiento
    # Procesado -> OCR exitoso y datos validos
    # Rechazado -> OCR funciono pero los datos no pasaron validacion
    # Error     -> fallo durante el procesamiento
    estado = Column(String(20), default="Pendiente")

    # Texto completo extraido por EasyOCR, util para auditoria y depuracion en la vista de detalle
    datos_crudos = Column(Text)

    # Porcentaje de confianza promedio del motor OCR, indica que tan legible era el documento
    confianza_ocr = Column(Numeric(5, 2))

    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    # Timestamp que registra cuando termino el proceso OCR para esta factura
    procesado_en = Column(DateTime(timezone=True))

    proveedor = relationship("Proveedor", back_populates="facturas")
    usuario = relationship("Usuario", back_populates="facturas")
    bitacoras = relationship("Bitacora", back_populates="factura")
