# QAgent/tools/correlacion_pearson.py
import math
import pandas as pd
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text
from tenacity import retry, stop_after_attempt, wait_exponential
from QAgent.tools.base_tool import BaseTool
from QAgent.config.config_manager import config
import chainlit as cl
import json

class CorrelacionPearsonTool(BaseTool):
    """
    Calcula correlación de Pearson entre:
      - Ventas mensuales (SUM measures_envios_real)
      - Nivel de servicio mensual (AVG nivel_servicio_cliente)
    para un año dado.
    """

    _engine: Optional[AsyncEngine] = None

    def _get_engine(self) -> AsyncEngine:
        if self.__class__._engine is None:
            host = config.get("DB_HOST", "127.0.0.1")
            port = int(config.get("DB_MYSQL_PORT", 3306))
            db   = config.get("DB_NAME")
            user = config.get("DB_USER")
            pwd  = config.get("DB_PASSWORD", "")
            url = f"mysql+aiomysql://{user}:{pwd}@{host}:{port}/{db}"
            self.__class__._engine = create_async_engine(
                url, pool_size=10, max_overflow=20,
                pool_pre_ping=True, pool_recycle=3600,
            )
        return self.__class__._engine

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _pearson_from_series(x: pd.Series, y: pd.Series) -> float:
        n = len(x)
        if n < 2:
            return float("nan")
        sx = x.sum(); sy = y.sum()
        sxx = (x * x).sum(); syy = (y * y).sum()
        sxy = (x * y).sum()
        num = sxy - (sx * sy) / n
        den_x = sxx - (sx * sx) / n
        den_y = syy - (sy * sy) / n
        den = math.sqrt(max(den_x, 0.0)) * math.sqrt(max(den_y, 0.0))
        if den == 0:
            return float("nan")
        return num / den

    # Mapa robusto de meses cortos (ES) -> número
    _MONTH_MAP = {
        "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
        "jul": 7, "ago": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dic": 12,
    }
    _MONTH_LABEL = {
        1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
        7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"
    }

    @classmethod
    def _mes_to_num(cls, v) -> Optional[int]:
        # Si ya es número (o string numérico), úsalo
        try:
            n = int(v)
            if 1 <= n <= 12:
                return n
        except Exception:
            pass
        # Si es texto tipo "Ene", " sep ", "SEPT", etc.
        if isinstance(v, str):
            key = v.strip().lower()
            return cls._MONTH_MAP.get(key)
        return None

    @classmethod
    def _add_mes_num(cls, df: pd.DataFrame, col="mes") -> pd.DataFrame:
        if col not in df.columns:
            df["mes_num"] = pd.NA
            return df
        df = df.copy()
        df["mes_num"] = df[col].apply(cls._mes_to_num)
        return df

    @classmethod
    def _num_to_label(cls, n: int) -> str:
        return cls._MONTH_LABEL.get(int(n), str(n))

    @classmethod
    def _build_insight(cls, r: float, df: pd.DataFrame) -> str:
        if pd.isna(r):
            return "No fue posible calcular la correlación (serie constante o muy pocos puntos)."
        absr = abs(r)
        if absr >= 0.8:
            fuerza = "muy fuerte"
        elif absr >= 0.6:
            fuerza = "fuerte"
        elif absr >= 0.4:
            fuerza = "moderada"
        elif absr >= 0.2:
            fuerza = "débil"
        else:
            fuerza = "muy débil o nula"
        tendencia = "positiva" if r > 0 else "negativa"

        # Divergencia relativa
        df = df.copy()
        vmax = df["ventas"].max() or 0
        nsmax = df["ns"].max() or 0
        if vmax == 0 or nsmax == 0:
            return f"Correlación {fuerza} ({r:.3f}) y {tendencia}. No se pudo analizar divergencia por series nulas."

        df["diff_norm"] = (df["ventas"] / vmax) - (df["ns"] / nsmax)
        hot_idx = df["diff_norm"].abs().idxmax()
        hot_num = int(df.loc[hot_idx, "mes_num"])
        hot_lbl = cls._num_to_label(hot_num)

        return (
            f"Correlación {fuerza} ({r:.3f}) y {tendencia} entre ventas y nivel de servicio. "
            f"El mes con mayor divergencia relativa fue **{hot_lbl} ({hot_num:02d})**: "
            f"las curvas de ventas y servicio se separaron más que el resto."
        )

    # ---- ejecución -------------------------------------------------------
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, max=4), reraise=True)
    async def execute(self, anio: int) -> Dict[str, Any]:
        """
        Uso: correlacion_Pearson(anio=2024)
        Retorna (JSON):
          {
            "anio": 2024,
            "r": 0.73,
            "puntos": [{"mes_num":1,"mes":"Ene","ventas":..., "ns":...}, ...],
            "insight": "..."
          }
        """
        engine = self._get_engine()

        SQL_VENTAS = text("""
            SELECT be.mes, SUM(be.measures_envios_real) AS ventas
            FROM base_envios be
            WHERE be.anio = :anio
            GROUP BY be.mes
        """)
        SQL_NS = text("""
            SELECT c.mes, AVG(c.nivel_de_servicio_ajustado_cliente) AS ns
            FROM cep c
            WHERE c.anio = :anio
            GROUP BY c.mes
        """)

        async with engine.begin() as conn:
            ventas = await conn.run_sync(lambda sc: pd.read_sql(SQL_VENTAS, sc, params={"anio": anio}))
            ns     = await conn.run_sync(lambda sc: pd.read_sql(SQL_NS,     sc, params={"anio": anio}))

        # Normaliza meses (Ene/Feb/...) -> mes_num
        ventas = self._add_mes_num(ventas, "mes")
        ns     = self._add_mes_num(ns, "mes")

        # Descarta filas con mes inválido
        ventas = ventas.dropna(subset=["mes_num"])
        ns     = ns.dropna(subset=["mes_num"])

        # JOIN por mes_num para evitar problemas de espacios/casing en 'mes'
        df = pd.merge(
            ventas[["mes", "mes_num", "ventas"]],
            ns[["mes_num", "ns"]],
            on="mes_num", how="inner"
        )

        # Reasignar etiqueta canónica de mes a partir de mes_num
        df["mes"] = df["mes_num"].astype(int).apply(self._num_to_label)

        # Orden 1..12
        df = df.sort_values("mes_num")

        if df.empty or len(df) < 2:
            return json.dumps({
                "anio": anio, "r": None, "puntos": [],
                "insight": "No hay suficientes puntos para calcular correlación."
            }, ensure_ascii=False, separators=(",", ":"))

        r = self._pearson_from_series(df["ventas"].astype(float), df["ns"].astype(float))
        insight = self._build_insight(r, df)

        puntos = [
            {
                "mes_num": int(row.mes_num),
                "mes": str(row.mes),
                "ventas": float(row.ventas),
                "ns": float(row.ns),
            }
            for _, row in df.iterrows()
        ]

        result = {
            "anio": anio,
            "r": None if pd.isna(r) else float(r),
            "puntos": puntos,
            "insight": insight
        }
        return json.dumps(result, ensure_ascii=False, separators=(",", ":"))



@cl.step(type="tool")
async def correlacionPearson(anio: str) -> str:
    
    """
    Calcula correlación de Pearson ventas vs nivel de servicio para el año dado.
    """
    tool = CorrelacionPearsonTool()

    return await tool.execute(anio=anio)