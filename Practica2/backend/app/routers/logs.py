from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import QueryLog
from ..schemas import QueryLogOut

router = APIRouter()


@router.get("/", response_model=List[QueryLogOut])
def list_logs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Devuelve los últimos 200 registros del historial de consultas del bot
    # Ordenado por timestamp DESC → los más recientes primero
    # El límite de 200 evita que el endpoint devuelva demasiados datos de golpe
    return (
        db.query(QueryLog)
        .order_by(QueryLog.timestamp.desc())
        .limit(200)
        .all()
    )
