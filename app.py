"""
Punto de entrada principal de la aplicación.
Integra Chainlit con OpenAI Assistant y la nueva estructura modular.
"""

import logging
import os
import json
import re
import asyncio
import random
import traceback
import uuid
import bcrypt
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Callable

# Chainlit
import chainlit as cl
import chainlit.data as cl_data
from chainlit.config import config
from chainlit.element import Element
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.types import ThreadDict
from chainlit.input_widget import Select, TextInput

# SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# OpenAI
from openai import OpenAIError

# Módulos refactorizados
from QAgent.config.config_manager import config as app_config
from QAgent.events.event_handler import EventHandlerFactory
from QAgent.events.strategies.openai_event_strategy import OpenAIEventStrategy
from QAgent.services.openai_service import OpenAIService
from QAgent.tools import CUSTOM_TOOLS, register_user, submit_survey
from QAgent.prompt import instrucciones, instrucciones_adicionales, instrucciones_telegram, instrucciones_quinta, instrucciones_correos_de_chile, instrucciones_cpp, preguntas_frecuentes
from QAgent.utils.logging_utils import configure_logging, get_random_response
from QAgent.repositories.postgres_repository import PostgresRepository

# Configuración del logger
logger = logging.getLogger(__name__)
configure_logging(level=logging.DEBUG)

# Fecha y hora actual
now = datetime.now() 
hoy = now.strftime("%d-%m-%Y %H:%M:%S")

#------------------------------------------------------------------------
# Dependencias de LocalStorageClient
from fastapi.staticfiles import StaticFiles
from chainlit.server import app as chainlit_app
from QAgent.repositories.local_storage_client import LocalStorageClient

# 1️⃣  Storage local
LOCAL_DIR = "public/storage"

# Configuración del cliente de almacenamiento
#absolute_url="http://localhost:8000/public/storage",
storage_client = LocalStorageClient(
    base_dir=LOCAL_DIR,
    url_prefix="/public/storage",
    absolute_url=None  # Dejamos que use la URL relativa para mayor compatibilidad
)

# 2️⃣  Servir archivos estáticos (solo si estamos ejecutando directamente con chainlit)
if not hasattr(chainlit_app, "state"):
    chainlit_app.mount(
        "/public/storage",
        StaticFiles(directory=LOCAL_DIR),
        name="public-storage",
    )

#------------------------------------------------------------------------

# Configurar Chainlit
if os.name == 'nt':
    cl_data._data_layer = SQLAlchemyDataLayer(
        conninfo=app_config.get('CHAINLIT_DB_URI'),
        storage_provider=storage_client    
    )
else:
    cl_data._data_layer = SQLAlchemyDataLayer(
        conninfo=app_config.get('CHAINLIT_DB_URI'),
        storage_provider=storage_client
    )

# Configuración de UI
config.ui.name = "Qagent V2"

# Inicializar el servicio OpenAI
assistant = None
openai_service = None
try:
    openai_service = OpenAIService()
    assistant = openai_service.assistant
    logger.info(f"Servicio OpenAI inicializado: {assistant.name}")
except OpenAIError as e:
    logger.error(f"Error al inicializar OpenAI: {e}")
    raise

# Registrar la estrategia de eventos
event_factory = EventHandlerFactory()
event_factory.register_strategy("openai", OpenAIEventStrategy)


# Autenticación
@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    """Autenticación contra PostgreSQL con opción de superadmin desde variables de entorno"""
    try:
        # Verificar credenciales de superadmin definidas en variables de entorno
        super_admin_user = app_config.get("SUPER_ADMIN_USER")
        super_admin_pass = app_config.get("SUPER_ADMIN_PASS")
        
        # Si las credenciales de superadmin están definidas y coinciden
        if super_admin_user and super_admin_pass:
            if username == super_admin_user and password == super_admin_pass:
                return cl.User(
                    identifier=username,
                    metadata={"role": "Admin", "provider": "credentials"}
                )
        
        # Proceso normal de autenticación contra la base de datos
        repo = PostgresRepository()
        
        # Buscar usuario directamente
        user_data = await repo.fetchrow(
            "SELECT id, metadata, password_hash FROM users WHERE identifier = :identifier",
            {"identifier": username}
        )
        
        # Si no existe el usuario o no tiene password_hash, autenticación fallida
        if not user_data or not user_data.get("password_hash"):
            return None
        
        # Verificar contraseña con bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), user_data["password_hash"].encode('utf-8')):
            # Extraer rol del usuario de metadata
            metadata = {}
            try:
                if isinstance(user_data.get("metadata"), str):
                    metadata = json.loads(user_data.get("metadata", "{}"))
                else:
                    metadata = user_data.get("metadata", {})
            except:
                pass
            
            # Crear y devolver usuario autenticado
            return cl.User(
                identifier=username,
                metadata={"role": metadata.get("role", "user"), "provider": "credentials"}
            )
        
        return None
        
    except Exception as e:
        logger.error(f"Error de autenticación: {e}")
        return None

@cl.action_callback("fijar_grafico")
async def on_fijar_grafico(action: cl.Action):
    # Obtener thread_id y element_id del payload
    thread_id = action.payload.get("thread_id")
    element_id = action.payload.get("element_id")
    plotly_sql = action.payload.get("plotly_sql")

    if not thread_id or not element_id:
        await cl.Message(content="❌ Error: Información incompleta para fijar el gráfico").send()
        return

    try:
        session = Session()
        session.execute(
            text('UPDATE elements SET pin = 1, pin_sql = :plotly_sql WHERE id = :id AND "threadId" = :thread_id'),
            {"plotly_sql": plotly_sql, "id": element_id, "thread_id": thread_id}
        )
        session.commit()
       
        await cl.context.emitter.send_toast(
            message="Gráfico fijado correctamente!",
            type="success",
           
           
        )
        await action.remove()
        
           
            
    except Exception as e:
        logger.error(f"Error al fijar gráfico: {e}")
        await cl.Message(content="❌ Error al fijar el gráfico").send()
    finally:
        session.close()

@cl.action_callback("submit_survey")
async def on_submit_survey(action: cl.Action):
    try:
        payload = action.payload or {}
        # 1) Datos del formulario (front) – SurveyForm.jsx
        score = int(payload.get("score", 0))
        reason = (payload.get("reason") or "").strip()
        magic_wish = (payload.get("magicWish") or "").strip()

        # 2) Identifier desde la sesión
        user = cl.user_session.get("user") or {}
        if hasattr(user, "identifier"):
            identifier = getattr(user, "identifier") or "anónimo"
        elif isinstance(user, dict):
            identifier = user.get("identifier") or "anónimo"
        else:
            identifier = "anónimo"

        # 3) user_metadata desde la sesión (como dijiste)
        user_data = cl.user_session.get("user_data") or {}
        raw_user_metadata = user_data.get("user_metadata")
        if isinstance(raw_user_metadata, str):
            try:
                user_metadata = json.loads(raw_user_metadata)
            except Exception:
                user_metadata = {}
        elif isinstance(raw_user_metadata, dict):
            user_metadata = raw_user_metadata
        else:
            user_metadata = {}

        # 4) created_at en texto ISO con Z
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # 5) Guardar vía herramienta
        result = await submit_survey.execute(
            identifier=identifier,
            user_metadata=user_metadata,
            created_at=created_at,
            score=score,
            reason=reason,
            magic_wish=magic_wish
        )

        # Responder al front
        return result if isinstance(result, dict) else {"success": True}

    except Exception as e:
        await cl.Message(content=f"❌ Error al guardar encuesta: {e}").send()
        return {"success": False, "message": str(e)}

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="Modo Normal",
            markdown_description="Más rápido para preguntas simples",
            icon="/public/bot.svg",
        ),
        cl.ChatProfile(
            name="Modo Razonamiento profundo",
            markdown_description="Razonamiento para análisis y mayor complejidad",
            icon="/public/brain.svg",
        ),
    ]


async def process_files(files: List[Element]):
    # Upload files if any and get file_ids
    file_ids = []
    if len(files) > 0:
        file_ids = await openai_service.upload_files(files)
        logger.info(f"--> File_ids:{file_ids}")  
         

    return [
        {
            "file_id": file_id,
            "tools": [{"type": "code_interpreter"}, {"type": "file_search"}]
            if file.mime
            in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/markdown",
                "application/pdf",
                "text/plain",
            ]
            else [{"type": "code_interpreter"}],
        }
        for file_id, file in zip(file_ids, files)
    ]
    
    
    

# Continuación de la conversación
@cl.on_chat_resume
async def on_chat_resume(thread):
    logger.info("El usuario reanudó una sesión de chat anterior")     
    

# Callback para botones de acción
@cl.action_callback("action_button")
async def on_action(action):
    await cl.Message(content=f"Ejecutado {action.name}").send()
    await action.remove()

# Callback para acciones del formulario de usuario
@cl.action_callback("register_user")
async def on_register_user(action):
    try:
        # Obtener datos del payload
        email = action.payload.get("email")
        password = action.payload.get("password")
        role = action.payload.get("role", "Usuario")
        
        # Usar la herramienta register_user
        result = await register_user(email=email, password=password, role=role)
        
        # Devolver resultado
        return result
    except Exception as e:
        logger.error(f"Error en el callback register_user: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "message": str(e)}

# Configurar preguntas iniciales
@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="¿De qué se tratan los datos?",
            message="Sin realizar ni ejecutar análisis de los datos, por favor coméntame de qué se tratan los datos que manejas y qué análisis podemos obtener",
            icon="/public/learn.svg",
        ),
        cl.Starter(
            label="Preguntas más frecuentes",
            message="Lista las preguntas más frecuentes que puedes responder.",
            icon="/public/idea.svg",
        ),
         cl.Starter(
            label="Indicadores economicos",
            message="Necesito los indicadores economicos de hoy",
            icon="/public/indicadores.svg",
        )
    ]

# Función para crear manejadores de eventos
def create_event_handler():
    """Crea un nuevo manejador de eventos para OpenAI"""
    return event_factory.create_handler("openai", assistant.name)

# Configuración de SQLAlchemy
engine = create_engine(app_config.get('DB_URL'))
Session = sessionmaker(bind=engine)

@cl.on_chat_start
async def on_chat_start():
    
    print("algo se conecto")
    # Obtener thread ID del contexto
    context_thread_id = None
    if cl.context and hasattr(cl.context, 'session'):
        context_thread_id = cl.context.session.thread_id
    
    # Obtener o crear el thread ID de la sesión
    chainlit_thread_id = cl.user_session.get('chainlit_thread_id')
    if not chainlit_thread_id:
        # Si no hay ID en la sesión, usar el del contexto si existe
        if context_thread_id:
            chainlit_thread_id = context_thread_id
        else:
            # Si no hay ningún ID, crear uno nuevo
            chainlit_thread_id = str(uuid.uuid4())
        
        # Guardar en la sesión
        cl.user_session.set('chainlit_thread_id', chainlit_thread_id)
        chat_profile = cl.user_session.get("chat_profile")
        print(f"=== chat_profile on start:{chat_profile}")
       
    
    # Asegurar que el thread exista en la base de datos
    ensure_chainlit_thread_exists(chainlit_thread_id)
    
    # Obtener información del usuario
    user = cl.user_session.get("user")
    
    # Verificar si user es None o no tiene atributos necesarios
    if user is None:
        user_id = "anónimo"
        user_role = "usuario"
    else:
        # Acceder directamente a los atributos del objeto PersistedUser
        user_id = user.identifier if hasattr(user, "identifier") else "anónimo"
        
        if hasattr(user, "metadata") and user.metadata:
            # Asumiendo que metadata es un diccionario
            user_role = user.metadata.get("role", "usuario")
        else:
            user_role = "usuario"
    
    logger.info(f"===== INICIO DE SESIÓN =====")
    logger.info(f"Usuario: {user_id} (Rol: {user_role})")
    
       
    
    # Crear thread de OpenAI (API externa)
    openai_thread_id = cl.user_session.get('openai_thread_id')
    if not openai_thread_id:
        # Crear un thread en OpenAI
        openai_thread_id = await openai_service.create_thread()
        cl.user_session.set('openai_thread_id', openai_thread_id)


def ensure_chainlit_thread_exists(chainlit_thread_id):
    """Asegura que el thread de Chainlit exista en la base de datos local"""
    session = Session()
    try:
        # Verificar si el thread ya existe
        result = session.execute(
            text("SELECT id FROM threads WHERE id = :thread_id"), 
            {"thread_id": chainlit_thread_id}
        )
        thread_exists = result.fetchone()
        
        if not thread_exists:
            # Crear nombre para el thread de Chainlit
            thread_name = f"Thread {chainlit_thread_id[:8]}"
            
            # Crear el thread en la base de datos - usando nombres de columnas en minúsculas
            session.execute(
                text('INSERT INTO threads (id, "createdAt", name, metadata) VALUES (:id, :created_at, :name, :metadata)'),
                {
                    "id": chainlit_thread_id, 
                    "created_at": datetime.now().isoformat(), 
                    "name": thread_name, 
                    "metadata": "{}"  # JSON vacío para el campo metadata
                }
            )
            session.commit()
            logger.debug(f"Thread de Chainlit {chainlit_thread_id} creado en la base de datos")
    except Exception as e:
        logger.error(f"Error al verificar/crear thread de Chainlit: {e}")
        session.rollback()
    finally:
        session.close()

# Función auxiliar para verificar si el usuario es administrador
async def is_admin():
    """Verifica si el usuario actual tiene rol de administrador"""
    try:
        user = cl.user_session.get("user")
        if not user:
            # También podemos obtenerlo directamente de Chainlit
            user = cl.get_current_user()
            
        # Si no hay usuario autenticado, no es admin
        if not user:
            return False
            
        # Obtener el rol del usuario desde sus metadatos
        role = user.metadata.get("role", "").lower()
        return role == "admin"
    except Exception as e:
        logger.error(f"Error al verificar rol de usuario: {e}")
        return False

# Manejador principal de mensajes
@cl.on_message
async def main(message: cl.Message):
    print(f"==== Mensaje recibido ====")
    message_dict = message.to_dict()
    print(message_dict)
    print(f"Content: {message.content}")
    print(f"Output: {getattr(message, 'output', '')}")
    import pprint
    pprint.pprint(vars(message))
    
    
    
    # Obtener thread ID del contexto
    context_thread_id = None
    if cl.context and hasattr(cl.context, 'session'):
        context_thread_id = cl.context.session.thread_id
    
    # Obtener o crear el thread ID de la sesión
    chainlit_thread_id = cl.user_session.get('chainlit_thread_id')
    if not chainlit_thread_id:
        # Si no hay ID en sesión pero hay uno en contexto, usarlo
        if context_thread_id:
            chainlit_thread_id = context_thread_id
        else:
            # Crear uno nuevo si no hay ninguno
            chainlit_thread_id = str(uuid.uuid4())
        
        # Guardar en la sesión
        cl.user_session.set('chainlit_thread_id', chainlit_thread_id)
    
    # Asegurar que el thread exista en la base de datos
    ensure_chainlit_thread_exists(chainlit_thread_id)
    
    # Obtener usuario de la sesión
    user = cl.user_session.get("user")
    
    # Verificar si user es None o no tiene atributos necesarios
    if user is None:
        user_id = "anónimo"
        user_role = "usuario"
    else:
        # Acceder directamente a los atributos del objeto PersistedUser
        user_id = user.identifier if hasattr(user, "identifier") else "anónimo"
        
        if hasattr(user, "metadata") and user.metadata:
            # Asumiendo que metadata es un diccionario
            user_role = user.metadata.get("role", "usuario")
        else:
            user_role = "usuario"
    
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Mensaje de {user_id} (Rol: {user_role}): '{message.content[:30]}...'")
    
    # Código existente para verificación de comandos administrativos
    if message.content.startswith("/user"):
        if user_role != "Admin":
            logger.warning(f"⚠️ Intento de comando admin por usuario sin permisos: {user_id}")
            await cl.Message(content="⚠️ No tienes permisos suficientes para ejecutar este comando.").send()
            return
    
    solicitud = None
    
    # Manejar comandos especiales con verificación de permisos
    if message.content == "/user list":
        # Verificar si el usuario es administrador
        if not await is_admin():
            await cl.Message(content="❌ No tienes permisos para ver la lista de usuarios. Se requiere rol de administrador.").send()
            return
            
        # Consultar usuarios desde la base de datos
        try:
            repo = PostgresRepository()
            users = await repo.fetch("SELECT identifier, metadata, \"createdAt\" FROM users ORDER BY identifier")
            
            # Formatear los datos para el componente
            formatted_users = []
            for user in users:
                metadata = user.get("metadata", "{}")
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                created_at = user.get("createdAt", "")
                if created_at:
                    # Formatear fecha para que sea más legible
                    try:
                        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                
                formatted_users.append({
                    "email": user["identifier"],
                    "role": metadata.get("role", "usuario"),
                    "created_at": created_at
                })
            
            # Crear y mostrar el elemento personalizado
            users_list = cl.CustomElement(name="UsersList", props={"users": formatted_users})
            await cl.Message(content="Lista de usuarios registrados en la plataforma:", elements=[users_list]).send()
            return
        except Exception as e:
            logger.error(f"Error al listar usuarios: {e}")
            logger.error(traceback.format_exc())
            await cl.Message(content="❌ Error al obtener la lista de usuarios.").send()
            return
    
    
    # Verificar si el mensaje es el comando para registrar usuarios
    if message.content == "/user add":
        # Verificar si el usuario es administrador
        if not await is_admin():
            await cl.Message(content="❌ No tienes permisos para añadir usuarios. Se requiere rol de administrador.").send()
            return
            
        # Mostrar el formulario personalizado
        user_form = cl.CustomElement(name="UserForm", props={"email": "", "role": "Usuario"})
        await cl.Message(content="### Formulario de Registro de Usuario\n\nPor favor, complete el formulario para registrar un nuevo usuario.").send()
        await cl.Message(content="", elements=[user_form]).send()
        return
    
    if message.content.strip() == "/test_survey":
        cl.user_session.set("user", {"identifier": "tester@example.com"})
        cl.user_session.set("user_data", {"user_metadata": {"role": "analista", "society": "CL10"}})
        el = cl.CustomElement(name="SurveyForm")
        await cl.Message(content="Por favor responde la encuesta:", elements=[el]).send()
        return
    
    # Procesamiento normal
    message_content = solicitud if solicitud else message.content
    
    chat_profile = cl.user_session.get("chat_profile")      
    
    if chat_profile == "Modo Razonamiento profundo":
        RAZONAMIENTO = "--- # Primero Piensa bien tu respuesta y explica tu razonamiento antes de resolver la tarea. ---" 
    else:    
        RAZONAMIENTO = "" 
    
    # Obtener ID del thread de OpenAI
    openai_thread_id = cl.user_session.get('openai_thread_id')
    if not openai_thread_id:
        # Crear un thread en OpenAI si no existe
        openai_thread_id = await openai_service.create_thread()
        cl.user_session.set('openai_thread_id', openai_thread_id)
    
    
    now = datetime.now() 
    hoy = now.strftime("%d-%m-%Y %H:%M")
    hoy = f"--- ## Esta es la fecha de hoy: {hoy} --- "    
    
    #---------------------------------------------------------------#
    # Instrucciones adicionales
    # Definir aqui,  casos especiales para instrucciones adicionales
    
    # Normalizaciones previas
    raw_content = (message.content or "").strip()
   
    # 1) Construir additional_instructions de forma segura
    instrucciones_parts = []

    # Caso Telegram
    if raw_content.startswith("TELEGRAM_MSN:"):
        logger.info("---> Aplica instrucciones TELEGRAM_MSN ---")
        instrucciones_parts.append(instrucciones_telegram)
       

    # Caso “preguntas frecuentes”
    if raw_content == "Lista las preguntas más frecuentes que puedes responder.":
        instrucciones_parts.append(preguntas_frecuentes)

    # 2) Attachments (lista vacía si no hay)
    attachments = await process_files([el for el in message.elements if el.path]) or []
    print(f"->> Attachments: {attachments}")

    # 3) Hint por archivos
    if attachments:
        instrucciones_parts.append(
            "\n\n[NOTA]: El usuario ha cargado archivo(s). "
            "Revísalos y responde considerando su contenido."
        )

    # 4) Componer instrucciones + “hoy”
    additional_instructions = "".join(instrucciones_parts)
    assistant_payload = (hoy or "") + additional_instructions

    try:
        # Mensaje “assistant” con contexto + instrucciones
        await openai_service.add_message_to_thread(
            thread_id=openai_thread_id,
            role="assistant",
            content=assistant_payload,
            attachments=[],  # siempre lista vacía aquí
        )

        # Mensaje del usuario (puedes usar raw_content o message_content+RAZONAMIENTO)
        await openai_service.add_message_to_thread(
            thread_id=openai_thread_id,
            role="user",
            content=message_content + RAZONAMIENTO,
            attachments=attachments,  # [] si no hay archivos
        )

    except OpenAIError as e:
        logger.error(f"Error al añadir mensaje al hilo de OpenAI: {e}")
        logger.error(traceback.format_exc())

        
        if "Can't add messages to" in str(e):
            logger.info(f"Intento de agregar mensajes mientras un run está activo: {e}")
            response = get_random_response("tiempo")
            await cl.Message(response).send()
            
            # Extraer el ID de la ejecución
            pattern = r"run_[\w]+"
            run_id_matches = re.findall(pattern, str(e))
            
            if run_id_matches:
                # Cancelar la ejecución actual
                run_id = run_id_matches[0]
                try:
                    await openai_service.cancel_run(thread_id=openai_thread_id, run_id=run_id)
                    
                    # Esperar un momento y volver a intentar
                    await asyncio.sleep(1)
                    await openai_service.add_message_to_thread(
                        thread_id=openai_thread_id,
                        role='user',  
                        content=message.content,
                        attachments=attachments,
                    )
                except Exception as cancel_e:
                    logger.error(f"Error al cancelar ejecución: {cancel_e}")
                    logger.error(traceback.format_exc())
                    await cl.Message("Lo siento, estoy teniendo problemas técnicos. Por favor, intenta de nuevo en unos momentos.").send()
                    return
    
    
    try:
        # Ejecutar el hilo de OpenAI usando la función para crear manejadores de eventos
        await openai_service.run_thread(
            thread_id=openai_thread_id,
            event_handler_creator=create_event_handler
        )
    except OpenAIError as e:
        logger.error(f"Error al ejecutar el hilo de OpenAI: {e}")
        logger.error(traceback.format_exc())
        
        if "Can't add messages to" in str(e):
            logger.error(f"Intento de agregar mensajes mientras un run está activo: {e}")
            response = get_random_response("tiempo")
            await cl.Message(response).send()
        else:
            await cl.Message("Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta de nuevo con una consulta diferente.").send()
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        logger.error(traceback.format_exc())
        await cl.Message("Ha ocurrido un error inesperado. Por favor, intenta de nuevo más tarde.").send()

if __name__ == "__main__":
    # Este bloque no se ejecutará con Chainlit, pero es útil para pruebas
    print("Iniciando QAgent refactorizado...")
    print(f"Versión: 1.0.0 ({hoy})")
