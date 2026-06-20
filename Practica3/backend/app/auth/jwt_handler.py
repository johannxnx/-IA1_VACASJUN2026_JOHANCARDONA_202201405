# Modulo de autenticacion: manejo de contrasenas con bcrypt y generacion/validacion de tokens JWT
# JWT (JSON Web Token) permite autenticar peticiones sin consultar la BD en cada solicitud

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db

# Contexto de hashing: usa el algoritmo bcrypt para almacenar contrasenas de forma segura
# bcrypt es resistente a ataques de fuerza bruta gracias a su funcion de costo configurable
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2: indica a FastAPI como extraer el token del encabezado HTTP
# El cliente debe enviar: Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password: str) -> str:
    # Convierte una contrasena en texto plano a un hash bcrypt irreversible
    # Este hash es el que se almacena en la base de datos
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    # Compara la contrasena ingresada por el usuario contra el hash almacenado en BD
    # bcrypt internamente extrae el salt del hash para hacer la comparacion correctamente
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    # Genera un token JWT firmado digitalmente con la clave secreta del servidor
    # El payload incluye: sub (ID del usuario), email, rol y fecha de expiracion (exp)
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Dependencia de FastAPI que protege los endpoints privados
    # Se inyecta en cualquier endpoint que requiera autenticacion
    # Si el token es invalido, expirado o el usuario no existe, retorna HTTP 401 automaticamente
    from app.models.usuario import Usuario

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica el token y verifica la firma digital usando la clave secreta
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        # JWTError cubre tokens malformados, expirados o con firma invalida
        raise credentials_exception

    # Consulta la BD para confirmar que el usuario sigue activo
    # Esto permite revocar acceso desactivando el usuario sin invalidar todos los tokens
    user = db.query(Usuario).filter(Usuario.id == int(user_id), Usuario.activo == True).first()
    if user is None:
        raise credentials_exception
    return user
