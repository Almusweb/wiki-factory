#!/usr/bin/env python3
"""Accesso agli oggetti dei bucket S3-compatibili con le credenziali di un file env locale (capability
object_storage_access, opt-in).

Sottocomandi (output JSON su stdout, diagnostica su stderr):

  targets [--env ENV]                               registro + stato credenziali, nessuna connessione
  check   ENV TARGET                                credenziali, raggiungibilita' del bucket, TLS
  list    ENV TARGET [--prefix P] [--no-recursive] [--max N]
                                                    oggetti (chiave, dimensione, data, etag)
  stat    ENV TARGET --object K                     metadati di un oggetto
  download ENV TARGET --object K [--dest D]         file singolo, o cartella se K termina con /
  presign ENV TARGET --object K [--expires S]       link pre-firmato di lettura
  renew-link --url U [--expires S]                  nuovo link pre-firmato per lo stesso oggetto
  upload  ENV TARGET --file F [--object K] --dry-run
  upload  ENV TARGET --file F [--object K] --commit --token T --human-gate-approved [--confirm-env ENV]
  delete  ENV TARGET --object K --dry-run
  delete  ENV TARGET --object K --commit --token T --human-gate-approved [--confirm-env ENV]

TARGET e' il bucket logico del registro; --bucket usa un altro bucket con le stesse credenziali.

Capability spenta (`object_storage_access.enabled: false` o chiave assente): messaggio esplicito su stdout
(`capability_disabled`), exit 0, nessuna connessione e nessun import di boto3.

Scritture (upload, delete): SPENTE per default (`object_storage_access.write.enabled: false`, errore
`write_disabled`). Se accese, sempre in due passi. --dry-run legge lo stato dell'oggetto (assente, da
sovrascrivere, da cancellare), registra la scrittura pendente e stampa il token. --commit la esegue solo con
lo stesso file e lo stesso oggetto, con un token valido e non scaduto, con --human-gate-approved (il si'
esplicito di una persona dopo il dry-run: lo dichiara chi invoca, mai un subagente) e solo se l'etag
dell'oggetto non e' cambiato dal dry-run; prima salva una copia dell'oggetto precedente, dopo rilegge e
aggiunge una riga all'audit JSONL (append-only). Gli ambienti in `read_only_envs` rifiutano upload e delete
prima di connettersi, dry-run compreso; su quelli in `protected_envs` il commit richiede anche
--confirm-env e i download non vanno in raw/, wiki/, deliverables/, management/ o memory/.

TLS: verificato per default. Con `ca_file` nel registro (PEM non versionato) si usa quella catena; senza,
vale il bundle di sistema. `verify_tls: false` sull'endpoint e' ammesso solo se scritto esplicitamente e
produce un avviso (stderr e campo `warning`, `tls_verified: false`). Le richieste sono firmate (SigV4): le
chiavi non viaggiano.

Exit code: 0 ok | 1 uso/config | 2 connessione/autenticazione | 4 gate (write spento, token, TTL, conferma
ambiente, oggetto cambiato, ambiente in sola lettura, gate umano) | 5 errore S3 (oggetto assente, permesso
negato) | 6 timeout
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_CONNECT = 2
EXIT_GATE = 4
EXIT_S3 = 5
EXIT_TIMEOUT = 6

MAX_STDOUT_BYTES = 32 * 1024
MAX_PRESIGN_SECONDS = 604800          # limite SigV4: 7 giorni

DEFAULTS: dict[str, Any] = {
    "enabled": False,
    "env_file": ".env.object-storage",
    "registry": "tools/object_storage/storage-targets.yaml",
    "protected_envs": ["prod"],
    "read_only_envs": ["prod"],         # nessuna scrittura, nemmeno il dry-run
    "pending_ttl_minutes": 30,
    "state_dir": ".object-storage-state",
    "download_dir": ".object-storage-state/downloads",
    "audit_log": "deliverables/object-storage-access/audit-scritture.jsonl",
    "default_link_expires_s": 3600,
    "list_max_keys": 1000,
    "connect_timeout_s": 15,
    "read_timeout_s": 60,
    # La scrittura e' una scelta esplicita: spenta per default.
    "write": {"enabled": False},
}

# Cartelle versionate della factory: su un ambiente protetto i download non ci finiscono.
_PROTECTED_DEST_DIRS = ("raw", "wiki", "deliverables", "management", "memory")

# Parametri response-* di un link pre-firmato -> argomenti di get_object.
_RESPONSE_PARAMS = {
    "response-content-disposition": "ResponseContentDisposition",
    "response-content-type": "ResponseContentType",
    "response-content-language": "ResponseContentLanguage",
    "response-content-encoding": "ResponseContentEncoding",
    "response-cache-control": "ResponseCacheControl",
    "response-expires": "ResponseExpires",
}

_NOT_FOUND_CODES = {"404", "NoSuchKey", "NotFound", "NoSuchBucket"}
_AUTH_CODES = {"403", "AccessDenied", "InvalidAccessKeyId", "SignatureDoesNotMatch", "InvalidToken"}

TLS_OFF_WARNING = ("verify_tls: false: il certificato del server NON e' verificato (nessuna protezione da "
                   "intercettazione); preferire ca_file con la catena dell'endpoint")


class ToolError(Exception):
    def __init__(self, code: int, error: str, message: str, **extra: Any) -> None:
        super().__init__(message)
        self.code = code
        self.payload = {"ok": False, "error": error, "message": message, **extra}


# ---------------------------------------------------------------------------
# env, configurazione, registro
# ---------------------------------------------------------------------------

def parse_env_file(path: Path) -> dict[str, str]:
    """KEY=VALUE senza interpretazione shell; apici esterni rimossi, nessun taglio dei commenti in linea."""
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def load_config(root: Path) -> dict[str, Any]:
    import yaml  # import pigro: il modulo resta leggero all'import

    data = yaml.safe_load((root / "factory.config.yaml").read_text(encoding="utf-8")) or {}
    cfg = copy.deepcopy(DEFAULTS)
    user = data.get("object_storage_access") or {}
    cfg.update(user)
    cfg["write"] = {**DEFAULTS["write"], **(user.get("write") or {})}
    return cfg


def write_enabled(cfg: dict[str, Any]) -> bool:
    return (cfg.get("write") or {}).get("enabled") is True


def load_registry(root: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    import yaml

    path = root / cfg["registry"]
    if not path.is_file():
        raise ToolError(EXIT_USAGE, "registry_missing", f"registro non trovato: {cfg['registry']}",
                        hint="copiare storage-targets.example.yaml nel percorso di object_storage_access.registry")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not data.get("environments"):
        raise ToolError(EXIT_USAGE, "registry_empty", f"nessun ambiente in {cfg['registry']}")
    return data


def env_values(root: Path, cfg: dict[str, Any]) -> dict[str, str]:
    """Valori del file env; le variabili di processo valgono solo dove il file non le ha."""
    path = root / cfg["env_file"]
    values = dict(os.environ)
    if path.is_file():
        values.update(parse_env_file(path))
    return values


def _target_entry(registry: dict[str, Any], env: str, target: str) -> tuple[dict, dict, str]:
    envs = registry["environments"]
    if env not in envs:
        raise ToolError(EXIT_USAGE, "unknown_env", f"ambiente sconosciuto: {env}", available=sorted(envs))
    targets = envs[env].get("targets") or {}
    aliases = registry.get("aliases") or {}
    name = target if target in targets else aliases.get(target, target)
    if name not in targets:
        raise ToolError(EXIT_USAGE, "unknown_target", f"target sconosciuto per {env}: {target}",
                        available=sorted(targets))
    return envs[env], targets[name], name


def resolve_target(root: Path, cfg: dict[str, Any], registry: dict[str, Any], values: dict[str, str],
                   env: str, target: str, bucket_override: str | None = None) -> dict[str, Any]:
    env_entry, entry, name = _target_entry(registry, env, target)
    endpoint_name = entry.get("endpoint") or env_entry.get("endpoint") or "default"
    endpoint = (registry.get("endpoints") or {}).get(endpoint_name)
    if not endpoint:
        raise ToolError(EXIT_USAGE, "unknown_endpoint", f"endpoint non nel registro: {endpoint_name}")
    candidates = [list(pair) for pair in entry.get("credentials") or []]
    chosen = next((pair for pair in candidates if values.get(pair[0]) and values.get(pair[1])), None)
    ca_file = endpoint.get("ca_file")
    warning = None
    if ca_file:
        ca_path = root / ca_file
        if not ca_path.is_file():
            raise ToolError(EXIT_USAGE, "ca_file_missing",
                            f"ca_file dichiarato ma non trovato: {ca_file}",
                            hint="il PEM non e' versionato: copiarlo in locale oppure correggere il percorso")
        verify: bool | str = str(ca_path)
    else:
        verify = endpoint.get("verify_tls", True) is not False   # solo `false` esplicito spegne la verifica
        if verify is False:
            warning = TLS_OFF_WARNING
    resolved = {
        "env": env,
        "env_label": env_entry.get("label", env),
        "target": name,
        "bucket": bucket_override or entry["bucket"],
        "registry_bucket": entry["bucket"],
        "endpoint": endpoint["url"],
        "region": endpoint.get("region", "us-east-1"),
        "verify": verify,
        "tls_verified": verify is not False,
        "used_by": entry.get("used_by") or [],
        "credential_candidates": candidates,
        "credential_vars": chosen,
        "credentials_ready": chosen is not None,
        "protected": env in cfg["protected_envs"],
        "read_only": env in cfg["read_only_envs"],
    }
    if warning:
        resolved["warning"] = warning
    if bucket_override and bucket_override != entry["bucket"]:
        extra = f"bucket {bucket_override} fuori registro: credenziali del target {name}"
        resolved["warning"] = f"{resolved['warning']}; {extra}" if warning else extra
    return resolved


def public_target(resolved: dict[str, Any]) -> dict[str, Any]:
    """Il target senza valori sensibili (le credenziali restano nomi di variabile)."""
    out = {k: v for k, v in resolved.items() if k != "verify"}
    if isinstance(resolved.get("verify"), str):
        out["ca_file"] = resolved["verify"]
    return out


# ---------------------------------------------------------------------------
# Client S3
# ---------------------------------------------------------------------------

def _make_client(resolved: dict[str, Any], access: str, secret: str, cfg: dict[str, Any]):  # pragma: no cover
    """Unico punto che importa boto3; i test lo sostituiscono con un client finto."""
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise ToolError(EXIT_USAGE, "boto3_missing", "manca boto3: pip install -r tools/requirements.txt") from exc

    base = {
        "signature_version": "s3v4",
        "s3": {"addressing_style": "path", "payload_signing_enabled": True},
        "connect_timeout": cfg["connect_timeout_s"],
        "read_timeout": cfg["read_timeout_s"],
        "retries": {"max_attempts": 2, "mode": "standard"},
    }
    # Alcuni server S3-compatibili rifiutano i checksum aggiuntivi che boto3 >= 1.36 manda di default.
    try:
        config = Config(**base, request_checksum_calculation="when_required",
                        response_checksum_validation="when_required")
    except TypeError:  # boto3 precedente: quei checksum non li manda
        config = Config(**base)
    if resolved["verify"] is False:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return boto3.client("s3", endpoint_url=resolved["endpoint"], region_name=resolved["region"],
                        aws_access_key_id=access, aws_secret_access_key=secret,
                        verify=resolved["verify"], config=config)


def open_client(cfg: dict[str, Any], resolved: dict[str, Any], values: dict[str, str]):
    if not resolved["credentials_ready"]:
        raise ToolError(EXIT_USAGE, "credentials_missing",
                        f"credenziali assenti per {resolved['env']}/{resolved['target']} in {cfg['env_file']}",
                        expected_vars=resolved["credential_candidates"])
    access_var, secret_var = resolved["credential_vars"]
    secrets = {"access": values[access_var], "secret": values[secret_var]}
    if resolved.get("warning") and not resolved["tls_verified"]:
        print(f"object_storage_access: avviso: {TLS_OFF_WARNING}", file=sys.stderr)
    return _make_client(resolved, secrets["access"], secrets["secret"], cfg), secrets


def _scrub(text: str, secrets: dict[str, str] | None) -> str:
    for value in (secrets or {}).values():
        if value:
            text = text.replace(value, "[redatto]")
    return text


def classify(exc: Exception, secrets: dict[str, str] | None) -> ToolError:
    """Eccezione boto3/botocore -> ToolError con exit code del contratto. Per nome di classe: i test
    non dipendono da botocore."""
    name = type(exc).__name__
    message = _scrub(str(exc), secrets)
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        error = response.get("Error") or {}
        code = str(error.get("Code") or response.get("ResponseMetadata", {}).get("HTTPStatusCode") or "")
        if code in _NOT_FOUND_CODES:
            return ToolError(EXIT_S3, "not_found", message, s3_code=code)
        if code in _AUTH_CODES:
            return ToolError(EXIT_CONNECT, "auth_failed", message, s3_code=code)
        return ToolError(EXIT_S3, "s3_error", message, s3_code=code)
    if "Timeout" in name and "Connect" not in name:
        return ToolError(EXIT_TIMEOUT, "timeout", message)
    if name in ("SSLError",) or "SSL" in message and "CERTIFICATE_VERIFY_FAILED" in message:
        return ToolError(EXIT_CONNECT, "tls_error", message,
                         hint="CA non riconosciuta: indicare ca_file nel registro (PEM non versionato)")
    if name in ("EndpointConnectionError", "ConnectTimeoutError", "ConnectionClosedError",
                "ConnectionError", "ProxyConnectionError"):
        return ToolError(EXIT_CONNECT, "connection_failed", message,
                         hint="endpoint non raggiungibile: verificare rete e accesso all'ambiente")
    return ToolError(EXIT_S3, "s3_error", f"{name}: {message}")


def head(client, bucket: str, key: str, secrets: dict[str, str] | None) -> dict[str, Any] | None:
    """Metadati dell'oggetto, None se non esiste."""
    try:
        resp = client.head_object(Bucket=bucket, Key=key)
    except Exception as exc:  # noqa: BLE001 - classificata subito sotto
        err = classify(exc, secrets)
        if err.payload["error"] == "not_found":
            return None
        raise err from exc
    return {
        "etag": str(resp.get("ETag", "")).strip('"'),
        "size": resp.get("ContentLength"),
        "last_modified": _iso(resp.get("LastModified")),
        "content_type": resp.get("ContentType"),
    }


# ---------------------------------------------------------------------------
# Utilita'
# ---------------------------------------------------------------------------

def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return str(value)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_join(base: Path, relative: str) -> Path:
    """base/relative senza uscire da base (chiavi con '..' o assolute rifiutate)."""
    parts = [p for p in relative.replace("\\", "/").split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts) or not parts:
        raise ToolError(EXIT_USAGE, "unsafe_key", f"chiave non scaricabile in modo sicuro: {relative}")
    return base.joinpath(*parts)


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _operator(root: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), "config", "user.name"], capture_output=True,
                             text=True, timeout=5, check=False, encoding="utf-8", errors="replace")
        return out.stdout.strip() or os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
    except (OSError, subprocess.TimeoutExpired):
        return os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"


def emit(root: Path, cfg: dict[str, Any], payload: dict[str, Any], spill_key: str | None = None) -> None:
    """JSON su stdout; oltre 32 KiB il campo spill_key va su file in state_dir e resta il path."""
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    if spill_key and len(text.encode("utf-8")) > MAX_STDOUT_BYTES and spill_key in payload:
        state = root / cfg["state_dir"]
        state.mkdir(parents=True, exist_ok=True)
        out = state / f"{spill_key}-{_now().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}.json"
        out.write_text(json.dumps(payload[spill_key], ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        payload = {**payload, spill_key: None, f"{spill_key}_file": str(out.relative_to(root)).replace("\\", "/")}
        text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    print(text)


# ---------------------------------------------------------------------------
# Comandi di lettura
# ---------------------------------------------------------------------------

def cmd_targets(root: Path, cfg: dict[str, Any], args) -> int:
    registry = load_registry(root, cfg)
    values = env_values(root, cfg)
    rows = []
    for env, env_entry in registry["environments"].items():
        if args.env and env != args.env:
            continue
        for target in env_entry.get("targets") or {}:
            try:
                rows.append(public_target(resolve_target(root, cfg, registry, values, env, target)))
            except ToolError as err:   # un target mal configurato non nasconde gli altri
                rows.append({"env": env, "target": target, "error": err.payload["error"],
                             "message": err.payload["message"]})
    if args.env and not rows:
        raise ToolError(EXIT_USAGE, "unknown_env", f"ambiente sconosciuto: {args.env}",
                        available=sorted(registry["environments"]))
    emit(root, cfg, {"ok": True, "env_file": cfg["env_file"], "targets": rows})
    return EXIT_OK


def _context(root: Path, cfg: dict[str, Any], args):
    registry = load_registry(root, cfg)
    values = env_values(root, cfg)
    resolved = resolve_target(root, cfg, registry, values, args.env, args.target, getattr(args, "bucket", None))
    return registry, values, resolved


def cmd_check(root: Path, cfg: dict[str, Any], args) -> int:
    _, values, resolved = _context(root, cfg, args)
    client, secrets = open_client(cfg, resolved, values)
    try:
        client.head_bucket(Bucket=resolved["bucket"])
        sample = client.list_objects_v2(Bucket=resolved["bucket"], MaxKeys=1)
    except Exception as exc:  # noqa: BLE001
        raise classify(exc, secrets) from exc
    emit(root, cfg, {"ok": True, "target": public_target(resolved), "bucket_reachable": True,
                     "has_objects": bool(sample.get("KeyCount") or sample.get("Contents"))})
    return EXIT_OK


def cmd_list(root: Path, cfg: dict[str, Any], args) -> int:
    _, values, resolved = _context(root, cfg, args)
    client, secrets = open_client(cfg, resolved, values)
    limit = args.max or int(cfg["list_max_keys"])
    params: dict[str, Any] = {"Bucket": resolved["bucket"], "Prefix": args.prefix or ""}
    if args.no_recursive:
        params["Delimiter"] = "/"
    objects: list[dict[str, Any]] = []
    prefixes: list[str] = []
    truncated = False
    token = None
    try:
        while True:
            page_params = dict(params, MaxKeys=min(1000, limit - len(objects)))
            if token:
                page_params["ContinuationToken"] = token
            resp = client.list_objects_v2(**page_params)
            for item in resp.get("Contents") or []:
                objects.append({"key": item["Key"], "size": item.get("Size"),
                                "last_modified": _iso(item.get("LastModified")),
                                "etag": str(item.get("ETag", "")).strip('"')})
            prefixes.extend(p["Prefix"] for p in resp.get("CommonPrefixes") or [])
            token = resp.get("NextContinuationToken")
            if not resp.get("IsTruncated") or not token:
                break
            if len(objects) >= limit:
                truncated = True
                break
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise classify(exc, secrets) from exc
    payload = {"ok": True, "target": public_target(resolved), "prefix": args.prefix or "",
               "recursive": not args.no_recursive, "count": len(objects), "truncated": truncated,
               "total_size": sum(o["size"] or 0 for o in objects), "prefixes": prefixes, "objects": objects}
    emit(root, cfg, payload, spill_key="objects")
    return EXIT_OK


def cmd_stat(root: Path, cfg: dict[str, Any], args) -> int:
    _, values, resolved = _context(root, cfg, args)
    client, secrets = open_client(cfg, resolved, values)
    meta = head(client, resolved["bucket"], args.object, secrets)
    if meta is None:
        raise ToolError(EXIT_S3, "not_found", f"oggetto assente: {resolved['bucket']}/{args.object}")
    emit(root, cfg, {"ok": True, "target": public_target(resolved), "object": args.object, **meta})
    return EXIT_OK


def _download_one(client, bucket: str, key: str, dest: Path, secrets: dict[str, str]) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".objstore-", dir=str(dest.parent))
    os.close(fd)
    try:
        try:
            resp = client.get_object(Bucket=bucket, Key=key)
            body = resp["Body"].read()
        except Exception as exc:  # noqa: BLE001
            raise classify(exc, secrets) from exc
        Path(tmp).write_bytes(body)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return {"key": key, "path": str(dest), "size": len(body),
            "etag": str(resp.get("ETag", "")).strip('"'), "sha256": hashlib.sha256(body).hexdigest()}


def _check_dest(root: Path, resolved: dict[str, Any], dest: Path) -> None:
    if not resolved["protected"]:
        return
    for name in _PROTECTED_DEST_DIRS:
        if _is_under(dest, root / name):
            raise ToolError(EXIT_GATE, "protected_dest",
                            f"{resolved['env']} e' protetto: niente download in {name}/ (cartella versionata)")


def cmd_download(root: Path, cfg: dict[str, Any], args) -> int:
    _, values, resolved = _context(root, cfg, args)
    key = args.object
    base_default = root / cfg["download_dir"] / resolved["env"] / resolved["target"]
    folder = key.endswith("/")
    if args.dest:
        dest_arg = Path(args.dest)
        dest_root = dest_arg if dest_arg.is_absolute() else Path.cwd() / dest_arg
    else:
        dest_root = base_default
    _check_dest(root, resolved, dest_root)
    client, secrets = open_client(cfg, resolved, values)
    files = []
    if folder:
        try:
            page_token = None
            keys: list[str] = []
            while True:
                params = {"Bucket": resolved["bucket"], "Prefix": key}
                if page_token:
                    params["ContinuationToken"] = page_token
                resp = client.list_objects_v2(**params)
                keys.extend(item["Key"] for item in resp.get("Contents") or [] if not item["Key"].endswith("/"))
                page_token = resp.get("NextContinuationToken")
                if not resp.get("IsTruncated") or not page_token:
                    break
        except Exception as exc:  # noqa: BLE001
            raise classify(exc, secrets) from exc
        if not keys:
            raise ToolError(EXIT_S3, "not_found", f"nessun oggetto sotto {resolved['bucket']}/{key}")
        for item_key in keys:
            files.append(_download_one(client, resolved["bucket"], item_key,
                                       _safe_join(dest_root, item_key[len(key):]), secrets))
    else:
        if args.dest and (dest_root.is_dir() or str(args.dest).endswith(("/", "\\"))):
            dest = _safe_join(dest_root, key.rsplit("/", 1)[-1])
        elif args.dest:
            dest = dest_root
        else:
            dest = _safe_join(dest_root, key)
        files.append(_download_one(client, resolved["bucket"], key, dest, secrets))
    for item in files:
        try:
            item["path"] = str(Path(item["path"]).resolve().relative_to(root.resolve())).replace("\\", "/")
        except ValueError:
            pass  # fuori dalla factory: resta il path assoluto
    emit(root, cfg, {"ok": True, "target": public_target(resolved), "object": key, "count": len(files),
                     "files": files}, spill_key="files")
    return EXIT_OK


# ---------------------------------------------------------------------------
# Link pre-firmati
# ---------------------------------------------------------------------------

def _expires(cfg: dict[str, Any], value: int | None) -> int:
    seconds = int(value or cfg["default_link_expires_s"])
    if not 1 <= seconds <= MAX_PRESIGN_SECONDS:
        raise ToolError(EXIT_USAGE, "bad_expires", f"--expires fra 1 e {MAX_PRESIGN_SECONDS} secondi (limite SigV4)")
    return seconds


def _presign(client, secrets, bucket: str, key: str, expires: int, extra: dict[str, Any] | None = None) -> str:
    params = {"Bucket": bucket, "Key": key, **(extra or {})}
    try:
        return client.generate_presigned_url("get_object", Params=params, ExpiresIn=expires)
    except Exception as exc:  # noqa: BLE001
        raise classify(exc, secrets) from exc


def cmd_presign(root: Path, cfg: dict[str, Any], args) -> int:
    expires = _expires(cfg, args.expires)
    _, values, resolved = _context(root, cfg, args)
    client, secrets = open_client(cfg, resolved, values)
    url = _presign(client, secrets, resolved["bucket"], args.object, expires)
    emit(root, cfg, {"ok": True, "target": public_target(resolved), "object": args.object,
                     "expires_at": _iso(_now() + dt.timedelta(seconds=expires)), "url": url,
                     "protected": resolved["protected"]})
    return EXIT_OK


def parse_presigned(url: str) -> dict[str, Any]:
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        raise ToolError(EXIT_USAGE, "bad_url", "URL non valido")
    query = {k: v[0] for k, v in parse_qs(parts.query, keep_blank_values=True).items()}
    path = unquote(parts.path).lstrip("/")
    bucket, _, key = path.partition("/")
    info: dict[str, Any] = {"host": parts.netloc, "bucket": bucket, "key": key, "query": query,
                            "presigned": "X-Amz-Signature" in query, "expires_at": None, "expired": None}
    if "X-Amz-Date" in query and "X-Amz-Expires" in query:
        try:
            signed = dt.datetime.strptime(query["X-Amz-Date"], "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
            expires_at = signed + dt.timedelta(seconds=int(query["X-Amz-Expires"]))
            info["expires_at"] = _iso(expires_at)
            info["expired"] = expires_at <= _now()
        except ValueError:
            info["expired"] = True  # data illeggibile: il link non e' utilizzabile, va rinnovato
    return info


def find_by_bucket(root: Path, cfg: dict[str, Any], registry: dict[str, Any], values: dict[str, str],
                   bucket: str) -> dict[str, Any] | None:
    for env, env_entry in registry["environments"].items():
        for target, entry in (env_entry.get("targets") or {}).items():
            if entry.get("bucket") == bucket:
                return resolve_target(root, cfg, registry, values, env, target)
    return None


def cmd_renew_link(root: Path, cfg: dict[str, Any], args) -> int:
    expires = _expires(cfg, args.expires)
    info = parse_presigned(args.url)
    registry = load_registry(root, cfg)
    values = env_values(root, cfg)
    resolved = find_by_bucket(root, cfg, registry, values, info["bucket"])
    if resolved is None:
        raise ToolError(EXIT_USAGE, "bucket_not_in_registry", f"bucket non nel registro: {info['bucket']}",
                        bucket=info["bucket"])
    client, secrets = open_client(cfg, resolved, values)
    extra = {param: info["query"][name] for name, param in _RESPONSE_PARAMS.items() if name in info["query"]}
    url = _presign(client, secrets, info["bucket"], info["key"], expires, extra)
    emit(root, cfg, {"ok": True, "env": resolved["env"], "target": resolved["target"], "bucket": info["bucket"],
                     "key": info["key"], "protected": resolved["protected"],
                     "previous_expires_at": info["expires_at"], "was_expired": info["expired"],
                     "expires_at": _iso(_now() + dt.timedelta(seconds=expires)), "url": url})
    return EXIT_OK


# ---------------------------------------------------------------------------
# Scritture: dry-run, gate, commit
# ---------------------------------------------------------------------------

def _pending_path(root: Path, cfg: dict[str, Any], token: str) -> Path:
    if not token.isalnum():
        raise ToolError(EXIT_GATE, "bad_token", "token non valido")
    return root / cfg["state_dir"] / "pending" / f"{token}.json"


def _write_request(args, resolved: dict[str, Any]) -> dict[str, Any]:
    request: dict[str, Any] = {"action": args.command, "env": resolved["env"], "target": resolved["target"],
                               "bucket": resolved["bucket"]}
    if args.command == "upload":
        path = Path(args.file)
        if not path.is_file():
            raise ToolError(EXIT_USAGE, "file_missing", f"file non trovato: {args.file}")
        request.update({"file": str(path.resolve()), "object": args.object or path.name,
                        "size": path.stat().st_size, "sha256": _sha256_file(path),
                        "content_type": args.content_type})
    else:
        if args.object.endswith("/"):
            raise ToolError(EXIT_USAGE, "folder_delete", "delete di una cartella non ammesso: un oggetto alla volta")
        request["object"] = args.object
    return request


def cmd_write(root: Path, cfg: dict[str, Any], args) -> int:
    if not write_enabled(cfg):
        raise ToolError(EXIT_GATE, "write_disabled",
                        "la scrittura e' spenta: object_storage_access.write.enabled e' false (default). "
                        "Accenderla e' una scelta esplicita del maintainer; anche accesa, --commit richiede "
                        "token e gate umano")
    if args.env in cfg["read_only_envs"]:
        raise ToolError(EXIT_GATE, "read_only_env",
                        f"{args.env} e' in sola lettura: {args.command} rifiutato, dry-run compreso")
    if args.dry_run == args.commit:
        raise ToolError(EXIT_USAGE, "mode_required", "serve esattamente uno fra --dry-run e --commit --token")
    _, values, resolved = _context(root, cfg, args)
    request = _write_request(args, resolved)
    if args.dry_run:
        return _write_dry_run(root, cfg, values, resolved, request)
    return _write_commit(root, cfg, values, resolved, request, args)


def _write_dry_run(root, cfg, values, resolved, request) -> int:
    client, secrets = open_client(cfg, resolved, values)
    current = head(client, resolved["bucket"], request["object"], secrets)
    if request["action"] == "delete" and current is None:
        raise ToolError(EXIT_S3, "not_found", f"oggetto assente: {resolved['bucket']}/{request['object']}")
    effect = ("delete" if request["action"] == "delete" else "overwrite" if current else "create")
    token = uuid.uuid4().hex[:16]
    expires = _now() + dt.timedelta(minutes=int(cfg["pending_ttl_minutes"]))
    pending = {**request, "token": token, "effect": effect, "current": current,
               "created_at": _iso(_now()), "expires_at": _iso(expires)}
    path = _pending_path(root, cfg, token)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pending, indent=2), encoding="utf-8")
    emit(root, cfg, {"ok": True, "mode": "dry-run", "target": public_target(resolved), **pending,
                     "confirm_env_required": resolved["protected"],
                     "commit_requires": {"token": token, "human_gate_approved": True,
                                         "confirm_env": resolved["env"] if resolved["protected"] else None}})
    return EXIT_OK


def _write_commit(root, cfg, values, resolved, request, args) -> int:
    if not args.token:
        raise ToolError(EXIT_USAGE, "token_required", "--commit richiede --token dal dry-run")
    path = _pending_path(root, cfg, args.token)
    if not path.is_file():
        raise ToolError(EXIT_GATE, "token_unknown", "token sconosciuto o gia' usato: rifare il dry-run")
    pending = json.loads(path.read_text(encoding="utf-8"))
    if dt.datetime.fromisoformat(pending["expires_at"].replace("Z", "+00:00")) < _now():
        path.unlink()
        raise ToolError(EXIT_GATE, "token_expired", "dry-run scaduto: rifarlo")
    for field in ("action", "env", "target", "bucket", "object", "sha256", "size"):
        if pending.get(field) != request.get(field):
            raise ToolError(EXIT_GATE, "request_mismatch",
                            f"{field} diverso dal dry-run: il token vale solo per la stessa operazione",
                            field=field, dry_run=pending.get(field), commit=request.get(field))
    if not args.human_gate_approved:
        raise ToolError(EXIT_GATE, "human_gate_required",
                        "il commit richiede il si' esplicito di una persona dopo il dry-run: --human-gate-approved")
    if resolved["protected"] and args.confirm_env != resolved["env"]:
        raise ToolError(EXIT_GATE, "confirm_env_required", f"ambiente protetto: serve --confirm-env {resolved['env']}")
    client, secrets = open_client(cfg, resolved, values)
    bucket, key = resolved["bucket"], request["object"]
    current = head(client, bucket, key, secrets)
    before = (pending.get("current") or {}).get("etag")
    if (current or {}).get("etag") != before:
        raise ToolError(EXIT_GATE, "object_changed", "l'oggetto e' cambiato dopo il dry-run: rifare il dry-run",
                        dry_run_etag=before, current_etag=(current or {}).get("etag"))
    backup = None
    if current is not None:
        stamp = _now().strftime("%Y%m%dT%H%M%SZ")
        backup_path = _safe_join(root / cfg["state_dir"] / "backups" / resolved["env"] / resolved["target"] / stamp, key)
        saved = _download_one(client, bucket, key, backup_path, secrets)
        if saved["etag"] != before:
            raise ToolError(EXIT_GATE, "object_changed", "l'oggetto e' cambiato durante la copia di sicurezza")
        backup = str(Path(saved["path"]).resolve().relative_to(root.resolve())).replace("\\", "/")
    try:
        if request["action"] == "upload":
            body = Path(request["file"]).read_bytes()
            if hashlib.sha256(body).hexdigest() != request["sha256"]:
                raise ToolError(EXIT_GATE, "request_mismatch", "il file e' cambiato durante il commit")
            content_type = (request.get("content_type") or (current or {}).get("content_type")
                            or mimetypes.guess_type(key)[0] or "application/octet-stream")
            client.put_object(Bucket=bucket, Key=key, Body=body, ContentType=content_type)
        else:
            client.delete_object(Bucket=bucket, Key=key)
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise classify(exc, secrets) from exc
    path.unlink()  # token monouso: consumato anche se la verifica sotto fallisce
    after = head(client, bucket, key, secrets)
    if request["action"] == "upload":
        verified = after is not None and after["size"] == request["size"]
    else:
        verified = after is None
    record = {"ts": _iso(_now()), "operator": _operator(root), "env": resolved["env"],
              "target": resolved["target"], "bucket": bucket, "object": key, "action": request["action"],
              "effect": pending["effect"], "previous_etag": before, "new_etag": (after or {}).get("etag"),
              "size": request.get("size"), "sha256": request.get("sha256"), "backup": backup,
              "human_gate_approved": True, "verified": verified}
    audit = root / cfg["audit_log"]
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    payload = {"ok": verified, "mode": "commit", "target": public_target(resolved), **record,
               "audit_log": cfg["audit_log"]}
    if not verified:
        payload.update(error="verify_failed", message="scrittura eseguita ma la rilettura non corrisponde")
    emit(root, cfg, payload)
    return EXIT_OK if verified else EXIT_S3


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Accesso agli oggetti dei bucket S3-compatibili")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]),
                        help="root della factory (default: dedotta dal path dello script)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("targets", help="registro e stato delle credenziali")
    p.add_argument("--env")

    def env_target(p: argparse.ArgumentParser) -> None:
        p.add_argument("env", help="ambiente del registro")
        p.add_argument("target", help="bucket logico del registro")
        p.add_argument("--bucket", help="altro bucket con le credenziali del target")

    p = sub.add_parser("check", help="credenziali e raggiungibilita' del bucket")
    env_target(p)

    p = sub.add_parser("list", help="elenca gli oggetti")
    env_target(p)
    p.add_argument("--prefix", default="")
    p.add_argument("--no-recursive", action="store_true")
    p.add_argument("--max", type=int)

    p = sub.add_parser("stat", help="metadati di un oggetto")
    env_target(p)
    p.add_argument("--object", required=True)

    p = sub.add_parser("download", help="scarica un oggetto, o una cartella se termina con /")
    env_target(p)
    p.add_argument("--object", required=True)
    p.add_argument("--dest")

    p = sub.add_parser("presign", help="link pre-firmato di lettura")
    env_target(p)
    p.add_argument("--object", required=True)
    p.add_argument("--expires", type=int)

    for name in ("upload", "delete"):
        p = sub.add_parser(name, help=f"{name} con dry-run e commit")
        env_target(p)
        if name == "upload":
            p.add_argument("--file", required=True)
            p.add_argument("--object")
            p.add_argument("--content-type")
        else:
            p.add_argument("--object", required=True)
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--commit", action="store_true")
        p.add_argument("--token")
        p.add_argument("--confirm-env")
        p.add_argument("--human-gate-approved", action="store_true",
                       help="il si' esplicito di una persona dopo il dry-run (mai passato da un subagente)")

    p = sub.add_parser("renew-link", help="nuovo link pre-firmato per l'oggetto di un URL")
    p.add_argument("--url", required=True)
    p.add_argument("--expires", type=int)
    return parser


COMMANDS = {
    "targets": cmd_targets, "check": cmd_check, "list": cmd_list, "stat": cmd_stat,
    "download": cmd_download, "presign": cmd_presign, "upload": cmd_write, "delete": cmd_write,
    "renew-link": cmd_renew_link,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    try:
        cfg = load_config(root)
        if not cfg.get("enabled"):
            print(json.dumps({"ok": True, "enabled": False, "error": "capability_disabled",
                              "message": "object_storage_access disabilitata: imposta "
                                         "object_storage_access.enabled: true in factory.config.yaml. "
                                         "Nessuna operazione eseguita."}, ensure_ascii=False, indent=2))
            return EXIT_OK
        return COMMANDS[args.command](root, cfg, args)
    except ToolError as err:
        print(json.dumps(err.payload, ensure_ascii=False, indent=2, default=str))
        print(f"object_storage_access: {err.payload['error']}: {err.payload['message']}", file=sys.stderr)
        return err.code


if __name__ == "__main__":
    sys.exit(main())
