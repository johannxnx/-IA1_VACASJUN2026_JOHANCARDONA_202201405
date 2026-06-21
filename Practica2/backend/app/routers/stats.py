from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Answer, Category, QueryLog, Question
from ..schemas import StatsOut

router = APIRouter()


@router.get("/", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Conteos simples de cada tabla principal
    total_questions   = db.query(Question).count()
    total_answers     = db.query(Answer).count()
    total_categories  = db.query(Category).count()
    total_queries     = db.query(QueryLog).count()

    # Filtra el log por el campo booleano found_answer
    queries_answered   = db.query(QueryLog).filter(QueryLog.found_answer == True).count()
    queries_unanswered = db.query(QueryLog).filter(QueryLog.found_answer == False).count()

    # Consulta SQL agregada: agrupa por texto de consulta, cuenta repeticiones y toma las 10 más frecuentes
    # Equivale a: SELECT query_text, COUNT(id) as cnt FROM query_logs GROUP BY query_text ORDER BY cnt DESC LIMIT 10
    top_raw = (
        db.query(QueryLog.query_text, func.count(QueryLog.id).label("cnt"))
        .group_by(QueryLog.query_text)
        .order_by(func.count(QueryLog.id).desc())
        .limit(10)
        .all()
    )

    return StatsOut(
        total_questions=total_questions,
        total_answers=total_answers,
        total_categories=total_categories,
        total_queries=total_queries,
        queries_answered=queries_answered,
        queries_unanswered=queries_unanswered,
        # Convierte los resultados de la consulta agregada a una lista de dicts
        top_queries=[{"query": r.query_text, "count": r.cnt} for r in top_raw],
    )
