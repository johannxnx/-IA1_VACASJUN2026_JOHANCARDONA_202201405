# Router de autenticacion: endpoints de login y registro de usuarios
# Todos los demas endpoints del sistema requieren el token JWT obtenido en /login

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, Token, LoginRequest
from app.auth.jwt_handler import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])

@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Busca el usuario por email y verifica que este activo en el sistema
    user = db.query(Usuario).filter(Usuario.email == data.email, Usuario.activo == True).first()

    # Si el email no existe o la contrasena no coincide con el hash, rechaza con 401
    # Se usa el mismo mensaje de error para ambos casos, evitando revelar cual fallo
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

    # Genera el token JWT con el ID, email y rol del usuario
    # Este token se debe incluir en cada peticion posterior como: Authorization: Bearer <token>
    token = create_access_token({"sub": str(user.id), "email": user.email, "rol": user.rol})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/registro", response_model=UsuarioOut, status_code=201)
def registro(data: UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica que el email no este ya registrado para evitar duplicados
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    # Crea el usuario hasheando la contrasena antes de guardarla en BD
    user = Usuario(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password),  # Nunca se guarda en texto plano
        rol=data.rol,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
