import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.factura import Factura
from app.models.bitacora import Bitacora
from app.schemas.factura import FacturaOut, FacturaDetalle
from app.auth.jwt_handler import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/facturas", tags=["Facturas"])

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "application/pdf"}

@router.get("/", response_model=List[FacturaOut])
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Factura).order_by(Factura.creado_en.desc()).all()

@router.get("/{id}", response_model=FacturaDetalle)
def obtener(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    f = db.query(Factura).filter(Factura.id == id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return f

@router.post("/upload", status_code=201)
async def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Use PDF, JPG, JPEG o PNG.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    async with aiofiles.open(file_path, "wb") as out:
        content = await file.read()
        await out.write(content)

    ext = file.filename.rsplit(".", 1)[-1].lower()
    factura = Factura(
        usuario_id=current_user.id,
        archivo_nombre=file.filename,
        archivo_ruta=file_path,
        archivo_tipo=ext,
        estado="Pendiente",
    )
    db.add(factura)
    db.commit()
    db.refresh(factura)

    log = Bitacora(
        factura_id=factura.id,
        usuario_id=current_user.id,
        documento=file.filename,
        estado="Pendiente",
        accion="upload",
        resultado="Archivo recibido correctamente",
    )
    db.add(log)
    db.commit()

    background_tasks.add_task(procesar_factura, factura.id, current_user.id)
    return {"id": factura.id, "mensaje": "Factura cargada. Procesando en segundo plano."}

def procesar_factura(factura_id: int, usuario_id: int):
    from app.database import SessionLocal
    from app.services.ocr_service import extraer_datos
    from app.services.vision_service import preprocesar_imagen
    from datetime import datetime

    db = SessionLocal()
    try:
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            return

        imagen_preprocesada = preprocesar_imagen(factura.archivo_ruta, factura.archivo_tipo)
        resultado = extraer_datos(imagen_preprocesada)

        subtotal = float(resultado["subtotal"]) if resultado.get("subtotal") is not None else None
        impuestos = float(resultado["impuestos"]) if resultado.get("impuestos") is not None else None
        total = float(resultado["total"]) if resultado.get("total") is not None else None

        # --- Validación automática ---
        errores_validacion = []
        if not resultado.get("numero_factura"):
            errores_validacion.append("número de factura no detectado")
        if total is not None and total <= 0:
            errores_validacion.append("total debe ser mayor que cero")
        if subtotal is not None and total is not None and impuestos is not None:
            diferencia = abs((subtotal + impuestos) - total)
            if diferencia > 0.10:
                errores_validacion.append(f"inconsistencia numérica: subtotal+impuestos={subtotal+impuestos:.2f} vs total={total:.2f}")

        factura.numero_factura = resultado.get("numero_factura")
        factura.fecha_factura = resultado.get("fecha_factura")
        factura.subtotal = subtotal
        factura.impuestos = impuestos
        factura.total = total
        factura.nombre_proveedor_ocr = resultado.get("nombre_proveedor")
        factura.datos_crudos = resultado.get("texto_crudo")
        factura.confianza_ocr = float(resultado["confianza"]) if resultado.get("confianza") is not None else None
        factura.procesado_en = datetime.utcnow()

        # Buscar proveedor por NIT; si no, por nombre
        from app.models.proveedor import Proveedor
        nit = resultado.get("nit")
        nombre_ocr = resultado.get("nombre_proveedor")
        if nit:
            proveedor = db.query(Proveedor).filter(Proveedor.nit == nit).first()
            if proveedor:
                factura.proveedor_id = proveedor.id
        if not factura.proveedor_id and nombre_ocr:
            proveedor = db.query(Proveedor).filter(
                Proveedor.nombre.ilike(f"%{nombre_ocr[:30]}%")
            ).first()
            if proveedor:
                factura.proveedor_id = proveedor.id

        if errores_validacion:
            factura.estado = "Rechazado"
        elif not factura.total and not factura.numero_factura:
            factura.estado = "Error"
        else:
            factura.estado = "Procesado"

        db.commit()

        resultado_msg = f"Extracción completada. Total: {factura.total}"
        if errores_validacion:
            resultado_msg = "Rechazado por validación: " + "; ".join(errores_validacion)

        log = Bitacora(
            factura_id=factura_id,
            usuario_id=usuario_id,
            documento=factura.archivo_nombre,
            estado=factura.estado,
            accion="ocr_process",
            resultado=resultado_msg,
        )
        db.add(log)
        db.commit()

        # --- Automatización RPA: registrar en formulario web simulado ---
        if factura.estado == "Procesado":
            try:
                from app.services.rpa_service import registrar_factura_rpa
                rpa_res = registrar_factura_rpa(
                    numero_factura=factura.numero_factura,
                    fecha=str(factura.fecha_factura) if factura.fecha_factura else None,
                    proveedor=factura.nombre_proveedor_ocr,
                    nit=resultado.get("nit"),
                    subtotal=subtotal,
                    impuestos=impuestos,
                    total=total,
                )
                # screenshot path guardado en detalle_error para mostrarlo en bitácora
                screenshot = rpa_res.get("screenshot")
                screenshot_nombre = os.path.basename(screenshot) if screenshot else None
                rpa_log = Bitacora(
                    factura_id=factura_id,
                    usuario_id=usuario_id,
                    documento=factura.archivo_nombre,
                    estado="Procesado" if rpa_res["exito"] else "Error",
                    accion="rpa_registro",
                    resultado=rpa_res["mensaje"],
                    detalle_error=screenshot_nombre,
                )
                db.add(rpa_log)
                db.commit()
            except Exception as rpa_e:
                import logging
                logging.getLogger(__name__).warning(f"RPA no ejecutado: {rpa_e}")

    except Exception as e:
        db.query(Factura).filter(Factura.id == factura_id).update({"estado": "Error"})
        log = Bitacora(
            factura_id=factura_id,
            usuario_id=usuario_id,
            documento=str(factura_id),
            estado="Error",
            accion="ocr_process",
            detalle_error=str(e),
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

@router.delete("/{id}", status_code=204)
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    f = db.query(Factura).filter(Factura.id == id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    db.delete(f)
    db.commit()
