from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.bitacora import Bitacora
from app.schemas.bitacora import BitacoraOut
from app.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/api/bitacora", tags=["Bitácora"])

@router.get("/", response_model=List[BitacoraOut])
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Bitacora).order_by(Bitacora.fecha_hora.desc()).limit(200).all()
