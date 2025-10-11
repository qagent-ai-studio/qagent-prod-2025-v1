#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analisis_ia_standalone.py
Script stand-alone para generar e insertar el análisis IA (HTML) en la tabla public.analisis_ia,
reutilizando la misma consulta de threads/steps del reporte mensual.

Uso:
    python analisis_ia_standalone.py [YYYY-MM-DD] [YYYY-MM-DD]

- Si no pasas fechas, usa el rango del mes anterior.
- Requiere variables de entorno en .env (mismo esquema que create_report.py):
    DB_URL=postgresql://usuario:pass@host:puerto/dbname
    AZURE_OPENAI_ENDPOINT=...
    AZURE_OPENAI_API_KEY=...
    AZURE_OPENAI_API_VERSION=2024-05-01-preview (opcional; default igual)
    ANALYSIS_MODEL=GPT-4.1 (opcional; default GPT-4.1)
"""
import os
import sys
import json
import logging
from datetime import date, timedelta, datetime

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ==== Config .env ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise RuntimeError("DB_URL no está definido en .env")

# Normaliza driver: postgresql -> postgresql+psycopg2
if DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Logging
LOG_PATH = os.getenv("REPORT_LOG", "analisis_ia_standalone.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

# Engine global
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)

def get_previous_month_range():
    today = date.today().replace(day=1)
    last_month_end = today - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return last_month_start, last_month_end

def get_data_analisis(fecha_inicio: str, fecha_fin: str):
    """
    Retorna lista de dicts con los registros necesarios para el análisis IA.
    Fechas en formato 'YYYY-MM-DD'.
    """
    QUERY = text("""
        SELECT
            t.id AS thread_id,
            t.name AS thread_name,
            u."identifier" AS usuario,
            s.id AS step_id,
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

    with engine.connect() as conn:
        df = pd.read_sql_query(
            QUERY,
            conn,
            params={
                "fecha_inicio": f"{fecha_inicio} 00:00:00",
                "fecha_fin": f"{fecha_fin} 23:59:59",
            },
        )

    # Limpiezas
    if "feedback" in df.columns:
        df["feedback"] = df["feedback"].fillna("")
    # Excluir pasos 'run'
    if "type" in df.columns:
        df = df[~(df["type"] == "run")]

    # Tipos
    if "thread_id" in df.columns:
        df["thread_id"] = df["thread_id"].astype(str)
    if "step_id" in df.columns:
        df["step_id"] = df["step_id"].astype(str)

    # Saneos a UTF-8 en campos de texto para evitar \u00f3, etc.
    for col in ["texto", "name", "feedback_comment", "usuario", "thread_name"]:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(lambda x: x.encode("utf-8", errors="replace").decode("utf-8"))

    registros = df.to_dict(orient="records")
    return registros

def run_llm_analysis(registros: list) -> str:
    """
    Llama a Azure OpenAI ChatCompletions con el prompt de análisis y
    devuelve el HTML listo para insertar.
    """
    from openai import AzureOpenAI

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
    model = os.environ.get("ANALYSIS_MODEL", "GPT-4.1")
    if not endpoint or not api_key:
        raise RuntimeError("Faltan AZURE_OPENAI_ENDPOINT o AZURE_OPENAI_API_KEY en .env")

    client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)

    system_prompt = """
        # Debes analizar un data frame correspondiente a las conversaciones e interacciones de un chat con un Asistente IA.
        ## Explicación de los campos a analizar del DataFrame:
        | Campo            | Comentario |
        |------------------|------------|
        | thread_id        | Un thread_id es una conversación; cada conversación tiene varias interacciones descritas por su tipo (campo type). |
        | type             | - `user_message`: pregunta del usuario<br>- `assistant_message`: respuesta del asistente<br>- `tool`: herramienta usada<br>- `feedback`: feedback del usuario |
        | texto            | - Si type es `user_message`, es la pregunta del usuario.<br>- Si es `assistant_message`, es la respuesta (sin razonamiento oculto). |
        | usuario          | Identificador del usuario. |
        | feedback         | - `1` positivo, `0` negativo. |
        | feedback_comment | Comentario del usuario al responder feedback. |
        | createdAt        | Fecha de creación. |
        
        Basado en el dataset, responde:
        1) ¿Cuáles son los tenores/temas más frecuentes de las consultas? (lista de tópicos y ejemplos)
        2) ¿Qué tipos de análisis/información se solicitan con mayor frecuencia?
        3) Sentimiento general y señales de satisfacción/insatisfacción (usa feedback si existe).
        4) Conteo y calificación de conversaciones por el siguiente criterio:
        
        | **CALIFICACIÓN** | **DESCRIPCIÓN** |
        |------------------|------------------|
        | Perfecta | Responde sin problemas durante toda la conversación. Genera consultas a datos adecuadas. |
        | Aceptable | Responde, pero hay consultas subóptimas o búsquedas sin resultado. |
        | Necesita mejorar | Comportamientos erráticos parciales o consultas incorrectas/no ejecutadas. |
        | Fallida | Errático durante toda la conversación; sin consultas o incoherencias. |
        
        Agrega insights y oportunidades de mejora (breve). El formato de salida debe ser **HTML** listo para insertar en un <div> existente: NO incluyas <html>, <body> ni fences ```.
        No hagas preguntas al final.
    """.strip()

    content = json.dumps(registros, ensure_ascii=False)
    completion = client.chat.completions.create(
        model=model,
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
    )
    html = (completion.choices[0].message.content or "").encode("utf-8", errors="replace").decode("utf-8")
    return html

def save_analysis_html(fecha_reporte: date, html_analisis: str):
    """
    Inserta (o upsertea) el HTML en public.analisis_ia por fecha.
    """
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO public.analisis_ia (fecha, analisis)
                VALUES (:fecha, :analisis)
                ON CONFLICT (fecha) DO UPDATE
                SET analisis = EXCLUDED.analisis,
                    created_at = now();
            """),
            {"fecha": fecha_reporte, "analisis": html_analisis},
        )

def main():
    try:
        # Rango por CLI o por mes anterior
        if len(sys.argv) == 3:
            fecha_inicio = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
        else:
            fecha_inicio, fecha_fin = get_previous_month_range()

        print(f"Generando análisis IA para {fecha_inicio} a {fecha_fin}...")
        # 1) Datos base
        registros = get_data_analisis(str(fecha_inicio), str(fecha_fin))

        # 2) LLM
        html = run_llm_analysis(registros)

        # 3) Guardar (usa fecha_fin como fecha del análisis; si no viene, hoy)
        fecha_reporte = fecha_fin or date.today()
        save_analysis_html(fecha_reporte, html)

        print("✅ Análisis IA guardado correctamente.")
    except Exception as e:
        # Limpia el pool si hay error
        try:
            engine.dispose()
        except Exception:
            pass
        logging.error(f"Error en analisis_ia_standalone: {repr(e)}")
        print("❌ ERROR:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
