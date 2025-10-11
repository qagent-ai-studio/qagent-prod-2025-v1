"""
Archivo de compatibilidad para mantener las importaciones durante la transición.
Este archivo mantiene las mismas funciones y estructura que el original para 
que el código existente siga funcionando mientras se migra al nuevo diseño.
"""

import logging
import os
import json
import random
from datetime import datetime, timezone, date

# Re-exportar lo que está en las nuevas ubicaciones
from QAgent.tools.data_tools import getdataMSQL, getdataASQLS, getdataASQLS_AD, getdataGSQLS, createDataFrame, explainSQL,  explainGCPSQL, explainASQL, getdataSQLSLocal
from QAgent.tools.plotting_tools import draw_plotly_chart
from QAgent.tools.utility_tools import getCurrentDate, send_mail, qtokens, almacenar_interaccion, get_mysql_schema,getMySQLTablesAndColumns, getMySQLRelationships,getASQLSTablesAndColumns, getASQLSRelationships
from QAgent.tools.clima_tool import clima_actual, pronostico
from QAgent.tools.web_search_tool import web_search
from QAgent.tools.google_anatytic_v4_tools import google_analytic_report, google_analytic_concept
from QAgent.tools.user_tools import register_user, submit_survey
from QAgent.tools.multimedia_tools import video_tool,pdf_tool
from QAgent.tools.customer_tools import busca_rut_cliente, segmenta_cliente, busca_sku, recursos_conaf
from QAgent.tools.faiss_ai_search_tool import faiss_ai_search
from QAgent.tools.blueraptor_tool import blueRaptor    
from QAgent.tools.sky_tool import audit_excel_tool   
from QAgent.tools.indicadores_tool import indicadores
from QAgent.tools.correlacion_pearson_tool import correlacionPearson

# Configuración del logger
logger = logging.getLogger(__name__)

# Mantenemos la misma estructura CUSTOM_TOOLS para compatibilidad
# COMENTAR LAS QUE NO SE UTILIZARÁN
CUSTOM_TOOLS = {
    'getCurrentDate': getCurrentDate,
    'register_user': register_user,
    'submit_survey':submit_survey,
    'draw_plotly_chart': draw_plotly_chart,    
    'getdataMSQL': getdataMSQL,
    'getdataASQLS':getdataASQLS,
    'getdataASQLS_AD':getdataASQLS_AD,
    'getdataGSQLS':getdataGSQLS,
    'send_mail': send_mail,
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
    'getdataSQLSLocal':getdataSQLSLocal,
    'explainGCPSQL':explainGCPSQL, 
    'explainASQL':explainASQL,
    'getMySQLTablesAndColumns':getMySQLTablesAndColumns, 
    'getMySQLRelationships':getMySQLRelationships,
    'getASQLSTablesAndColumns':getASQLSTablesAndColumns, 
    'getASQLSRelationships':getASQLSRelationships,
    'blueRaptor':blueRaptor,
    'audit_excel_tool':audit_excel_tool,
    'indicadores':indicadores,
    'correlacionPearson':correlacionPearson
    
}

# Funciones originales re-exportadas para compatibilidad
def respuestas_error():
    respuestas = [
        "Estoy replanteando la consulta, por favor dame un momento.",
        "Permíteme unos instantes para revisar la información.",
        "Estoy trabajando en tu solicitud, un momento por favor.",
        "Déjame verificar los detalles, esto tomará solo un momento.",
        "Por favor, espera un instante mientras reviso la información.",
        "Estoy buscando la mejor solución para ti, dame un momento.",
        "Gracias por tu paciencia, ya casi lo tengo.",
        "Solo un momento más, estoy revisando los datos.",
        "Déjame asegurarme de que todo esté correcto, un momento por favor.",
        "Estoy en ello, gracias por tu paciencia.",
        "Un momento mientras confirmo la información.",
        "Estoy analizando tu solicitud, esto tomará solo un instante.",
        "Por favor, espera un momento mientras termino de revisar.",
        "Estoy ajustando algunos detalles, dame unos segundos.",
        "Gracias por tu paciencia, ya estoy trabajando en ello."
    ]

    return random.choice(respuestas)


def respuestas_tiempo():
    respuestas = [
        "Estoy teniendo problemas para procesar los datos, dame unos segundos para intentar solucionarlo ",
        "Estoy presentando problemas con la respuesta, permíteme unos instantes para revisar la información.",
        "Estoy trabajando en tu solicitud, un momento por favor.",
        "Estoy buscando la mejor solución para ti, dame unos segundos.",
        "Algo paso con los datos, pero voy a tratar de resolverlo",
        "Hubo un problema técnico pero voy a intenetar solucionarlo, gracias por tu paciencia.",      
    ]

    return random.choice(respuestas)

 
