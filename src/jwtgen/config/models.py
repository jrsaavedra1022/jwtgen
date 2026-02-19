from __future__ import annotations

from typing import Dict, Optional
from pydantic import BaseModel, Field


class KeyConfig(BaseModel):
    public_cer: str = Field(..., min_length=20, description="Certificado público X509 (PEM con BEGIN/END) en una sola línea")
    private_pem: str = Field(..., min_length=20, description="Llave privada PEM (BEGIN/END) en una sola línea")


class ProfileDefaults(BaseModel):
    ttl: Optional[str] = Field(default="1h", description="TTL por defecto (ej: 1h, 30m, 7d)")


class ProfileConfig(BaseModel):
    audience_default: str = Field(..., min_length=3)
    alg: str = Field(default="RS256")
    payload_template: str = Field(default="generic")
    keys: KeyConfig
    defaults: ProfileDefaults = Field(default_factory=ProfileDefaults)


class EnvironmentConfig(BaseModel):
    issuer_default: str = Field(..., min_length=2)
    profiles: Dict[str, ProfileConfig]


class AppConfig(BaseModel):
    environments: Dict[str, EnvironmentConfig]


class ProfileConfig(BaseModel):
    audience_default: str = Field(..., min_length=3)
    alg: str = Field(default="RS256")
    payload_template: str = Field(default="generic", description="Nombre del template en configs/payloads/<name>.json")
    keys: KeyConfig
    defaults: ProfileDefaults = Field(default_factory=ProfileDefaults)