from difflib import SequenceMatcher

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Question, QueryLog
from ..schemas import BotQueryRequest, BotQueryResponse

router = APIRouter()

# Palabras que se ignoran al comparar textos (artículos, preposiciones, pronombres comunes)
# Eliminarlas mejora la precisión porque evita que dos frases puntúen alto solo por compartir "el", "la", "de", etc.
STOP_WORDS = {
    "¿", "?", "el", "la", "los", "las", "de", "del", "en", "es", "un",
    "una", "que", "y", "a", "por", "con", "se", "su", "me", "al", "si",
    "hay", "como", "qué", "cómo", "cuál", "cuáles", "cuándo", "dónde",
    "puedo", "puede", "tengo", "tiene", "hacer", "hago",
}


def _score(query: str, question_text: str) -> float:
    # Normaliza ambos textos a minúsculas y sin espacios extra
    q = query.lower().strip()
    t = question_text.lower().strip()

    # Método 1 – Coincidencia exacta / subcadena
    # Si el texto del usuario está contenido en la pregunta o viceversa → score alto fijo (0.85)
    if q in t or t in q:
        return 0.85

    # Método 2 – Solapamiento de palabras (excluyendo stop words)
    # Divide en palabras, quita las stop words y calcula cuántas palabras comparten ambos textos
    q_words = set(q.split()) - STOP_WORDS
    t_words = set(t.split()) - STOP_WORDS
    if q_words and t_words:
        # Intersección / máximo de los dos conjuntos → valor entre 0.0 y 1.0
        overlap = len(q_words & t_words) / max(len(q_words), len(t_words))
    else:
        overlap = 0.0

    # Método 3 – SequenceMatcher (similitud de cadenas carácter a carácter)
    # Útil para capturar errores tipográficos o variaciones de escritura
    seq = SequenceMatcher(None, q, t).ratio()

    # Devuelve el mayor de los dos scores ponderados
    # overlap × 0.75 tiene más peso que seq × 0.55 porque la coincidencia de palabras clave es más relevante
    return max(overlap * 0.75, seq * 0.55)


@router.post("/query", response_model=BotQueryResponse)
def bot_query(request: BotQueryRequest, db: Session = Depends(get_db)):
    # Carga todas las preguntas con sus respuestas en una sola consulta (joinedload evita N+1)
    questions = db.query(Question).options(joinedload(Question.answers)).all()

    best_score  = 0.0
    best_answer = None

    # Recorre todas las preguntas y calcula el score de similitud con la consulta del usuario
    for question in questions:
        if not question.answers:
            continue  # omite preguntas sin respuestas registradas
        s = _score(request.query, question.question_text)
        if s > best_score:
            best_score  = s
            best_answer = question.answers[0].answer_text  # toma la primera respuesta de la pregunta

    # Umbral mínimo de aceptación: si el mejor score es menor a 0.25, no se considera válido
    found = best_score >= 0.25 and best_answer is not None
    if not found:
        best_answer = None  # el bot responderá con un mensaje de "no encontré respuesta"

    # Registra la consulta en el log independientemente de si se encontró respuesta o no
    db.add(QueryLog(
        telegram_user=request.telegram_user,
        telegram_user_id=request.telegram_user_id,
        query_text=request.query,
        response_text=best_answer,
        found_answer=found,
    ))
    db.commit()

    return BotQueryResponse(answer=best_answer, found=found)
