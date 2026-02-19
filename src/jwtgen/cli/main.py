import typer
import json
from typing import List, Optional

from jwtgen.domain.claims import parse_claims_list, ClaimError
from jwtgen.application.dto import SignJwtRequest
from jwtgen.application.jwt_service import JwtService, JwtServiceError
from jwtgen.config.loader import ConfigLoader, ConfigError

app = typer.Typer(
    help="jwtgen: Generador de JWT RS256 por ambiente y perfiles (config YAML)."
)


@app.command()
def version() -> None:
    """
    Muestra la versión del CLI.
    """
    typer.echo("jwtgen 0.1.0")

@app.command("list-envs")
def list_envs(
    config: str = typer.Option(
        "configs/envs.example.yaml",
        "--config",
        "-c",
        help="Ruta al YAML con envs/profiles/keys",
    )
) -> None:
    """
    Lista ambientes disponibles en el archivo de configuración.
    """
    try:
        envs = ConfigLoader(config).list_envs()
    except ConfigError as e:
        raise typer.BadParameter(str(e))

    for e in envs:
        typer.echo(e)


@app.command("list-profiles")
def list_profiles(
    config: str = typer.Option(
        "configs/envs.example.yaml",
        "--config",
        "-c",
        help="Ruta al YAML con envs/profiles/keys",
    ),
    env: str = typer.Option(..., "--env", "-e", help="Ambiente a consultar"),
) -> None:
    """
    Lista profiles disponibles dentro de un ambiente.
    """
    try:
        profiles = ConfigLoader(config).list_profiles(env)
    except ConfigError as e:
        raise typer.BadParameter(str(e))

    for p in profiles:
        typer.echo(p)


@app.command("show-profile")
def show_profile(
    config: str = typer.Option(
        "configs/envs.example.yaml",
        "--config",
        "-c",
        help="Ruta al YAML con envs/profiles/keys",
    ),
    env: str = typer.Option(..., "--env", "-e", help="Ambiente"),
    profile: str = typer.Option(..., "--profile", "-p", help="Profile"),
) -> None:
    """
    Muestra detalles del profile (SIN llaves).
    """
    try:
        info = ConfigLoader(config).show_profile_safe(env=env, profile=profile)
    except ConfigError as e:
        raise typer.BadParameter(str(e))

    typer.echo(json.dumps(info, indent=2, ensure_ascii=False))
    
@app.command()
def sign(
    config: str = typer.Option(
        "configs/envs.example.yaml",
        "--config",
        "-c",
        help="Ruta al YAML con envs/profiles/keys",
    ),
    env: str = typer.Option(..., "--env", "-e", help="Ambiente (qa/dev/pdn, etc.)"),
    profile: str = typer.Option(..., "--profile", "-p", help="Perfil / app dentro del ambiente"),
    sub: str = typer.Option(..., "--sub", help="Subject (sub)"),
    aud: str = typer.Option(None, "--aud", help="Audience override"),
    iss: str = typer.Option(None, "--iss", help="Issuer override"),
    ttl: str = typer.Option(None, "--ttl", help="TTL relativo (ej: 1h, 30m, 7d)"),
    exp: int = typer.Option(None, "--exp", help="Exp epoch absoluto (tiene prioridad sobre ttl)"),
    claim: Optional[List[str]] = typer.Option(
        None,
        "--claim",
        help="Claim extra key=value (repetible). Ej: --claim scope=admin --claim channel=web",
    ),
    print_payload: bool = typer.Option(
        False,
        "--print-payload",
        help="Imprime el payload final (primero) antes del JWT",
    ),
    print_header: bool = typer.Option(
        False,
        "--print-header",
        help="Imprime el header final antes del JWT",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Imprime información de contexto (sin exponer llaves)",
    ),
    payload: str = typer.Option(
        None,
        "--payload",
        help="Nombre del template payload (configs/payloads/<name>.json). Override sobre el profile.",
    ),
) -> None:
    """
    Firma un JWT RS256 usando config YAML (env/profile), con claims extra opcionales.
    Salida por defecto: solo JWT.
    Con --print-payload: payload primero y luego JWT.
    """
    try:
        extra_claims = parse_claims_list(claim)
    except ClaimError as e:
        raise typer.BadParameter(str(e))

    service = JwtService()

    try:
        result = service.sign_rs256(
            SignJwtRequest(
                config_path=config,
                env=env,
                profile=profile,
                sub=sub,
                aud=aud,
                iss=iss,
                ttl=ttl,
                exp=exp,
                extra_claims=extra_claims,
                payload_template=payload,
            )
        )
    except JwtServiceError as e:
        raise typer.BadParameter(str(e))

    if verbose:
        typer.echo(f"config={config}")
        typer.echo(f"env={env} profile={profile}")

    if print_header:
        typer.echo("Header:")
        typer.echo(json.dumps(result.header, indent=2, ensure_ascii=False))

    if print_payload:
        typer.echo("Payload:")
        typer.echo(json.dumps(result.payload, indent=2, ensure_ascii=False))

    typer.echo(result.token)


if __name__ == "__main__":
    app()