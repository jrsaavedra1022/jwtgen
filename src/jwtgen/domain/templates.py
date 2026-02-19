from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class TemplateError(Exception):
    pass


class PayloadTemplateRepository:
    """
    Carga templates JSON desde un directorio (por defecto configs/payloads).
    """

    def __init__(self, base_dir: str = "configs/payloads") -> None:
        self._base = Path(base_dir)

    def load(self, template_name: str) -> Dict[str, Any]:
        if not template_name:
            raise TemplateError("template_name vacío")

        path = self._base / f"{template_name}.json"
        if not path.exists():
            raise TemplateError(f"No existe template: {path}")

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            raise TemplateError(f"Template JSON inválido ({path}): {e}") from e

        if not isinstance(data, dict):
            raise TemplateError(f"Template debe ser un JSON object (dict): {path}")

        return data