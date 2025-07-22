from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union

from chainlit.data.storage_clients.base import BaseStorageClient
from chainlit.logger import logger


class LocalStorageClient(BaseStorageClient):
    def __init__(
        self,
        base_dir: str | Path = "public/storage",
        url_prefix: str = "/public/storage",
        absolute_url: str | None = None,  # p.e. "http://localhost:8000/public/storage"
    ):
        self.base_dir = Path(base_dir).expanduser().resolve()
        self.url_prefix = url_prefix.strip("/")          # "public/storage"
        self.absolute_url = absolute_url.rstrip("/") if absolute_url else None
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorageClient → {self.base_dir}")

    # ───────────────────────────── upload_file ──────────────────────────
    async def upload_file(
        self,
        object_key: str,
        data: Union[bytes, str],
        mime: str = "application/octet-stream",
        overwrite: bool = True,
    ) -> Dict[str, Any]:

        # añade .json si corresponde
        from pathlib import Path
        if mime == "application/json" and Path(object_key).suffix == "":
            object_key = f"{object_key}.json"
            
        if mime == "application/pdf" and Path(object_key).suffix == "":
            object_key = f"{object_key}.pdf"

        path = self.base_dir / object_key
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not overwrite:
            raise FileExistsError(path)

        if isinstance(data, str):
            data = data.encode()

        path.write_bytes(data)
        stat = path.stat()

        url = (
            f"{self.absolute_url}/{object_key}"
            if self.absolute_url
            else f"/{self.url_prefix}/{object_key}"
        )

        return {
            "object_key": object_key,
            "url": url,
            "size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "content_type": mime,
        }

    # ─────────────────────────── get_read_url ───────────────────────────
    async def get_read_url(self, object_key: str) -> str:
        if self.absolute_url:
            return f"{self.absolute_url}/{object_key}"
        return f"/{self.url_prefix}/{object_key}"

    async def delete_file(self, object_key: str)-> str:
        pass
    
    
    """
    
    Producción vs. desarrollo
    En prod solo cambias absolute_url (p.e. https://mi-dominio.com/public/storage)
    y, si tu servidor corre detrás de un proxy/Nginx, asegúrate de redirigir el
    mismo path al contenedor/app.

    Si no quieres hard-codear localhost, lee el host desde una variable de entorno
    (BASE_PUBLIC_URL) y pásala a absolute_url.

    Con esta configuración el archivo vive en public/storage/… y la base de datos siempre almacena la URL completa que tus clientes necesitan.
    
    """