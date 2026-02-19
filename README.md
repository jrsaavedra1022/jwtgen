# JWTGEN

## Generador de JWT RS256 por Ambientes y Perfiles

jwtgen es una herramienta de línea de comandos (CLI) para generar tokens JWT firmados con RS256, utilizando configuración por ambientes y perfiles.

Permite generar JWT sin necesidad de tener una aplicación corriendo. Solo requiere un archivo YAML de configuración y, opcionalmente, templates de payload.

---

### CARACTERÍSTICAS

- Firma JWT con RS256
- Soporte multi-ambiente (dev, qa, prod, etc.)
- Soporte multi-perfil (una API o aplicación por perfil)
- Templates de payload configurables
- Generación automática de iat y exp
- Soporte TTL relativo (1h, 30m, 7d, etc.)
- Claims adicionales dinámicos (--claim)
- Arquitectura limpia y mantenible

---

### REQUISITOS

- Python 3.10 o superior
- pip

---

### INSTALACIÓN

Clonar repositorio e instalar en entorno virtual:

macOS / Linux:

```bash
    git clone <repo>
    cd jwtgen
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install -e .
```
Windows (PowerShell):

```bash
    git clone <repo>
    cd jwtgen
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    py -m pip install -U pip
    pip install -e .
```

Verificar instalación:

```bash
    jwtgen --help
    jwtgen version
```
---

### CONFIGURACIÓN

La herramienta utiliza un archivo YAML para definir ambientes y perfiles.

Ejemplo:

```yaml
environments:
  qa:
    issuer_default: "JRSC0001"
    profiles:
      admin-service:
        audience_default: "example-cypher-api.com"
        alg: "RS256"
        payload_template: "admin_service"
        keys:
          public_cer: "-----BEGIN CERTIFICATE-----REPLACE_ME-----END CERTIFICATE-----"
          private_pem: "-----BEGIN PRIVATE KEY-----REPLACE_ME-----END PRIVATE KEY-----"
        defaults:
          ttl: "1h"

      payments-service:
        audience_default: "example-payments-api.com"
        alg: "RS256"
        payload_template: "generic"
        keys:
          public_cer: "-----BEGIN CERTIFICATE-----REPLACE_ME-----END CERTIFICATE-----"
          private_pem: "-----BEGIN PRIVATE KEY-----REPLACE_ME-----END PRIVATE KEY-----"
        defaults:
          ttl: "1h"
```
---

### EXPLICACIÓN DE CAMPOS

**environments**  
  Agrupa ambientes como dev, qa, prod.

**issuer_default**  
  Valor por defecto para el claim iss.

**profiles**  
  Cada perfil representa una API o aplicación distinta.

Dentro de cada profile:

- ***audience_default*** → valor por defecto del claim aud
- ***payload_template*** → nombre del template JSON
- ***keys.public_cer*** → certificado público
- ***keys.private_pem*** → llave privada para firmar
- ***defaults.ttl*** → tiempo de expiración por defecto

---

### TEMPLATES DE PAYLOAD

Los templates deben ubicarse en:

`configs/payloads/`

Ejemplo:

`configs/payloads/generic.json`
```json
{
  "scope": "read",
  "channel": "default"
}
```
Los claims estándar (iss, sub, aud, iat, exp) siempre son generados automáticamente.

---

### USO BÁSICO

Generar un JWT mínimo:

```bash
jwtgen sign -c secrets/envs.qa.yaml -e qa -p admin-service --sub user_123
```
Esto:

- Usa issuer_default del environment
- Usa audience_default del profile
- Genera iat automáticamente
- Calcula exp usando TTL por defecto
- Firma con la llave privada configurada

---
### MOSTRAR PAYLOAD ANTES DE FIRMAR
```bash
jwtgen sign -c secrets/envs.qa.yaml -e qa -p admin-service --sub user_123 --print-payload
```

Orden de salida:
1) Payload final
2) Token firmado

---
### CAMBIAR EXPIRACIÓN

TTL relativo:
```bash
jwtgen sign -c secrets/envs.qa.yaml -e qa -p admin-service --sub user_123 --ttl 8h
```
Expiración absoluta (epoch):
```bash
jwtgen sign -c secrets/envs.qa.yaml -e qa -p admin-service --sub user_123 --exp 1893456000
```
Prioridad de expiración:

1) --exp
2) --ttl
3) defaults.ttl

---

### SOBRESCRIBIR ISS O AUD
```bash
jwtgen sign -c secrets/envs.qa.yaml -e qa -p admin-service --sub user_123 --iss customIssuer --aud customAudience
```
---

### AGREGAR CLAIMS ADICIONALES

```bash
jwtgen sign -c secrets/envs.qa.yaml -e qa -p admin-service --sub user_123 --claim role=admin --claim active=true --claim level=5
```

Soporta:

- booleanos (true / false)
- números
- JSON (objetos o listas)
- strings

No permite sobrescribir iss, sub, aud, iat, exp usando --claim.

---

### COMANDOS ÚTILES

Listar ambientes:
```bash
jwtgen list-envs -c secrets/envs.qa.yaml
```
Listar perfiles:
```bash
jwtgen list-profiles -c secrets/envs.qa.yaml -e qa
```
Ver configuración de un perfil:
```bash
jwtgen show-profile -c secrets/envs.qa.yaml -e qa -p admin-service
```
El listado de comandos lo encuetras en:
```path
docs/commands.sh
```
---

### CÓMO FUNCIONA A NIVEL SIMPLE

1) Se selecciona un environment
2) Se selecciona un profile
3) Se construyen los claims estándar
4) Se aplica el template del profile
5) Se agregan claims adicionales si existen
6) Se firma con la llave privada
7) Se imprime el JWT

---

### ERRORES COMUNES

- No activar el entorno virtual
- YAML mal indentado
- Llaves mal formateadas
- Intentar sobrescribir claims estándar con --claim
- TTL inválido (formato incorrecto)

---

### NOTAS

- Las llaves privadas deben mantenerse seguras.
- No subir archivos reales con llaves a repositorios públicos.
- Usar archivos distintos por ambiente si es necesario.
