"""
Módulo de herramientas.
Mantiene compatibilidad exportando CUSTOM_TOOLS tal como en el original.
"""

from QAgent.tools.tool_factory import ToolFactory
from QAgent.tools.data_tools import getdataMSQL, getdataASQLS, getdataGSQLS,createDataFrame, explainSQL, getdataSQLSLocal
from QAgent.tools.plotting_tools import draw_plotly_chart
from QAgent.tools.utility_tools import getCurrentDate, send_mail, qtokens, almacenar_interaccion, get_mysql_schema
from QAgent.tools.user_tools import register_user
from QAgent.tools.clima_tool import clima_actual, pronostico
from QAgent.tools.web_search_tool import web_search
from QAgent.tools.google_anatytic_v4_tools import google_analytic_report, google_analytic_concept
from QAgent.tools.multimedia_tools import video_tool, pdf_tool
from QAgent.tools.customer_tools import busca_rut_cliente, segmenta_cliente, busca_sku, recursos_conaf
from QAgent.tools.faiss_ai_search_tool import faiss_ai_search

# Define las herramientas del asistente manteniendo la misma estructura que el original
CUSTOM_TOOLS = {
    'getCurrentDate': getCurrentDate,
    'draw_plotly_chart': draw_plotly_chart,    
    'getdataMSQL': getdataMSQL,
    'getdataASQLS':getdataASQLS,
    'getdataGSQLS':getdataGSQLS,
    'send_mail': send_mail,
    'register_user': register_user,
    'clima_actual': clima_actual,
    'pronostico': pronostico,
    'web_search': web_search,
    'google_analytic_report': google_analytic_report,
    'google_analytic_concept':google_analytic_concept,
    'get_mysql_schema':get_mysql_schema,
    'video_tool':video_tool,
    'pdf_tool':pdf_tool,
    'busca_rut_cliente':busca_rut_cliente,
    'segmenta_cliente':segmenta_cliente,
    'busca_sku':busca_sku,
    'faiss_ai_search':faiss_ai_search,
    'createDataFrame': createDataFrame,
    'recursos_conaf':recursos_conaf,
    'explainSQL':explainSQL,
    'getdataSQLSLocal':getdataSQLSLocal

}

__all__ = [
    'CUSTOM_TOOLS', 
    'ToolFactory',
    'draw_plotly_chart',     
    'getCurrentDate', 
    'qtokens', 
    'almacenar_interaccion',
    'send_mail',
    'register_user',
    'clima_actual',
    'pronostico',
    'web_search',
    'google_analytic_report',
    'google_analytic_concept',
    'get_mysql_schema'
    'video_tool',
    'pdf_tool'
    'busca_rut_cliente',
    'segmenta_cliente',
    'busca_sku',
    'faiss_ai_search',
    'getdataASQLS',
    'getdataGSQLS',
    'getdataMSQL',
    'createDataFrame',
    'recursos_conaf',
    'explainSQL',
    'getdataSQLSLocal'
]
