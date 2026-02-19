from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Dict
from jwtgen.config.models import AppConfig


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class ResolvedProfile:
    env_name: str
    profile_name: str
    issuer_default: str
    audience_default: str
    alg: str
    default_ttl: str
    public_cer: str
    private_pem: str
    payload_template: str


class ConfigLoader:
    def __init__(self, path: str) -> None:
        self._path = path
        self._config: Optional[AppConfig] = None

    def load(self) -> AppConfig:
        if self._config is not None:
            return self._config

        data = self._read_yaml(self._path)
        try:
            self._config = AppConfig(**data)
        except Exception as e:
            raise ConfigError(f"Error validando configuración: {e}") from e

        return self._config

    def resolve(self, env: str, profile: str) -> ResolvedProfile:
        cfg = self.load()

        env_cfg = cfg.environments.get(env)
        if not env_cfg:
            available = ", ".join(sorted(cfg.environments.keys()))
            raise ConfigError(f"Ambiente '{env}' no existe. Disponibles: {available}")

        prof_cfg = env_cfg.profiles.get(profile)
        if not prof_cfg:
            available = ", ".join(sorted(env_cfg.profiles.keys()))
            raise ConfigError(f"Profile '{profile}' no existe en '{env}'. Disponibles: {available}")

        return ResolvedProfile(
            env_name=env,
            profile_name=profile,
            issuer_default=env_cfg.issuer_default,
            audience_default=prof_cfg.audience_default,
            alg=prof_cfg.alg,
            default_ttl=prof_cfg.defaults.ttl or "1h",
            payload_template=prof_cfg.payload_template or "generic",
            public_cer=prof_cfg.keys.public_cer,
            private_pem=prof_cfg.keys.private_pem,
        )

    def list_envs(self) -> list[str]:
        cfg = self.load()
        return sorted(cfg.environments.keys())

    def list_profiles(self, env: str) -> list[str]:
        cfg = self.load()
        env_cfg = cfg.environments.get(env)
        if not env_cfg:
            available = ", ".join(sorted(cfg.environments.keys()))
            raise ConfigError(f"Ambiente '{env}' no existe. Disponibles: {available}")
        return sorted(env_cfg.profiles.keys())

    def show_profile_safe(self, env: str, profile: str) -> dict[str, str]:
        resolved = self.resolve(env=env, profile=profile)

        return {
            "env": resolved.env_name,
            "profile": resolved.profile_name,
            "alg": resolved.alg,
            "issuer_default": resolved.issuer_default,
            "audience_default": resolved.audience_default,
            "default_ttl": resolved.default_ttl,
            "payload_template": resolved.payload_template,
        }

    @staticmethod
    def _read_yaml(path: str) -> Dict[str, Any]:
        import yaml
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            raise ConfigError(f"No existe archivo config: {path}")

        try:
            return yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as e:
            raise ConfigError(f"Error leyendo YAML: {e}") from e