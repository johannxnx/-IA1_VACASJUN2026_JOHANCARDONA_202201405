from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Answer, Question
from ..schemas import AnswerCreate, AnswerOut, AnswerUpdate

router = APIRouter()


@router.get("/", response_model=List[AnswerOut])
def list_answers(
    question_id: Optional[int] = None,  # parámetro de query opcional: GET /api/answers/?question_id=3
    db: Session = Depends(get_db),
):
    # No requiere autenticación (el panel admin y el bot pueden consultar respuestas)
    q = db.query(Answer)
    if question_id is not None:
        q = q.filter(Answer.question_id == question_id)
    return q.order_by(Answer.id).all()


@router.post("/", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
def create_answer(
    data: AnswerCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    # Verifica que la pregunta a la que se asocia la respuesta exista
    if not db.query(Question).filter(Question.id == data.question_id).first():
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")

    answer = Answer(**data.model_dump())
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@router.get("/{answer_id}", response_model=AnswerOut)
def get_answer(answer_id: int, db: Session = Depends(get_db)):
    a = db.query(Answer).filter(Answer.id == answer_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return a


@router.put("/{answer_id}", response_model=AnswerOut)
def update_answer(
    answer_id: int,
    data: AnswerUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    a = db.query(Answer).filter(Answer.id == answer_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")

    # Solo actualiza los campos que el cliente envió (answer_text en este caso)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(a, key, value)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer(
    answer_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    a = db.query(Answer).filter(Answer.id == answer_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    db.delete(a)
    db.commit()
