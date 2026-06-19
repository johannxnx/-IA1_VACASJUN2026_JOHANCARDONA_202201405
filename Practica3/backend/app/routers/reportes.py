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

class ReporteRequest(BaseModel):
    tipo: str = "pdf"
    email_destino: Optional[str] = None

@router.post("/generar")
def generar(
    data: ReporteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if data.tipo not in ("pdf", "excel", "csv"):
        raise HTTPException(status_code=400, detail="Tipo debe ser pdf, excel o csv")

    background_tasks.add_task(_generar_reporte, data.tipo, data.email_destino, current_user.id)
    return {"mensaje": f"Reporte {data.tipo.upper()} en generación. Recibirás notificación cuando esté listo."}

def _generar_reporte(tipo: str, email_destino: Optional[str], usuario_id: int):
    from app.database import SessionLocal
    from app.services.report_service import generar_pdf, generar_excel, generar_csv
    from app.services.email_service import enviar_reporte
    from app.models.reporte import Reporte
    from datetime import datetime

    db = SessionLocal()
    try:
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        nombre = f"reporte_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{tipo}"
        ruta = os.path.join(settings.REPORTS_DIR, nombre)

        if tipo == "pdf":
            generar_pdf(db, ruta)
        elif tipo == "excel":
            generar_excel(db, ruta)
        else:
            generar_csv(db, ruta)

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
    return db.query(Reporte).order_by(Reporte.creado_en.desc()).all()

@router.get("/{id}/descargar")
def descargar(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    r = db.query(Reporte).filter(Reporte.id == id).first()
    if not r or not os.path.exists(r.archivo_ruta):
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return FileResponse(r.archivo_ruta, filename=r.nombre)
