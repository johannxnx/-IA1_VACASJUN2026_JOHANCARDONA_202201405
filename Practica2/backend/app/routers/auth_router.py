from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AdminUser
from ..schemas import LoginRequest, Token
from ..auth import verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Busca al usuario en la BD por nombre de usuario
    user = db.query(AdminUser).filter(AdminUser.username == request.username).first()

    # Si no existe el usuario O la contraseña no coincide con el hash → 401
    # Se usa el mismo mensaje genérico en ambos casos para no revelar si el usuario existe
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    # Genera y devuelve el JWT con el username como "sub" (subject)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
