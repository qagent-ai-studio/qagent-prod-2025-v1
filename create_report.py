# create_report.py (versión saneada UTF-8)
import os
import sys
import logging
import json
from datetime import date, timedelta, datetime

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from dotenv import load_dotenv

# === Carga .env ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# === Configuración ===
DB_URL = os.getenv("DB_URL")
LOG_PATH = os.getenv("REPORT_LOG", "create_report.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

if not DB_URL:
    raise RuntimeError("DB_URL no está definido en .env")

# (Opcional) Si tu DB_URL no incluye el dialecto, podrías normalizarlo aquí
# Ej: postgresql://... -> postgresql+psycopg2://...
if DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Un único engine para todo el script
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

def formatea_duracion(segundos: float) -> str:
    if segundos < 60:
        return f"{segundos:.2f} Seg."
    minutos = int(segundos // 60)
    segundos_restantes = int(segundos % 60)
    return f"{minutos}:{segundos_restantes:02d} Min."

def get_previous_month_range():
    today = date.today().replace(day=1)
    last_month_end = today - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return last_month_start, last_month_end

def generate_report(fecha_inicio: date, fecha_fin: date, cliente: str = "GLobal Reefers"):
    # ⚠️ Sin SET client_encoding ni connect_args forzando LATIN1/WIN1252
    QUERY = text("""
        SELECT
            t.id AS thread_id,
            t.name AS thread_name,
            u."identifier" AS usuario,
            s.id AS step_id,
            s.start as inicio,
            s."end" as final,
            CASE
                WHEN s.type = 'run' AND f.value IS NOT NULL THEN 'feedback'
                ELSE s.type
            END AS type,
            s.name,
            CASE
                WHEN s.type = 'tool' THEN s.input
                ELSE s.output
            END AS texto,
            f.value AS feedback,
            f."comment" AS feedback_comment,
            e."type" AS element_type,
            s."createdAt"
        FROM public.threads t
        JOIN public.steps s ON s."threadId" = t.id
        LEFT JOIN public.users u ON u.id = t."userId"
        LEFT JOIN public.feedbacks f ON f."forId" = s.id
        LEFT JOIN public.elements e ON e."forId" = s.id
        WHERE s."createdAt" BETWEEN :fecha_inicio AND :fecha_fin
        ORDER BY s."createdAt"
    """)

    # Solo lectura: no hace falta transacción; si prefieres, usa begin()
    with engine.connect() as conn:
        df = pd.read_sql_query(
            QUERY,
            conn,
            params={
                "fecha_inicio": f"{fecha_inicio} 00:00:00",
                "fecha_fin": f"{fecha_fin} 23:59:59",
            },
        )

    # Normalizaciones
    if "feedback" in df.columns:
        df["feedback"] = df["feedback"].fillna("")
    # Excluir pasos tipo 'run'
    if "type" in df.columns:
        df = df[~(df["type"] == "run")]

    # Serie temporal
    df["createdAt"] = pd.to_datetime(df["createdAt"])
    df["fecha"] = df["createdAt"].dt.date
    df_ts = df[["thread_id", "fecha"]].drop_duplicates()
    serie = (
        df_ts.groupby("fecha")["thread_id"]
        .nunique()
        .reset_index()
        .sort_values("fecha")
    )
    if not serie.empty:
        idx = pd.date_range(serie["fecha"].min(), serie["fecha"].max(), freq="D")
        serie = (
            serie.set_index("fecha")
            .reindex(idx, fill_value=0)
            .rename_axis("fecha")
            .reset_index()
        )
        rango_fechas = serie["fecha"].astype(str).tolist()
        rango_conversaciones = serie["thread_id"].tolist()
    else:
        rango_fechas = []
        rango_conversaciones = []

    feedback_positivo = df[df["feedback"] == 1].shape[0] if "feedback" in df.columns else 0
    feedback_negativo = df[df["feedback"] == 0].shape[0] if "feedback" in df.columns else 0

    conversaciones = df["thread_id"].nunique()
    interacciones = df["step_id"].nunique()
    consultas_usuario = df[df["type"] == "user_message"].shape[0]
    respuestas_asistente = df[df["type"] == "assistant_message"].shape[0]
    consultas_fuentes = df[df["type"] == "tool"].shape[0]
    otras_interacciones = interacciones - consultas_usuario - respuestas_asistente - consultas_fuentes

    mix_consultas_usuario = round(consultas_usuario / interacciones, 2) if interacciones else 0
    mix_respuestas_asistente = round(respuestas_asistente / interacciones, 2) if interacciones else 0
    mix_consultas_fuentes = round(consultas_fuentes / interacciones, 2) if interacciones else 0
    mix_otras_interacciones = round(otras_interacciones / interacciones, 2) if interacciones else 0

    tools = df[df["type"] == "tool"]["name"].value_counts().to_dict()
    elementos_raw = df[~df["element_type"].isna()]["element_type"].value_counts().to_dict()
    elementos = {k.capitalize(): v for k, v in elementos_raw.items()}

    # KPIs de tiempo
    df["inicio"] = pd.to_datetime(df["inicio"])
    df["final"] = pd.to_datetime(df["final"])
    df["duracion"] = (df["final"] - df["inicio"]).dt.total_seconds()
    conversaciones_duracion = df.groupby("thread_id")["duracion"].sum().dropna()
    conversaciones_duracion = conversaciones_duracion[conversaciones_duracion >= 2]

    duracion_mas_baja_raw = float(np.round(conversaciones_duracion.min(), 2)) if not conversaciones_duracion.empty else 0
    duracion_mas_alta_raw = float(np.round(conversaciones_duracion.max(), 2)) if not conversaciones_duracion.empty else 0
    duracion_promedio_raw = float(np.round(conversaciones_duracion.mean(), 2)) if not conversaciones_duracion.empty else 0
    tiempo_total_raw = float(np.round(conversaciones_duracion.sum(), 2)) if not conversaciones_duracion.empty else 0

    duracion_mas_baja = formatea_duracion(duracion_mas_baja_raw)
    duracion_mas_alta = formatea_duracion(duracion_mas_alta_raw)
    duracion_promedio = formatea_duracion(duracion_promedio_raw)
    tiempo_total = formatea_duracion(tiempo_total_raw)

    # Limpieza defensiva de strings a UTF-8
    for col in ["texto", "name", "feedback_comment"]:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(lambda x: x.encode("utf-8", errors="replace").decode("utf-8"))

    reporte = {
        "cliente": cliente,
        "fecha_inicio": str(fecha_inicio),
        "fecha_fin": str(fecha_fin),
        "conversaciones": conversaciones,
        "interacciones": interacciones,
        "consultas_usuario": consultas_usuario,
        "respuestas_asistente": respuestas_asistente,
        "consultas_fuentes": consultas_fuentes,
        "otras": otras_interacciones,
        "tools": tools,
        "elementos": elementos,
        "mix_consultas_usuario": mix_consultas_usuario,
        "mix_respuestas_asistente": mix_respuestas_asistente,
        "mix_consultas_fuentes": mix_consultas_fuentes,
        "mix_otras_interacciones": mix_otras_interacciones,
        "feedback_positivo": feedback_positivo,
        "feedback_negativo": feedback_negativo,
        "total_registros": len(df),
        "time_series_dates": rango_fechas,
        "time_series_conversaciones": rango_conversaciones,
        "duracion_mas_baja": duracion_mas_baja,
        "duracion_mas_alta": duracion_mas_alta,
        "duracion_promedio": duracion_promedio,
        "tiempo_total": tiempo_total,
    }

    def safe_encode(value):
        if isinstance(value, str):
            return value.encode("utf-8", errors="replace").decode("utf-8")
        if isinstance(value, dict):
            return {k: safe_encode(v) for k, v in value.items()}
        if isinstance(value, list):
            return [safe_encode(v) for v in value]
        return value

    return safe_encode(reporte)

def insert_report(fecha_reporte: date, resumen_json: dict):
    # Reutilizamos el mismo engine; begin() maneja commit/rollback
    with engine.begin() as conn:
        resumen_limpio = json.dumps(resumen_json, ensure_ascii=False).encode("utf-8", errors="replace").decode("utf-8")
        conn.execute(
            text("""
                INSERT INTO reportes_metrics (fecha_reporte, resumen)
                VALUES (:fecha_reporte, :resumen)
            """),
            {"fecha_reporte": fecha_reporte, "resumen": resumen_limpio},
        )

if __name__ == "__main__":
    try:
        # Argumentos opcionales: python create_report.py 2025-06-01 2025-06-30
        if len(sys.argv) == 3:
            fecha_inicio = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
        else:
            fecha_inicio, fecha_fin = get_previous_month_range()

        hoy = date.today()
        logging.info(f"Generando reporte para el rango {fecha_inicio} a {fecha_fin}...")
        print("Generando...")
        reporte = generate_report(fecha_inicio, fecha_fin)
        insert_report(fecha_reporte=hoy, resumen_json=reporte)
        logging.info(f"Reporte generado y guardado correctamente para {fecha_inicio}.")
        print("OK")
    except Exception as e:
        # Limpia el pool por si quedó una conexión en mal estado tras excepción
        try:
            engine.dispose()
        except Exception:
            pass
        logging.error(f"Error generando reporte: {repr(e)}")
        print("ERROR", e)
        sys.exit(1)
