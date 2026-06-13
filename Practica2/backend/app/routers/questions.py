from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user
from ..database import get_db
from ..models import Question
from ..schemas import QuestionCreate, QuestionOut, QuestionUpdate

router = APIRouter()


@router.get("/", response_model=List[QuestionOut])
def list_questions(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Question).options(
        joinedload(Question.category),
        joinedload(Question.answers),
    )
    if category_id is not None:
        q = q.filter(Question.category_id == category_id)
    return q.order_by(Question.id).all()


@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    question = Question(**data.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return db.query(Question).options(
        joinedload(Question.category),
        joinedload(Question.answers),
    ).filter(Question.id == question.id).first()


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(Question).options(
        joinedload(Question.category),
        joinedload(Question.answers),
    ).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return q


@router.put("/{question_id}", response_model=QuestionOut)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(q, key, value)
    db.commit()
    return db.query(Question).options(
        joinedload(Question.category),
        joinedload(Question.answers),
    ).filter(Question.id == question_id).first()


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    db.delete(q)
    db.commit()
