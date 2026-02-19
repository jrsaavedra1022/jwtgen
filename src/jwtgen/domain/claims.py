from __future__ import annotations

import re
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Iterable, Tuple


class ClaimError(Exception):
    pass


_TTL_PATTERN = re.compile(r"^\s*(\d+)\s*([smhd])\s*$", re.IGNORECASE)
_RESERVED_STANDARD_KEYS = {"iss", "sub", "aud", "iat", "exp"}



def now_epoch() -> int:
    return int(time.time())


def parse_ttl_to_seconds(ttl: str) -> int:
    """
    Convierte TTL tipo '30m', '1h', '7d' a segundos.
    Soporta unidades:
      s = seconds
      m = minutes
      h = hours
      d = days
    """
    if ttl is None:
        raise ClaimError("TTL es None.")

    m = _TTL_PATTERN.match(ttl)
    if not m:
        raise ClaimError(f"TTL inválido '{ttl}'. Formatos válidos: 30m, 1h, 7d, 15s.")

    value = int(m.group(1))
    unit = m.group(2).lower()

    if value <= 0:
        raise ClaimError(f"TTL inválido '{ttl}': el valor debe ser > 0.")

    multiplier = {
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
    }[unit]

    return value * multiplier


@dataclass(frozen=True)
class StandardClaimsInput:
    iss: str
    sub: str
    aud: str
    ttl: str
    exp: Optional[int] = None
    iat: Optional[int] = None


def build_standard_claims(inp: StandardClaimsInput) -> Dict[str, Any]:
    """
    Construye claims estándar para JWT.
    - iat: epoch actual si no viene
    - exp: si viene inp.exp se respeta; si no, se calcula con ttl.
    """
    if not inp.iss:
        raise ClaimError("iss no puede ser vacío.")
    if not inp.sub:
        raise ClaimError("sub no puede ser vacío.")
    if not inp.aud:
        raise ClaimError("aud no puede ser vacío.")
    if not inp.ttl:
        raise ClaimError("ttl no puede ser vacío (use defaults.ttl o --ttl).")

    iat = inp.iat if inp.iat is not None else now_epoch()

    if inp.exp is not None:
        exp = int(inp.exp)
        if exp <= iat:
            raise ClaimError(f"exp ({exp}) debe ser > iat ({iat}).")
    else:
        ttl_seconds = parse_ttl_to_seconds(inp.ttl)
        exp = iat + ttl_seconds

    return {
        "iss": inp.iss,
        "sub": inp.sub,
        "aud": inp.aud,
        "iat": iat,
        "exp": exp,
    }

def parse_claim_kv(kv: str) -> Tuple[str, Any]:
    """
    Parsea 'key=value' con inferencia básica:
    - true/false -> bool
    - números -> int
    - JSON (empieza con { o [) -> dict/list
    - si no -> string
    """
    if kv is None or "=" not in kv:
        raise ClaimError(f"Claim inválido '{kv}'. Usa formato key=value")

    key, raw = kv.split("=", 1)
    key = key.strip()
    raw = raw.strip()

    if not key:
        raise ClaimError(f"Claim inválido '{kv}': key vacío")

    low = raw.lower()
    if low == "true":
        return key, True
    if low == "false":
        return key, False

    if re.fullmatch(r"-?\d+", raw):
        try:
            return key, int(raw)
        except Exception:
            pass

    if raw.startswith("{") or raw.startswith("["):
        try:
            return key, json.loads(raw)
        except Exception as e:
            raise ClaimError(f"Claim '{key}' tiene JSON inválido: {e}") from e

    return key, raw


def parse_claims_list(claims: Optional[Iterable[str]]) -> Dict[str, Any]:
    """
    Convierte lista de '--claim key=value' a dict.
    Rechaza claves duplicadas.
    """
    result: Dict[str, Any] = {}
    if not claims:
        return result

    for kv in claims:
        k, v = parse_claim_kv(kv)
        if k in result:
            raise ClaimError(f"Claim duplicado: '{k}'")
        result[k] = v

    return result


def merge_extra_claims(payload: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge de claims extra sobre payload.
    Por seguridad/claridad NO permite sobrescribir claves estándar (iss/sub/aud/iat/exp).
    """
    if not extra:
        return payload

    for k in extra.keys():
        if k in _RESERVED_STANDARD_KEYS:
            raise ClaimError(
                f"No puedes sobrescribir '{k}' usando --claim. Usa los parámetros dedicados (--iss/--aud/--sub/--ttl/--exp)."
            )

    merged = dict(payload)
    merged.update(extra)
    return merged

def render_payload_from_template(
    template: Dict[str, Any],
    standard_claims: Dict[str, Any],
    extra_claims: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Render final:
    1) parte de template (base)
    2) sobreescribe con standard_claims (iss/sub/aud/iat/exp)
    3) aplica extra_claims (ya validado que no pisa estándar)
    """
    if not isinstance(template, dict):
        raise ClaimError("Template inválido: debe ser un dict JSON.")

    payload = dict(template)
    payload.update(standard_claims)
    payload = merge_extra_claims(payload, extra_claims)
    return payload