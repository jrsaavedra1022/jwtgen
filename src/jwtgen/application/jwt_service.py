from __future__ import annotations

from jwtgen.application.dto import SignJwtRequest
from jwtgen.config.loader import ConfigLoader, ConfigError
from jwtgen.crypto.key_material import load_key_material_from_inline, KeyMaterialError
from jwtgen.crypto.signer import Rs256JwtSigner, JwtSignError, SignResult
from jwtgen.domain.claims import (
    StandardClaimsInput,
    build_standard_claims,
    ClaimError,
    render_payload_from_template,
)
from jwtgen.domain.templates import PayloadTemplateRepository, TemplateError


class JwtServiceError(Exception):
    pass


class JwtService:
    def __init__(self) -> None:
        self._signer = Rs256JwtSigner()
        self._templates = PayloadTemplateRepository()

    def sign_rs256(self, req: SignJwtRequest) -> SignResult:
        try:
            resolved = ConfigLoader(req.config_path).resolve(env=req.env, profile=req.profile)
        except ConfigError as e:
            raise JwtServiceError(str(e)) from e

        final_iss = req.iss or resolved.issuer_default
        final_aud = req.aud or resolved.audience_default
        final_ttl = req.ttl or resolved.default_ttl

        try:
            standard_claims = build_standard_claims(
                StandardClaimsInput(
                    iss=final_iss,
                    sub=req.sub,
                    aud=final_aud,
                    ttl=final_ttl,
                    exp=req.exp,
                )
            )
        except ClaimError as e:
            raise JwtServiceError(str(e)) from e

        template_name = req.payload_template or resolved.payload_template or "generic"
        try:
            template = self._templates.load(template_name)
        except TemplateError as e:
            raise JwtServiceError(str(e)) from e

        try:
            payload = render_payload_from_template(
                template=template,
                standard_claims=standard_claims,
                extra_claims=req.extra_claims,
            )
        except ClaimError as e:
            raise JwtServiceError(str(e)) from e

        try:
            keys = load_key_material_from_inline(
                public_cer_inline=resolved.public_cer,
                private_pem_inline=resolved.private_pem,
            )
        except KeyMaterialError as e:
            raise JwtServiceError(str(e)) from e

        try:
            return self._signer.sign(payload=payload, keys=keys, kid=None)
        except JwtSignError as e:
            raise JwtServiceError(str(e)) from e