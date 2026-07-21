from __future__ import annotations

import json
from pathlib import Path


def cargar_documentos(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)
