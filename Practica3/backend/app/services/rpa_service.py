# Servicio RPA (Robotic Process Automation): automatizacion del registro de facturas en formularios web
# Utiliza Playwright para controlar un navegador Chromium de forma programatica y sin intervencion humana

from playwright.sync_api import sync_playwright
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# URL del formulario web objetivo para el registro automatico
# Es el formulario simulado que sirve el propio servidor FastAPI en /rpa-form.html
RPA_TARGET_URL = "http://localhost:8000/rpa-form.html"

def registrar_factura_rpa(
    numero_factura: Optional[str],
    fecha: Optional[str],
    proveedor: Optional[str],
    nit: Optional[str],
    subtotal: Optional[float],
    impuestos: Optional[float],
    total: Optional[float],
) -> dict:
    # Abre el formulario web con Playwright, llena todos los campos automaticamente,
    # toma un screenshot de evidencia y hace clic en el boton de registro
    resultado = {"exito": False, "mensaje": "", "screenshot": None}

    try:
        with sync_playwright() as p:
            # Lanza Chromium en modo headless (sin ventana visible)
            # --no-sandbox y --disable-dev-shm-usage son necesarios en entornos sin GUI
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page()

            # Navega al formulario y espera a que termine de cargar completamente
            page.goto(RPA_TARGET_URL, timeout=15000)
            page.wait_for_load_state("networkidle")

            # Llena cada campo del formulario con los datos extraidos por OCR
            _fill_if_exists(page, "#rpa-numero-factura", numero_factura or "")
            _fill_if_exists(page, "#rpa-fecha", fecha or "")
            _fill_if_exists(page, "#rpa-proveedor", proveedor or "")
            _fill_if_exists(page, "#rpa-nit", nit or "")
            _fill_if_exists(page, "#rpa-subtotal", str(subtotal or ""))
            _fill_if_exists(page, "#rpa-impuestos", str(impuestos or ""))
            _fill_if_exists(page, "#rpa-total", str(total or ""))

            # Toma un screenshot del formulario lleno como evidencia de la ejecucion RPA
            # El archivo se guarda en la carpeta uploads con el numero de factura en el nombre
            screenshot_path = f"uploads/rpa_evidence_{numero_factura or 'sin_numero'}.png"
            page.screenshot(path=screenshot_path)

            # Hace clic en el boton de envio del formulario y espera brevemente
            submit_btn = page.query_selector("#rpa-submit")
            if submit_btn:
                submit_btn.click()
                page.wait_for_timeout(1500)  # Espera 1.5 segundos para que el formulario procese

            browser.close()

            resultado["exito"] = True
            resultado["mensaje"] = "Datos registrados mediante RPA exitosamente"
            resultado["screenshot"] = screenshot_path  # Ruta del screenshot de evidencia

    except Exception as e:
        # Registra el error en el log del servidor sin interrumpir el proceso principal
        logger.error(f"Error en RPA: {e}")
        resultado["mensaje"] = f"Error RPA: {str(e)}"

    return resultado

def _fill_if_exists(page, selector: str, value: str):
    # Funcion auxiliar: llena un campo del formulario solo si el selector existe en la pagina
    # Usa try/except para que un campo faltante no interrumpa el resto del llenado
    try:
        el = page.query_selector(selector)
        if el:
            el.fill(value)
    except Exception:
        pass
