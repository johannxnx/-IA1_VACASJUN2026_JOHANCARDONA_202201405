import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from .models import AdminUser

# Lee configuración de JWT desde variables de entorno (definidas en docker-compose.yml)
SECRET_KEY                  = os.getenv("SECRET_KEY", "smartbot-secret-key-change-in-production-2024")
ALGORITHM                   = os.getenv("ALGORITHM", "HS256")                      # Algoritmo de firma del token
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 1440 min = 24 horas

# Contexto de hashing: usa bcrypt para almacenar contraseñas de forma segura
# deprecated="auto" → detecta hashes antiguos y los marca para actualización
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad HTTP Bearer: FastAPI lo usa para mostrar el candado en Swagger
# y para extraer el token del header "Authorization: Bearer <token>"
security = HTTPBearer()


def verify_password(plain: str, hashed: str) -> bool:
    # Compara la contraseña en texto plano contra el hash guardado en la BD
    # bcrypt rehashea el plain y compara; nunca decodifica el hash
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    # Genera el hash bcrypt de una contraseña; se usa al crear o actualizar usuarios
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # Calcula la fecha de expiración: ahora + delta personalizado o el valor por defecto (24h)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire   # "exp" es un claim estándar de JWT para la expiración
    # Firma y codifica el token con la clave secreta y el algoritmo configurado
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # extrae el token del header
    db: Session = Depends(get_db),
) -> AdminUser:
    # Dependencia inyectada en todos los endpoints que requieren autenticación
    # Si el token es inválido o expirado lanza HTTP 401
    try:
        # Decodifica y verifica la firma del JWT
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # "sub" (subject) es el claim donde guardamos el username
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    # Verifica que el usuario del token todavía exista en la BD
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user
