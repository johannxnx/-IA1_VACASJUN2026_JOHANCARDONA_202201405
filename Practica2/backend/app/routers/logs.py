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
    return (
        db.query(QueryLog)
        .order_by(QueryLog.timestamp.desc())
        .limit(200)
        .all()
    )
