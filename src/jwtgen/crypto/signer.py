from __future__ import annotations

import jwt

from dataclasses import dataclass
from typing import Any, Dict, Optional
from jwtgen.crypto.key_material import KeyMaterial


class JwtSignError(Exception):
    pass


@dataclass(frozen=True)
class SignResult:
    token: str
    header: Dict[str, Any]
    payload: Dict[str, Any]


class Rs256JwtSigner:
    def sign(self, payload: Dict[str, Any], keys: KeyMaterial, kid: Optional[str] = None) -> SignResult:
        if not isinstance(payload, dict) or not payload:
            raise JwtSignError("Payload vacío o inválido.")

        headers: Dict[str, Any] = {
            "typ": "JWT",
            "alg": "RS256",
        }
        if kid:
            headers["kid"] = kid

        try:
            token = jwt.encode(
                payload=payload,
                key=keys.private_key,
                algorithm="RS256",
                headers=headers,
            )
        except Exception as e:
            raise JwtSignError(f"Error firmando JWT RS256: {e}") from e

        return SignResult(token=token, header=headers, payload=payload)