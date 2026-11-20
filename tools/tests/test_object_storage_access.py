"""
Test di tools/object_storage/object_storage_access.py.

Nessuna rete e nessun boto3: `_make_client` e' sostituita da un client S3 finto in memoria che
registra le chiamate. La factory di prova (config, registro, file env) vive in tmp_path.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "tools" / "object_storage" / "object_storage_access.py"
_EXAMPLE = _REPO_ROOT / "tools" / "object_storage" / "storage-targets.example.yaml"

_spec = importlib.util.spec_from_file_location("object_storage_access", _SCRIPT)
osa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(osa)

REGISTRY = """
version: 1
endpoints:
  default: {url: "https://s3.example.invalid", region: eu-test-1}
  lab: {url: "https://s3-lab.example.invalid", verify_tls: false}
  pinned: {url: "https://s3-pinned.example.invalid", ca_file: certs/ca.pem}
  missingca: {url: "https://s3-x.example.invalid", ca_file: certs/nope.pem}
environments:
  test:
    label: TEST
    targets:
      docs:
        bucket: bucket-test
        credentials: [[T_ACCESS, T_SECRET]]
      labdocs:
        bucket: bucket-lab
        endpoint: lab
        credentials: [[T_ACCESS, T_SECRET]]
      pinned:
        bucket: bucket-pinned
        endpoint: pinned
        credentials: [[T_ACCESS, T_SECRET]]
      brokenca:
        bucket: bucket-broken
        endpoint: missingca
        credentials: [[T_ACCESS, T_SECRET]]
      nocreds:
        bucket: bucket-nocreds
        credentials: [[NOPE_ACCESS, NOPE_SECRET]]
  staging:
    targets:
      docs:
        bucket: bucket-staging
        credentials: [[T_ACCESS, T_SECRET]]
  prod:
    targets:
      docs:
        bucket: bucket-prod
        credentials: [[T_ACCESS, T_SECRET]]
aliases:
  documents: docs
"""

# Valori finti composti a runtime: nessun segreto nel sorgente.
_ACCESS = "".join(["AK", "TESTACCESS"])
_SECRET = "".join(["sk", "-test-secret"])


class FakeS3Error(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class FakeClient:
    def __init__(self, objects: dict | None = None) -> None:
        self.objects = objects if objects is not None else {}   # (bucket, key) -> bytes
        self.etags: dict = {}
        self.calls: list = []

    def _etag(self, bucket, key):
        return self.etags.get((bucket, key)) or hashlib.md5(self.objects[(bucket, key)]).hexdigest()

    def head_bucket(self, Bucket):
        self.calls.append(("head_bucket", Bucket))

    def head_object(self, Bucket, Key):
        self.calls.append(("head_object", Bucket, Key))
        if (Bucket, Key) not in self.objects:
            raise FakeS3Error("404")
        body = self.objects[(Bucket, Key)]
        return {"ETag": f'"{self._etag(Bucket, Key)}"', "ContentLength": len(body),
                "LastModified": dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc), "ContentType": "text/plain"}

    def get_object(self, Bucket, Key):
        self.calls.append(("get_object", Bucket, Key))
        if (Bucket, Key) not in self.objects:
            raise FakeS3Error("NoSuchKey")
        body = self.objects[(Bucket, Key)]

        class _Body:
            def read(self_inner):
                return body
        return {"Body": _Body(), "ETag": f'"{self._etag(Bucket, Key)}"'}

    def list_objects_v2(self, Bucket, Prefix="", MaxKeys=1000, Delimiter=None, ContinuationToken=None):
        self.calls.append(("list_objects_v2", Bucket, Prefix))
        keys = sorted(k for (b, k) in self.objects if b == Bucket and k.startswith(Prefix))
        contents = [{"Key": k, "Size": len(self.objects[(Bucket, k)]),
                     "LastModified": dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
                     "ETag": f'"{self._etag(Bucket, k)}"'} for k in keys]
        return {"Contents": contents, "KeyCount": len(contents), "IsTruncated": False}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.calls.append(("put_object", Bucket, Key))
        self.objects[(Bucket, Key)] = Body
        self.etags.pop((Bucket, Key), None)

    def delete_object(self, Bucket, Key):
        self.calls.append(("delete_object", Bucket, Key))
        self.objects.pop((Bucket, Key), None)

    def generate_presigned_url(self, op, Params, ExpiresIn):
        self.calls.append(("presign", Params["Bucket"], Params["Key"], ExpiresIn))
        return (f"https://s3.example.invalid/{Params['Bucket']}/{Params['Key']}"
                f"?X-Amz-Signature=abc&X-Amz-Expires={ExpiresIn}")

    def written(self):
        return [c for c in self.calls if c[0] in ("put_object", "delete_object")]


def _config(enabled=True, extra=""):
    return f"object_storage_access:\n  enabled: {str(enabled).lower()}\n{extra}"


@pytest.fixture
def factory(tmp_path):
    (tmp_path / "factory.config.yaml").write_text(
        _config(extra="  write:\n    enabled: true\n"), encoding="utf-8")
    (tmp_path / "tools" / "object_storage").mkdir(parents=True)
    (tmp_path / "tools" / "object_storage" / "storage-targets.yaml").write_text(REGISTRY, encoding="utf-8")
    (tmp_path / "certs").mkdir()
    (tmp_path / "certs" / "ca.pem").write_text("pem", encoding="utf-8")
    (tmp_path / ".env.object-storage").write_text(
        f"T_ACCESS={_ACCESS}\nT_SECRET={_SECRET}\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient({("bucket-test", "a/one.txt"): b"uno", ("bucket-test", "a/two.txt"): b"due",
                         ("bucket-test", "b/three.txt"): b"tre", ("bucket-prod", "p.txt"): b"prod"})
    seen = {}

    def make(resolved, access, secret, cfg):
        seen["resolved"], seen["access"], seen["secret"] = resolved, access, secret
        return client

    monkeypatch.setattr(osa, "_make_client", make)
    client.seen = seen
    return client


def run(factory, capsys, *argv):
    code = osa.main(["--root", str(factory), *argv])
    out, err = capsys.readouterr()
    payload = json.loads(out) if out.strip() else None
    return code, payload, err


def set_cfg(factory, text):
    (factory / "factory.config.yaml").write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Capability spenta, registro d'esempio
# ---------------------------------------------------------------------------

def test_disabled_capability_explicit_message_exit_0(factory, fake, capsys):
    set_cfg(factory, _config(enabled=False))
    code, out, _ = run(factory, capsys, "list", "test", "docs")
    assert code == 0 and out["enabled"] is False and out["error"] == "capability_disabled"
    assert "object_storage_access" in out["message"] and not fake.calls


def test_missing_config_key_is_disabled(factory, fake, capsys):
    set_cfg(factory, "other_key: 1\n")
    code, out, _ = run(factory, capsys, "targets")
    assert code == 0 and out["enabled"] is False and not fake.calls


def test_disabled_does_not_need_registry_or_boto3(tmp_path, capsys):
    (tmp_path / "factory.config.yaml").write_text("x: 1\n", encoding="utf-8")
    code, out, _ = run(tmp_path, capsys, "list", "test", "docs")
    assert code == 0 and out["enabled"] is False
    assert "boto3" not in sys.modules


def test_example_registry_loads_and_is_fictitious(tmp_path, capsys):
    import yaml
    (tmp_path / "factory.config.yaml").write_text(_config(), encoding="utf-8")
    (tmp_path / "tools" / "object_storage").mkdir(parents=True)
    (tmp_path / "tools" / "object_storage" / "storage-targets.yaml").write_text(
        _EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    code, out, _ = run(tmp_path, capsys, "targets")
    assert code == 0 and all(t["error"] == "ca_file_missing" for t in out["targets"])   # PEM d'esempio assente: niente deroga silenziosa
    data = yaml.safe_load(_EXAMPLE.read_text(encoding="utf-8"))
    assert data["environments"] and all(e["url"].endswith(".invalid") for e in data["endpoints"].values())
    assert "bucket-di-esempio-test" in _EXAMPLE.read_text(encoding="utf-8")


def test_example_registry_targets_with_ca_present(tmp_path, capsys):
    (tmp_path / "factory.config.yaml").write_text(_config(), encoding="utf-8")
    (tmp_path / "tools" / "object_storage" / "certs").mkdir(parents=True)
    (tmp_path / "tools" / "object_storage" / "certs" / "example-ca.pem").write_text("pem", encoding="utf-8")
    (tmp_path / "tools" / "object_storage" / "storage-targets.yaml").write_text(
        _EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    code, out, _ = run(tmp_path, capsys, "targets", "--env", "test")
    assert code == 0 and {t["target"] for t in out["targets"]} == {"documents", "exports"}
    assert all(t["credentials_ready"] is False for t in out["targets"])


def test_registry_missing(factory, fake, capsys):
    (factory / "tools" / "object_storage" / "storage-targets.yaml").unlink()
    code, out, _ = run(factory, capsys, "list", "test", "docs")
    assert code == 1 and out["error"] == "registry_missing"


# ---------------------------------------------------------------------------
# Lettura
# ---------------------------------------------------------------------------

def test_targets_hides_secrets(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "targets", "--env", "test")
    text = json.dumps(out)
    assert code == 0 and _SECRET not in text and _ACCESS not in text
    broken = next(t for t in out["targets"] if t["target"] == "brokenca")
    assert broken["error"] == "ca_file_missing"
    docs = next(t for t in out["targets"] if t["target"] == "docs")
    assert docs["credentials_ready"] is True and docs["credential_vars"] == ["T_ACCESS", "T_SECRET"]


def test_list_stat(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "list", "test", "docs", "--prefix", "a/")
    assert code == 0 and out["count"] == 2 and [o["key"] for o in out["objects"]] == ["a/one.txt", "a/two.txt"]
    assert out["total_size"] == 6
    code, out, _ = run(factory, capsys, "stat", "test", "docs", "--object", "a/one.txt")
    assert code == 0 and out["size"] == 3 and out["etag"] == hashlib.md5(b"uno").hexdigest()


def test_alias_resolves_and_stat_missing(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "stat", "test", "documents", "--object", "nope")
    assert code == 5 and out["error"] == "not_found"


def test_unknown_env_and_target(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "list", "nowhere", "docs")
    assert code == 1 and out["error"] == "unknown_env"
    code, out, _ = run(factory, capsys, "list", "test", "nowhere")
    assert code == 1 and out["error"] == "unknown_target"


def test_credentials_missing(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "list", "test", "nocreds")
    assert code == 1 and out["error"] == "credentials_missing"


def test_download_file_and_folder(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "download", "test", "docs", "--object", "a/one.txt")
    assert code == 0 and out["files"][0]["sha256"] == hashlib.sha256(b"uno").hexdigest()
    saved = factory / out["files"][0]["path"]
    assert saved.read_bytes() == b"uno" and ".object-storage-state/downloads/test/docs" in out["files"][0]["path"]
    code, out, _ = run(factory, capsys, "download", "test", "docs", "--object", "a/")
    assert code == 0 and out["count"] == 2


def test_download_missing_object(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "download", "test", "docs", "--object", "zzz")
    assert code == 5 and out["error"] == "not_found"


def test_download_protected_env_refuses_versioned_dirs(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "download", "prod", "docs", "--object", "p.txt",
                       "--dest", str(factory / "wiki" / "p.txt"))
    assert code == 4 and out["error"] == "protected_dest"


def test_download_rejects_unsafe_key(factory, fake, capsys):
    fake.objects[("bucket-test", "../evil")] = b"x"
    code, out, _ = run(factory, capsys, "download", "test", "docs", "--object", "../evil")
    assert code == 1 and out["error"] == "unsafe_key"


def test_presign_and_expires_bounds(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "presign", "test", "docs", "--object", "a/one.txt", "--expires", "120")
    assert code == 0 and "X-Amz-Signature" in out["url"] and ("presign", "bucket-test", "a/one.txt", 120) in fake.calls
    code, out, _ = run(factory, capsys, "presign", "test", "docs", "--object", "a/one.txt")
    assert code == 0 and ("presign", "bucket-test", "a/one.txt", 3600) in fake.calls
    code, out, _ = run(factory, capsys, "presign", "test", "docs", "--object", "k", "--expires", "999999999")
    assert code == 1 and out["error"] == "bad_expires"


def test_renew_link_by_bucket(factory, fake, capsys):
    url = ("https://s3.example.invalid/bucket-test/a/one.txt?X-Amz-Date=20200101T000000Z"
           "&X-Amz-Expires=60&X-Amz-Signature=old")
    code, out, _ = run(factory, capsys, "renew-link", "--url", url)
    assert code == 0 and out["was_expired"] is True and out["env"] == "test" and out["key"] == "a/one.txt"
    code, out, _ = run(factory, capsys, "renew-link", "--url", "https://s3.example.invalid/unknown-bucket/k?X-Amz-Signature=a")
    assert code == 1 and out["error"] == "bucket_not_in_registry"


def test_secrets_are_scrubbed_from_errors(factory, fake, capsys):
    def boom(**kw):
        raise RuntimeError(f"fail with {_SECRET}")
    fake.list_objects_v2 = boom
    code, out, err = run(factory, capsys, "list", "test", "docs")
    assert code == 5 and _SECRET not in json.dumps(out) and "[redatto]" in out["message"]


# ---------------------------------------------------------------------------
# TLS
# ---------------------------------------------------------------------------

def test_tls_verified_by_default(factory, fake, capsys):
    code, out, err = run(factory, capsys, "list", "test", "docs")
    assert code == 0 and out["target"]["tls_verified"] is True and "warning" not in out["target"]
    assert fake.seen["resolved"]["verify"] is True and "avviso" not in err


def test_tls_ca_file_used(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "list", "test", "pinned")
    assert code == 0 and fake.seen["resolved"]["verify"] == str(factory / "certs" / "ca.pem")
    assert out["target"]["tls_verified"] is True


def test_tls_ca_file_declared_but_missing_is_an_error(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "list", "test", "brokenca")
    assert code == 1 and out["error"] == "ca_file_missing" and not fake.calls


def test_verify_tls_false_warns(factory, fake, capsys):
    code, out, err = run(factory, capsys, "list", "test", "labdocs")
    assert code == 0 and fake.seen["resolved"]["verify"] is False
    assert out["target"]["tls_verified"] is False and "NON e' verificato" in out["target"]["warning"]
    assert "avviso" in err


# ---------------------------------------------------------------------------
# Scritture
# ---------------------------------------------------------------------------

def _upload_file(factory, content=b"nuovo"):
    f = factory / "payload.txt"
    f.write_bytes(content)
    return str(f)


def _dry(factory, capsys, env="test", obj="a/one.txt", content=b"nuovo"):
    code, out, _ = run(factory, capsys, "upload", env, "docs", "--file", _upload_file(factory, content),
                       "--object", obj, "--dry-run")
    assert code == 0, out
    return out


def _commit(factory, capsys, token, env="test", obj="a/one.txt", gate=True, extra=()):
    argv = ["upload", env, "docs", "--file", str(factory / "payload.txt"), "--object", obj,
            "--commit", "--token", token, *extra]
    if gate:
        argv.append("--human-gate-approved")
    return run(factory, capsys, *argv)


def test_write_disabled_by_default(factory, fake, capsys):
    assert osa.DEFAULTS["write"] == {"enabled": False}
    set_cfg(factory, _config())
    code, out, _ = run(factory, capsys, "delete", "test", "docs", "--object", "a/one.txt", "--dry-run")
    assert code == 4 and out["error"] == "write_disabled" and not fake.calls


def test_write_enabled_must_be_boolean_true(factory, fake, capsys):
    set_cfg(factory, _config(extra='  write:\n    enabled: "yes"\n'))
    code, out, _ = run(factory, capsys, "delete", "test", "docs", "--object", "a/one.txt", "--dry-run")
    assert code == 4 and out["error"] == "write_disabled"


def test_dry_run_writes_nothing_and_returns_token(factory, fake, capsys):
    out = _dry(factory, capsys)
    assert out["mode"] == "dry-run" and out["effect"] == "overwrite" and out["token"]
    assert not fake.written()
    assert (factory / ".object-storage-state" / "pending" / f"{out['token']}.json").is_file()
    out = _dry(factory, capsys, obj="new.txt")
    assert out["effect"] == "create"


def test_commit_overwrite_with_backup_and_audit(factory, fake, capsys):
    dry = _dry(factory, capsys)
    code, out, _ = _commit(factory, capsys, dry["token"])
    assert code == 0 and out["ok"] is True and out["verified"] is True and out["effect"] == "overwrite"
    assert fake.objects[("bucket-test", "a/one.txt")] == b"nuovo"
    backup = factory / out["backup"]
    assert backup.read_bytes() == b"uno"
    lines = (factory / "deliverables" / "object-storage-access" / "audit-scritture.jsonl").read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[0])
    assert len(lines) == 1 and rec["action"] == "upload" and rec["backup"] == out["backup"]
    assert rec["human_gate_approved"] is True and rec["previous_etag"] != rec["new_etag"]
    # token monouso
    code, out, _ = _commit(factory, capsys, dry["token"])
    assert code == 4 and out["error"] == "token_unknown"


def test_audit_is_append_only(factory, fake, capsys):
    for obj in ("n1.txt", "n2.txt"):
        dry = _dry(factory, capsys, obj=obj)
        assert _commit(factory, capsys, dry["token"], obj=obj)[0] == 0
    lines = (factory / "deliverables" / "object-storage-access" / "audit-scritture.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(l)["object"] for l in lines] == ["n1.txt", "n2.txt"]
    assert json.loads(lines[0])["backup"] is None            # creazione: niente da salvare


def test_commit_delete_with_backup(factory, fake, capsys):
    code, dry, _ = run(factory, capsys, "delete", "test", "docs", "--object", "a/two.txt", "--dry-run")
    assert code == 0 and dry["effect"] == "delete"
    code, out, _ = run(factory, capsys, "delete", "test", "docs", "--object", "a/two.txt", "--commit",
                       "--token", dry["token"], "--human-gate-approved")
    assert code == 0 and ("bucket-test", "a/two.txt") not in fake.objects
    assert (factory / out["backup"]).read_bytes() == b"due"


def test_delete_missing_object_and_folder_refused(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "delete", "test", "docs", "--object", "zzz", "--dry-run")
    assert code == 5 and out["error"] == "not_found"
    code, out, _ = run(factory, capsys, "delete", "test", "docs", "--object", "a/", "--dry-run")
    assert code == 1 and out["error"] == "folder_delete"


def test_commit_without_token(factory, fake, capsys):
    _dry(factory, capsys)
    code, out, _ = run(factory, capsys, "upload", "test", "docs", "--file", str(factory / "payload.txt"),
                       "--object", "a/one.txt", "--commit", "--human-gate-approved")
    assert code == 1 and out["error"] == "token_required" and not fake.written()


def test_commit_with_unknown_token(factory, fake, capsys):
    _dry(factory, capsys)
    code, out, _ = _commit(factory, capsys, "deadbeef")
    assert code == 4 and out["error"] == "token_unknown" and not fake.written()


def test_commit_with_expired_token(factory, fake, capsys):
    dry = _dry(factory, capsys)
    pending = factory / ".object-storage-state" / "pending" / f"{dry['token']}.json"
    data = json.loads(pending.read_text(encoding="utf-8"))
    data["expires_at"] = "2020-01-01T00:00:00Z"
    pending.write_text(json.dumps(data), encoding="utf-8")
    code, out, _ = _commit(factory, capsys, dry["token"])
    assert code == 4 and out["error"] == "token_expired" and not fake.written()


def test_commit_without_human_gate_flag(factory, fake, capsys):
    dry = _dry(factory, capsys)
    code, out, _ = _commit(factory, capsys, dry["token"], gate=False)
    assert code == 4 and out["error"] == "human_gate_required" and not fake.written()


def test_commit_refuses_when_etag_changed(factory, fake, capsys):
    dry = _dry(factory, capsys)
    fake.etags[("bucket-test", "a/one.txt")] = "changed-by-someone-else"
    code, out, _ = _commit(factory, capsys, dry["token"])
    assert code == 4 and out["error"] == "object_changed" and not fake.written()
    assert fake.objects[("bucket-test", "a/one.txt")] == b"uno"


def test_commit_refuses_when_object_appeared_after_create_dry_run(factory, fake, capsys):
    dry = _dry(factory, capsys, obj="late.txt")
    fake.objects[("bucket-test", "late.txt")] = b"somebody"
    code, out, _ = _commit(factory, capsys, dry["token"], obj="late.txt")
    assert code == 4 and out["error"] == "object_changed" and not fake.written()


def test_commit_refuses_different_file_or_object(factory, fake, capsys):
    dry = _dry(factory, capsys)
    (factory / "payload.txt").write_bytes(b"altro contenuto")
    code, out, _ = _commit(factory, capsys, dry["token"])
    assert code == 4 and out["error"] == "request_mismatch" and out["field"] in ("sha256", "size")
    (factory / "payload.txt").write_bytes(b"nuovo")
    code, out, _ = _commit(factory, capsys, dry["token"], obj="a/other.txt")
    assert code == 4 and out["error"] == "request_mismatch" and out["field"] == "object"
    assert not fake.written()


def test_read_only_env_refuses_even_dry_run(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "upload", "prod", "docs", "--file", _upload_file(factory), "--dry-run")
    assert code == 4 and out["error"] == "read_only_env" and not fake.calls
    code, out, _ = run(factory, capsys, "delete", "prod", "docs", "--object", "p.txt", "--dry-run")
    assert code == 4 and out["error"] == "read_only_env" and not fake.calls


def test_read_only_envs_is_configurable(factory, fake, capsys):
    set_cfg(factory, _config(extra="  read_only_envs: [staging]\n  protected_envs: []\n  write:\n    enabled: true\n"))
    code, out, _ = run(factory, capsys, "upload", "staging", "docs", "--file", _upload_file(factory), "--dry-run")
    assert code == 4 and out["error"] == "read_only_env"
    out = _dry(factory, capsys, env="prod", obj="p.txt")           # prod non e' piu' in sola lettura
    assert out["token"]


def test_protected_env_needs_confirm_env(factory, fake, capsys):
    set_cfg(factory, _config(extra="  read_only_envs: []\n  protected_envs: [staging]\n  write:\n    enabled: true\n"))
    code, dry, _ = run(factory, capsys, "upload", "staging", "docs", "--file", _upload_file(factory),
                       "--object", "s.txt", "--dry-run")
    assert code == 0 and dry["confirm_env_required"] is True and dry["commit_requires"]["confirm_env"] == "staging"
    code, out, _ = _commit(factory, capsys, dry["token"], env="staging", obj="s.txt")
    assert code == 4 and out["error"] == "confirm_env_required" and not fake.written()
    code, out, _ = _commit(factory, capsys, dry["token"], env="staging", obj="s.txt", extra=("--confirm-env", "test"))
    assert code == 4 and out["error"] == "confirm_env_required"
    code, out, _ = _commit(factory, capsys, dry["token"], env="staging", obj="s.txt", extra=("--confirm-env", "staging"))
    assert code == 0 and out["ok"] is True


def test_mode_required(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "upload", "test", "docs", "--file", _upload_file(factory))
    assert code == 1 and out["error"] == "mode_required"
    code, out, _ = run(factory, capsys, "upload", "test", "docs", "--file", _upload_file(factory),
                       "--dry-run", "--commit")
    assert code == 1 and out["error"] == "mode_required"


def test_upload_missing_file(factory, fake, capsys):
    code, out, _ = run(factory, capsys, "upload", "test", "docs", "--file", str(factory / "nope"), "--dry-run")
    assert code == 1 and out["error"] == "file_missing"
