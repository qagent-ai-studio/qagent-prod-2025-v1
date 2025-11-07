"""
Servicio para generar reportes de conversaciones.
Procesa datos de threads y steps para crear reportes interactivos.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from QAgent.config.config_manager import config

logger = logging.getLogger(__name__)

class ReportService:
    """
    Singleton para gestionar la generación de reportes de conversaciones.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReportService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa el servicio de reportes"""
        # Usar la misma configuración de SQLAlchemy que main.py
        from sqlalchemy import create_engine

        db_uri = config.get('CHAINLIT_DB_URI')
        if 'postgresql+asyncpg' in db_uri:
            db_uri = db_uri.replace('postgresql+asyncpg', 'postgresql+psycopg2')

        self.engine = create_engine(db_uri)
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Servicio de reportes inicializado")

    def _safe_strip(self, value):
        """Safely strip a value that might be None"""
        return (value or "").strip()

    def format_duration_ms(self, ms: int) -> str:
        """Formatea duración de milisegundos a formato legible"""
        if not ms or ms < 0:
            return "0:00"
        s = ms // 1000
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        if h:
            return f"{h:d}:{m:02d}:{s:02d}"
        return f"{m:d}:{s:02d}"

    def parse_datetime(self, dt):
        """Parsea datetime desde varios formatos posibles"""
        if isinstance(dt, datetime):
            return dt
        if not dt:
            return None
        try:
            return datetime.fromisoformat(str(dt).replace("Z", ""))
        except Exception:
            return None

    def load_threads_with_interactions(
        self,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        user_identifier: Optional[str] = None,
        max_threads: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Carga threads con sus interacciones desde la base de datos.

        Args:
            fecha_inicio: Fecha de inicio para filtrar (formato: YYYY-MM-DD)
            fecha_fin: Fecha de fin para filtrar (formato: YYYY-MM-DD)
            user_identifier: Identificador del usuario para filtrar
            max_threads: Número máximo de threads a retornar

        Returns:
            Lista de threads procesados con sus interacciones
        """
        # Construir query base
        query = """
            SELECT
                t.id AS thread_id,
                t.name AS thread_name,
                u."identifier" AS usuario,
                u.metadata->>'role' AS user_role,
                u.user_metadata->>'Sucursal' AS sucursal,
                u.user_metadata->>'nombre' AS nombre_usuario,
                s.id AS step_id,
                s.start AS inicio,
                s."end" AS final,
                CASE
                    WHEN s.type = 'run' AND f.value IS NOT NULL THEN 'feedback'
                    ELSE s.type
                END AS type,
                s.name,
                CASE
                    WHEN s.type = 'tool' THEN NULL
                    ELSE s.output
                END AS texto,
                s.input AS tool_input,
                s.output AS tool_output,
                f.value AS feedback,
                f."comment" AS feedback_comment,
                e."type" AS element_type,
                s."createdAt"
            FROM public.threads t
            JOIN public.steps s ON s."threadId" = t.id
            LEFT JOIN public.users u ON u.id = t."userId"
            LEFT JOIN public.feedbacks f ON f."forId" = s.id
            LEFT JOIN public.elements e ON e."forId" = s.id
            WHERE (s.type <> 'run' OR f.value IS NOT NULL)
        """

        params = {}

        # Agregar filtros opcionales
        filters = []
        if fecha_inicio:
            # PostgreSQL compara correctamente strings ISO 8601
            filters.append('s."createdAt" >= :fecha_inicio')
            params['fecha_inicio'] = f"{fecha_inicio}T00:00:00"
            logger.info(f"Filtro fecha_inicio aplicado: {params['fecha_inicio']}")

        if fecha_fin:
            # PostgreSQL compara correctamente strings ISO 8601
            filters.append('s."createdAt" <= :fecha_fin')
            params['fecha_fin'] = f"{fecha_fin}T23:59:59"
            logger.info(f"Filtro fecha_fin aplicado: {params['fecha_fin']}")

        if user_identifier:
            filters.append('u."identifier" = :user_identifier')
            params['user_identifier'] = user_identifier

        if filters:
            query += " AND " + " AND ".join(filters)

        query += ' ORDER BY s."createdAt" DESC'

        try:
            logger.info(f"Ejecutando query de reporte con filtros: {params}")
            session = self.Session()
            try:
                result = session.execute(text(query), params)
                # Convertir resultados a diccionarios
                rows = [dict(row._mapping) for row in result]
                logger.info(f"Registros devueltos: {len(rows)}")
            finally:
                session.close()

            # Agrupar por thread_id
            threads_rows = defaultdict(list)
            for r in rows:
                tid = self._safe_strip(str(r.get("thread_id", "")))
                if tid:
                    threads_rows[tid].append(r)

            # Limitar threads si se especifica
            tids = list(threads_rows.keys())
            if max_threads:
                tids = tids[:max_threads]

            logger.info(f"Threads a procesar: {len(tids)}")

            threads = []
            for tid in tids:
                steps = threads_rows[tid]

                # IMPORTANTE: Ordenar steps cronológicamente para procesamiento correcto
                # La query principal usa ORDER BY DESC para ordenar threads, pero necesitamos
                # procesar los steps de cada thread en orden cronológico
                steps.sort(key=lambda x: x.get("createdAt") or "")

                # Metadata del thread
                thread_name = self._safe_strip(steps[0].get("thread_name")) or "Sin título"
                usuario = self._safe_strip(steps[0].get("usuario")) or "Usuario desconocido"
                first_dt = self.parse_datetime(steps[0].get("createdAt"))
                fecha_header = first_dt.strftime("%d-%m-%Y") if first_dt else ""

                # Estado del bloque actual
                current_user_text = None
                current_user_time = None
                current_assistant_final = None
                current_assistant_time = None
                current_tools = []
                current_feedbacks = []

                interactions = []

                def flush_block():
                    nonlocal current_user_text, current_user_time
                    nonlocal current_assistant_final, current_assistant_time
                    nonlocal current_tools, current_feedbacks

                    if current_user_text and current_assistant_final:
                        dur_ms = 0
                        if current_assistant_time and current_user_time:
                            dur_ms = int((current_assistant_time - current_user_time).total_seconds() * 1000)

                        interactions.append({
                            "user_text": (current_user_text or "").strip(),
                            "assistant_text": (current_assistant_final or "").strip(),
                            "user_time": current_user_time.isoformat() if current_user_time else None,
                            "assistant_time": current_assistant_time.isoformat() if current_assistant_time else None,
                            "duration_ms": max(dur_ms, 0),
                            "tools": current_tools[:],
                            "feedbacks": current_feedbacks[:],
                        })

                    # Reset de bloque
                    current_user_text = None
                    current_user_time = None
                    current_assistant_final = None
                    current_assistant_time = None
                    current_tools = []
                    current_feedbacks = []

                # Procesar steps
                for s in steps:
                    tipo = self._safe_strip(s.get("type"))
                    name = self._safe_strip(s.get("name"))
                    raw_texto = s.get("texto", "")
                    texto = raw_texto.strip() if raw_texto else ""

                    # Limpiar texto excesivo
                    if texto:
                        texto = '\n'.join(line.strip() for line in texto.split('\n') if line.strip())

                    createdAt = self.parse_datetime(s.get("createdAt"))
                    fb_val = s.get("feedback")
                    fb_comment = self._safe_strip(s.get("feedback_comment"))

                    if tipo == "user_message":
                        flush_block()
                        current_user_text = texto
                        current_user_time = createdAt

                    elif tipo == "assistant_message":
                        if current_user_text and texto.strip():  # Solo procesar si hay contenido
                            # Solo mantener el mensaje de asistente más reciente cronológicamente
                            # Esto es importante porque con ORDER BY DESC, podemos procesar mensajes intermedios antes que los finales
                            if not current_assistant_final or (createdAt and current_assistant_time and createdAt > current_assistant_time):
                                current_assistant_final = texto
                                current_assistant_time = createdAt

                    elif tipo == "tool":
                        if current_user_text:
                            # Intentar parsear el input como JSON para extraer la query
                            query_sql = None
                            tool_output = None

                            # Procesar el input (contiene la query SQL) - ahora en tool_input
                            try:
                                input_data = s.get("tool_input", "")
                                if input_data:
                                    # El input puede ser un string JSON o directamente un dict
                                    if isinstance(input_data, str):
                                        input_json = json.loads(input_data)
                                    else:
                                        input_json = input_data
                                    # Extraer la query SQL del JSON
                                    query_sql = input_json.get("consulta", None)
                            except (json.JSONDecodeError, Exception) as e:
                                logger.debug(f"No se pudo parsear JSON del tool input: {e}")
                                query_sql = None

                            # Procesar el output (contiene el resultado) - ahora en tool_output
                            raw_output = s.get("tool_output", "")
                            if raw_output:
                                # Intentar parsear el output como JSON para obtener resultado más limpio
                                try:
                                    if isinstance(raw_output, str) and raw_output.strip().startswith('['):
                                        # Es un resultado JSON array, mostrarlo formateado
                                        output_json = json.loads(raw_output)
                                        if isinstance(output_json, list) and len(output_json) > 0:
                                            # Formatear como texto simple si es una lista de resultados
                                            tool_output = json.dumps(output_json, ensure_ascii=False, indent=2)
                                        else:
                                            tool_output = raw_output
                                    else:
                                        tool_output = raw_output
                                except:
                                    # Si no se puede parsear, usar el texto tal cual
                                    tool_output = raw_output

                                # Truncar si es muy largo
                                if tool_output and len(tool_output) > 3000:
                                    tool_output = tool_output[:3000] + " …[truncado]"

                            current_tools.append({
                                "name": name or "(sin nombre)",
                                "query": query_sql,  # Query SQL extraída
                                "output": tool_output  # Resultado procesado
                            })

                    elif tipo == "feedback":
                        try:
                            val = int(fb_val) if fb_val is not None else None
                        except Exception:
                            val = None
                        current_feedbacks.append({
                            "value": val,
                            "comment": fb_comment
                        })

                # Cerrar último bloque
                flush_block()

                # Duración total del hilo
                total_ms = sum(it["duration_ms"] for it in interactions)

                threads.append({
                    "thread_id": tid,
                    "thread_name": thread_name,
                    "usuario": usuario,
                    "fecha": fecha_header,
                    "total_duration_ms": total_ms,
                    "interactions": interactions
                })

            logger.info(f"Interacciones totales: {sum(len(t['interactions']) for t in threads)}")
            return threads

        except Exception as e:
            logger.error(f"Error al cargar threads: {str(e)}")
            raise RuntimeError(f"Error al obtener datos de conversaciones: {str(e)}")

    def create_mock_judgments(self, threads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Crea evaluaciones simuladas para compatibilidad con el template.
        En el futuro se puede integrar con evaluación LLM real.
        """
        for t in threads:
            judgments = []
            for it in t["interactions"]:
                # Por ahora, evaluación vacía
                mock_judgment = {
                    "label": "Sin evaluar",
                    "score": None,
                    "rationale": "",
                    "checks": {},
                    "notes": []
                }
                judgments.append(mock_judgment)

            t["judgments"] = judgments

            # Emparejar interacciones + juicios para el template
            entries = []
            for i in range(len(t["interactions"])):
                entries.append({
                    "it": t["interactions"][i],
                    "j": t["judgments"][i]
                })
            t["entries"] = entries

        return threads