# Router de reportes: generacion asincrona de reportes PDF, Excel y CSV con envio opcional por email

import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.reporte import Reporte
from app.auth.jwt_handler import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

# Esquema de la peticion para generar un reporte
class ReporteRequest(BaseModel):
    tipo: str = "pdf"                          # Tipo de reporte: pdf, excel o csv
    email_destino: Optional[str] = None        # Correo al que enviar el reporte (opcional)

@router.post("/generar")
def generar(
    data: ReporteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Valida que el tipo de reporte sea uno de los formatos soportados
    if data.tipo not in ("pdf", "excel", "csv"):
        raise HTTPException(status_code=400, detail="Tipo debe ser pdf, excel o csv")

    # La generacion se ejecuta en segundo plano para no bloquear la respuesta HTTP
    # El usuario recibe confirmacion inmediata mientras el reporte se genera asincronamente
    background_tasks.add_task(_generar_reporte, data.tipo, data.email_destino, current_user.id)
    return {"mensaje": f"Reporte {data.tipo.upper()} en generacion. Recibiras notificacion cuando este listo."}

def _generar_reporte(tipo: str, email_destino: Optional[str], usuario_id: int):
    # Funcion ejecutada en segundo plano por BackgroundTasks de FastAPI
    # Se importa SessionLocal aqui porque esta funcion corre fuera del contexto de la peticion HTTP
    from app.database import SessionLocal
    from app.services.report_service import generar_pdf, generar_excel, generar_csv
    from app.services.email_service import enviar_reporte
    from app.models.reporte import Reporte
    from datetime import datetime

    db = SessionLocal()
    try:
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)

        # El nombre incluye timestamp para garantizar que cada archivo sea unico
        nombre = f"reporte_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{tipo}"
        ruta = os.path.join(settings.REPORTS_DIR, nombre)

        # Genera el archivo en el formato solicitado usando el servicio correspondiente
        if tipo == "pdf":
            generar_pdf(db, ruta)
        elif tipo == "excel":
            generar_excel(db, ruta)
        else:
            generar_csv(db, ruta)

        # Registra el reporte en la BD para mostrarlo en el panel y permitir descarga posterior
        reporte = Reporte(
            usuario_id=usuario_id,
            nombre=nombre,
            tipo=tipo,
            archivo_ruta=ruta,
            email_destino=email_destino,
        )
        db.add(reporte)
        db.commit()
        db.refresh(reporte)

        # Si se proporciono un email, envia el reporte como adjunto
        if email_destino:
            enviar_reporte(email_destino, ruta, nombre)
            reporte.enviado_email = True
            db.commit()

    except Exception as e:
        print(f"Error generando reporte: {e}")
    finally:
        db.close()

@router.get("/")
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Lista todos los reportes generados, del mas reciente al mas antiguo
    return db.query(Reporte).order_by(Reporte.creado_en.desc()).all()

@router.get("/{id}/descargar")
def descargar(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Verifica que el reporte exista en BD y que el archivo fisico este en disco
    r = db.query(Reporte).filter(Reporte.id == id).first()
    if not r or not os.path.exists(r.archivo_ruta):
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # FileResponse envia el archivo con el nombre original para que el navegador lo descargue
    return FileResponse(r.archivo_ruta, filename=r.nombre)
