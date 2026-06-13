from difflib import SequenceMatcher

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Question, QueryLog
from ..schemas import BotQueryRequest, BotQueryResponse

router = APIRouter()

STOP_WORDS = {
    "¿", "?", "el", "la", "los", "las", "de", "del", "en", "es", "un",
    "una", "que", "y", "a", "por", "con", "se", "su", "me", "al", "si",
    "hay", "como", "qué", "cómo", "cuál", "cuáles", "cuándo", "dónde",
    "puedo", "puede", "tengo", "tiene", "hacer", "hago",
}


def _score(query: str, question_text: str) -> float:
    q = query.lower().strip()
    t = question_text.lower().strip()

    # Exact or substring match
    if q in t or t in q:
        return 0.85

    # Word overlap (ignoring stop words)
    q_words = set(q.split()) - STOP_WORDS
    t_words = set(t.split()) - STOP_WORDS
    if q_words and t_words:
        overlap = len(q_words & t_words) / max(len(q_words), len(t_words))
    else:
        overlap = 0.0

    seq = SequenceMatcher(None, q, t).ratio()
    return max(overlap * 0.75, seq * 0.55)


@router.post("/query", response_model=BotQueryResponse)
def bot_query(request: BotQueryRequest, db: Session = Depends(get_db)):
    questions = db.query(Question).options(joinedload(Question.answers)).all()

    best_score = 0.0
    best_answer = None

    for question in questions:
        if not question.answers:
            continue
        s = _score(request.query, question.question_text)
        if s > best_score:
            best_score = s
            best_answer = question.answers[0].answer_text

    found = best_score >= 0.25 and best_answer is not None
    if not found:
        best_answer = None

    db.add(QueryLog(
        telegram_user=request.telegram_user,
        telegram_user_id=request.telegram_user_id,
        query_text=request.query,
        response_text=best_answer,
        found_answer=found,
    ))
    db.commit()

    return BotQueryResponse(answer=best_answer, found=found)
