"""
Herramientas para gestión de usuarios.
"""

import logging
import bcrypt
import json
import uuid
from datetime import datetime
from typing import Dict, Any

import chainlit as cl

from QAgent.tools.base_tool import BaseTool
from QAgent.repositories.postgres_repository import PostgresRepository
from QAgent.utils.logging_utils import notify_error, get_random_response

logger = logging.getLogger(__name__)

class RegisterUserTool(BaseTool):
    """
    Herramienta para registrar usuarios en la base de datos.
    """
    
    async def execute(self, email: str, password: str, role: str) -> Dict[str, Any]:
        """
        Registra un nuevo usuario en la base de datos
        
        Args:
            email: Correo electrónico del usuario
            password: Contraseña del usuario
            role: Rol del usuario (Admin, Analista, Usuario)
            
        Returns:
            Diccionario con resultado de la operación
        """
        try:
            # Validación básica
            if not email or not password:
                return {"success": False, "message": "Email y contraseña son obligatorios"}
            
            # Verificar si el usuario ya existe
            repo = PostgresRepository()
            existing_user = await repo.fetch(
                "SELECT id FROM users WHERE identifier = :identifier",
                {"identifier": email}
            )
            
            if existing_user:
                return {
                    "success": False, 
                    "message": f"Ya existe un usuario con el correo {email}"
                }
            
            # Generar hash de la contraseña
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Preparar datos
            user_id = str(uuid.uuid4())
            created_at = datetime.now().isoformat() + "Z"
            metadata = json.dumps({"role": role})
            
            # Registrar usuario
            await repo.execute(
                """
                INSERT INTO users (id, identifier, "createdAt", metadata, password_hash)
                VALUES (:id, :identifier, :createdAt, :metadata, :password_hash)
                ON CONFLICT (identifier) DO UPDATE
                SET metadata = :metadata, password_hash = :password_hash
                """,
                {
                    "id": user_id,
                    "identifier": email,
                    "createdAt": created_at,
                    "metadata": metadata,
                    "password_hash": password_hash
                }
            )
            
            logger.info(f"Usuario registrado: {email} con rol {role}")
            
            return {
                "success": True,
                "message": f"Usuario {email} registrado correctamente"
            }
        
        except Exception as err:
            # Gestión de errores
            modulo = "user_tools"
            funcion = "register_user"
            await notify_error(str(err), modulo, funcion)
            
            logger.error(f"Error al registrar usuario: {err}")
            return {
                "success": False,
                "message": f"Error al registrar usuario: {str(err)}"
            }

# Instancia de la herramienta
register_user = RegisterUserTool() 