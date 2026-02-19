from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes


class KeyMaterialError(Exception):
    pass


_PEM_HEADER_RE = re.compile(r"-----BEGIN ([A-Z0-9 \-]+)-----")
_PEM_FOOTER_RE = re.compile(r"-----END ([A-Z0-9 \-]+)-----")


def _wrap_base64_lines(b64: str, width: int = 64) -> str:
    b64 = re.sub(r"\s+", "", b64)
    return "\n".join(b64[i : i + width] for i in range(0, len(b64), width))


def normalize_pem_one_line(pem_one_line: str) -> bytes:
    """
    Recibe un PEM que puede venir en una sola línea (con BEGIN/END),
    y lo convierte a PEM válido con saltos de línea.
    Si ya viene con saltos, se retorna tal cual (normalizado).
    """
    if not pem_one_line or len(pem_one_line.strip()) < 20:
        raise KeyMaterialError("PEM vacío o inválido.")

    text = pem_one_line.strip()

    # Si ya contiene saltos, solo aseguramos trailing newline
    if "\n" in text:
        if not text.endswith("\n"):
            text += "\n"
        return text.encode("utf-8")

    header_m = _PEM_HEADER_RE.search(text)
    footer_m = _PEM_FOOTER_RE.search(text)

    if not header_m or not footer_m:
        raise KeyMaterialError("El PEM no contiene encabezado/fin BEGIN/END válido.")

    header = header_m.group(0)
    footer = footer_m.group(0)

    # Extraer cuerpo base64 entre header y footer
    body = text.replace(header, "").replace(footer, "")
    body_wrapped = _wrap_base64_lines(body, 64)

    normalized = f"{header}\n{body_wrapped}\n{footer}\n"
    return normalized.encode("utf-8")


@dataclass(frozen=True)
class KeyMaterial:
    public_key: PublicKeyTypes
    private_key: PrivateKeyTypes


def load_key_material_from_inline(public_cer_inline: str, private_pem_inline: str) -> KeyMaterial:
    """
    Carga:
    - public_cer_inline: certificado X.509 en PEM (una sola línea permitida)
    - private_pem_inline: llave privada en PEM (una sola línea permitida)
    """
    try:
        cert_pem = normalize_pem_one_line(public_cer_inline)
        cert = x509.load_pem_x509_certificate(cert_pem)
        public_key = cert.public_key()
    except Exception as e:
        raise KeyMaterialError(f"Error cargando certificado público (CER/PEM): {e}") from e

    try:
        private_pem = normalize_pem_one_line(private_pem_inline)
        private_key = load_pem_private_key(private_pem, password=None)
    except Exception as e:
        raise KeyMaterialError(f"Error cargando llave privada (PEM): {e}") from e

    return KeyMaterial(public_key=public_key, private_key=private_key)