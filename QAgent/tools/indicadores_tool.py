"""
Herramientas para obtener indficadores económicos.
"""
import json
import requests
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import chainlit as cl
from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
from QAgent.utils.logging_utils import notify_error

logger = logging.getLogger(__name__)

API_URL = "https://mindicador.cl/api"
TIMEOUT_SECS = 8.0

# ---------- Helpers de formato ----------

def fmt_date_iso_to_cl(fecha_iso: Optional[str]) -> str:
    """Convierte '2025-09-03T04:00:00.000Z' a '03-sep-2025'. Si falta, retorna '-'."""
    if not fecha_iso:
        return "-"
    try:
        dt = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00"))
        return dt.strftime("%d-%b-%Y").lower()
    except Exception:
        return "-"

def fmt_currency_clp(valor: Optional[float]) -> str:
    """Formatea CLP con separador de miles latino y 2 decimales."""
    if valor is None:
        return "-"
    return f"${valor:,.2f} CLP".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_usd(valor: Optional[float]) -> str:
    """Formatea USD con 2 decimales."""
    if valor is None:
        return "-"
    return f"US$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_percent(valor: Optional[float]) -> str:
    """Formatea porcentaje con 1 o 2 decimales según sea necesario."""
    if valor is None:
        return "-"
    # Si el valor tiene un solo decimal en mindicador, conserva 1; si no, usa 2
    s = f"{valor:.2f}".rstrip("0").rstrip(".")
    return f"{s}%"

def safe_val(d: Dict[str, Any], key: str, sub: str = "valor"):
    """Acceso seguro a datos[key][sub]."""
    try:
        return d.get(key, {}).get(sub, None)
    except Exception:
        return None

# ---------- Tool ----------

class IndicadoresTool(BaseTool):
    """
    Obtiene indicadores económicos actuales desde mindicador.cl y entrega
    un resumen tipo listado (string). El título incluye la fecha de corte,
    pero los indicadores se muestran sin fecha individual.
    """

    async def execute(self) -> str:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECS, headers={"Accept": "application/json"}) as client:
                resp = await client.get(API_URL)
                resp.raise_for_status()
                datos = resp.json()
        except httpx.HTTPError as e:
            logger.exception("HTTP error en mindicador.cl")
            notify_error(f"mindicador.cl HTTP error: {e}")
            return f"Error al acceder a mindicador.cl: {e}. Intenta buscando en la web."
        except Exception as e:
            logger.exception("Error inesperado en IndicadoresTool")
            notify_error(f"IndicadoresTool error: {e}")
            return f"Error al procesar los indicadores: {e}."

        # Fecha de corte general (cabecera)
        fecha_corte = safe_val(datos, "fecha")
        if isinstance(fecha_corte, str):
            fecha_corte_fmt = fmt_date_iso_to_cl(fecha_corte)
        else:
            fecha_corte_fmt = "-"

        lineas: List[str] = []
        lineas.append(f"Indicadores económicos al día de {fecha_corte_fmt}")

        campos = [
            ("uf", "UF", fmt_currency_clp),
            ("dolar", "Dólar observado", fmt_currency_clp),
            ("euro", "Euro", fmt_currency_clp),
            ("utm", "UTM", fmt_currency_clp),
            ("ipc", "IPC", fmt_percent),
            ("imacec", "Imacec", fmt_percent),
            ("tpm", "TPM", fmt_percent),
            ("libra_cobre", "Libra de cobre", fmt_usd),
            ("tasa_desempleo", "Tasa de desempleo", fmt_percent),
            ("dolar_intercambio", "Dólar acuerdo", fmt_currency_clp),
            ("bitcoin", "Bitcoin", fmt_usd),
        ]

        for key, etiqueta, formatter in campos:
            valor = safe_val(datos, key, "valor")
            if valor is None:
                continue
            try:
                num = float(valor)
            except Exception:
                num = None
            valor_fmt = formatter(num)
            lineas.append(f"- {etiqueta}: {valor_fmt}")

        return "\n".join(lineas)


@cl.step(type="tool")
async def indicadores() -> str:
    """
    Herramienta de Assistant
    Obtiene y resume indicadores económicos de Chile (mindicador.cl) en formato listado (string).
    
    Returns:
        str: Un string con los indicadores y sus valores. 
             Solo se incluye una fecha en el título, no en cada indicador.
    """
    tool = IndicadoresTool()
    return await tool.execute()
