# Modulo de configuracion: lee todas las variables de entorno desde el archivo .env
# Usando pydantic-settings para validacion automatica de tipos al arrancar el servidor

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # URL completa de conexion a PostgreSQL en formato:
    # postgresql://usuario:contrasena@host:puerto/nombre_base_de_datos
    DATABASE_URL: str

    # Clave secreta utilizada para firmar y verificar los tokens JWT
    SECRET_KEY: str

    # Algoritmo de firma para JWT: HS256 usa HMAC con SHA-256
    ALGORITHM: str = "HS256"

    # Tiempo en minutos antes de que el token JWT expire y el usuario deba volver a iniciar sesion
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Configuracion del servidor SMTP para envio de correos electronicos
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587        # Puerto 587 usa STARTTLS para cifrado
    EMAIL_USER: str = ""         # Correo del remitente (cuenta de Gmail)
    EMAIL_PASSWORD: str = ""     # App Password generada en Google, no la contrasena real
    EMAIL_FROM: str = ""         # Direccion que aparece como remitente en el correo

    # Rutas de carpetas donde el sistema almacena archivos en disco
    UPLOAD_DIR: str = "uploads"     # Facturas subidas y screenshots de evidencia RPA
    REPORTS_DIR: str = "reports"    # Reportes PDF, Excel y CSV generados

    class Config:
        # Le indica a pydantic que lea las variables desde el archivo .env
        env_file = ".env"

# Instancia global de configuracion accesible desde cualquier modulo del proyecto
settings = Settings()
