from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter()


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    # Devuelve todas las categorías ordenadas por ID
    # No requiere autenticación (el bot también puede consultarlas)
    return db.query(Category).order_by(Category.id).all()


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),    # _ indica que no usamos el usuario, solo verificamos que esté autenticado
):
    # Verifica que no exista otra categoría con el mismo nombre (el campo es UNIQUE en BD)
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")

    cat = Category(**data.model_dump())  # crea el objeto ORM con los datos del request
    db.add(cat)
    db.commit()
    db.refresh(cat)  # recarga desde BD para obtener el id generado
    return cat


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # exclude_unset=True → solo actualiza los campos que el cliente envió (no sobreescribe con None)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # SQLAlchemy ejecuta el cascade "delete-orphan" definido en el modelo:
    # al borrar la categoría también se borran sus preguntas (y las respuestas de esas preguntas)
    db.delete(cat)
    db.commit()
