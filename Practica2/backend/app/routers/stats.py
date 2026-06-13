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
    total_questions = db.query(Question).count()
    total_answers = db.query(Answer).count()
    total_categories = db.query(Category).count()
    total_queries = db.query(QueryLog).count()
    queries_answered = db.query(QueryLog).filter(QueryLog.found_answer == True).count()
    queries_unanswered = db.query(QueryLog).filter(QueryLog.found_answer == False).count()

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
        top_queries=[{"query": r.query_text, "count": r.cnt} for r in top_raw],
    )
