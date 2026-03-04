from __future__ import annotations

import uuid
from typing import List


class IdentifierError(Exception):
    """Error de validación/generación de identificadores."""


def generate_uuid_v4() -> str:
    """
    Genera un UUID versión 4 en formato canónico RFC 4122.
    """
    return str(uuid.uuid4())


def generate_uuid_v4_batch(count: int) -> List[str]:
    """
    Genera `count` UUID v4 y valida que la cantidad sea válida.
    """
    if count < 1:
        raise IdentifierError("count debe ser mayor o igual a 1")

    return [generate_uuid_v4() for _ in range(count)]


def format_uuid(value: str, upper: bool = False, no_hyphen: bool = False) -> str:
    """
    Aplica formato de salida al UUID generado.
    """
    normalized = value.replace("-", "") if no_hyphen else value
    return normalized.upper() if upper else normalized
