from dotenv import load_dotenv
load_dotenv()

import app  

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid

from chainlit.context import ChainlitContext, HTTPSession, context_var
from chainlit.message import Message
from chainlit.emitter import BaseChainlitEmitter
from chainlit.config import config
import asyncio

webhook_app = FastAPI()  # OJO: no llames a esto 'app' si ya existe

class Consulta(BaseModel):
    usuario: str
    mensaje: str

class WebhookEmitter(BaseChainlitEmitter):
    def __init__(self, session):
        super().__init__(session)
        self.last_output = None

    async def send_step(self, step_dict):
        print("\n----- > WebhookEmitter send_step", step_dict)  # DEBUG
        if step_dict.get("type") == "assistant_message" and step_dict.get("output"):
            self.last_output = step_dict.get("output")

    async def update_step(self, step_dict):
        print("\n----- > WebhookEmitter update_step", step_dict)  # DEBUG
        if step_dict.get("type") == "assistant_message" and step_dict.get("output"):
            self.last_output = step_dict.get("output")



@webhook_app.post("/webhook")
async def recibir_mensajes(consulta: Consulta):
    session = HTTPSession(
        id=str(uuid.uuid4()),
        thread_id=str(uuid.uuid4()),  # o el mapping usuario→hilo si lo deseas persistente
        user=consulta.usuario,
        client_type="webhook"
    )
    emitter = WebhookEmitter(session)
    context = ChainlitContext(session=session, emitter=emitter)
    context_var.set(context)

    msg = Message(
        content=consulta.mensaje,
        type="user_message",
        author=consulta.usuario
    )
    
    # Llama al handler de inicio de chat si existe
    if on_chat_start := config.code.on_chat_start:
        await on_chat_start()
        
    await msg.send()
    
    # Llama al handler principal del assistant si existe
    if on_message := config.code.on_message:
        await on_message(msg)

    # (Opcional) Llama al handler de fin de chat si existe
    if on_chat_end := config.code.on_chat_end:
        await on_chat_end()

    # Espera hasta 10 segundos por la respuesta completa del bot
    for _ in range(20):  # 20*0.5 = 10 segundos máx
        if emitter.last_output:
            break
        await asyncio.sleep(0.5)

    respuesta = emitter.last_output or "Sin respuesta"
    return JSONResponse({"respuesta": respuesta})

# Comando
# uvicorn hook:webhook_app --reload --port 8050