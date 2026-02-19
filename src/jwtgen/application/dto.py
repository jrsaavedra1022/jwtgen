from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Dict


@dataclass(frozen=True)
class SignJwtRequest:
    config_path: str
    env: str
    profile: str
    sub: str
    aud: Optional[str] = None
    iss: Optional[str] = None
    ttl: Optional[str] = None
    exp: Optional[int] = None
    extra_claims: Dict[str, Any] = field(default_factory=dict)
    payload_template: Optional[str] = None