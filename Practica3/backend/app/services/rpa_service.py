"""
Módulo RPA — registra automáticamente datos de facturas en un formulario web simulado
usando Playwright en modo headless.
"""
from playwright.sync_api import sync_playwright
from typing import Optional
import logging

logger = logging.getLogger(__name__)

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
    """
    Abre el formulario web simulado y completa los campos automáticamente.
    Retorna dict con estado y screenshot de evidencia.
    """
    resultado = {"exito": False, "mensaje": "", "screenshot": None}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page()
            page.goto(RPA_TARGET_URL, timeout=15000)
            page.wait_for_load_state("networkidle")

            # Llenar campos del formulario
            _fill_if_exists(page, "#rpa-numero-factura", numero_factura or "")
            _fill_if_exists(page, "#rpa-fecha", fecha or "")
            _fill_if_exists(page, "#rpa-proveedor", proveedor or "")
            _fill_if_exists(page, "#rpa-nit", nit or "")
            _fill_if_exists(page, "#rpa-subtotal", str(subtotal or ""))
            _fill_if_exists(page, "#rpa-impuestos", str(impuestos or ""))
            _fill_if_exists(page, "#rpa-total", str(total or ""))

            # Tomar screenshot antes de enviar
            screenshot_path = f"uploads/rpa_evidence_{numero_factura or 'sin_numero'}.png"
            page.screenshot(path=screenshot_path)

            # Enviar formulario
            submit_btn = page.query_selector("#rpa-submit")
            if submit_btn:
                submit_btn.click()
                page.wait_for_timeout(1500)

            browser.close()

            resultado["exito"] = True
            resultado["mensaje"] = "Datos registrados mediante RPA exitosamente"
            resultado["screenshot"] = screenshot_path

    except Exception as e:
        logger.error(f"Error en RPA: {e}")
        resultado["mensaje"] = f"Error RPA: {str(e)}"

    return resultado

def _fill_if_exists(page, selector: str, value: str):
    try:
        el = page.query_selector(selector)
        if el:
            el.fill(value)
    except Exception:
        pass
