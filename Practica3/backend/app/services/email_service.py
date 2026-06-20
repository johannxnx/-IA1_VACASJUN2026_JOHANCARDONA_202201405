# Servicio de envio de correo electronico: envia reportes como adjuntos via SMTP con STARTTLS
# Usa la libreria smtplib de Python y Gmail como servidor de correo saliente

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from app.config import settings

def enviar_reporte(destinatario: str, ruta_archivo: str, nombre_archivo: str):
    # Construye y envia un correo con el archivo de reporte como adjunto

    # Crea el mensaje MIME multipart para soportar texto + archivo adjunto
    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = destinatario
    msg["Subject"] = "SmartInvoice - Reporte de Facturas"

    # Cuerpo del correo en texto plano
    msg.attach(MIMEText(
        "Adjunto encontrara el reporte de facturas generado por SmartInvoice.\n\n"
        "Este es un mensaje automatico, por favor no responda.",
        "plain"
    ))

    # Lee el archivo del reporte desde disco y lo adjunta al correo
    with open(ruta_archivo, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())

    # Codifica el archivo en Base64 para transmitirlo de forma segura por SMTP
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{nombre_archivo}"')
    msg.attach(part)

    # Establece conexion SMTP con el servidor de Gmail usando STARTTLS para cifrado
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()  # Inicia el cifrado TLS antes de autenticarse
        # Usa el App Password de Gmail generado en la cuenta, no la contrasena real
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, destinatario, msg.as_string())
