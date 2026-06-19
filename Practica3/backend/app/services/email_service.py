import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from app.config import settings

def enviar_reporte(destinatario: str, ruta_archivo: str, nombre_archivo: str):
    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = destinatario
    msg["Subject"] = "SmartInvoice - Reporte de Facturas"

    msg.attach(MIMEText(
        "Adjunto encontrará el reporte de facturas generado por SmartInvoice.\n\n"
        "Este es un mensaje automático, por favor no responda.",
        "plain"
    ))

    with open(ruta_archivo, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{nombre_archivo}"')
    msg.attach(part)

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, destinatario, msg.as_string())
