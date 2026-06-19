from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token, LoginRequest
from app.auth.jwt_handler import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == data.email, Usuario.activo == True).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_access_token({"sub": str(user.id), "email": user.email, "rol": user.rol})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/registro", response_model=UsuarioOut, status_code=201)
def registro(data: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=data.rol,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
