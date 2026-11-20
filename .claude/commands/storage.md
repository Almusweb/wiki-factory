---
description: "Legge gli oggetti dei bucket S3-compatibili degli ambienti del registro (capability opt-in object_storage_access) con le credenziali del file env configurato: elenco, metadati, download, link pre-firmati e rinnovo. TLS verificato per default; ambienti in read_only_envs mai scritti; scrittura (upload, delete) spenta per default (object_storage_access.write.enabled) e, se accesa, solo dopo dry-run, token e gate umano. Alias: /minio."
argument-hint: "targets [<env>] · check <env> <target> · list <env> <target> [<prefisso>] · stat|download|presign <env> <target> <chiave> · renew-link <URL> · upload|delete <env> <target> ..."
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# /storage

Argomenti utente: `$ARGUMENTS`

Segui `.claude/skills/object-storage-access-protocol.md`. Tool unico: `tools/object_storage/object_storage_access.py`.
`/minio` e' un alias di questo comando (`.claude/commands/minio.md`).

## Sintassi

```
/storage targets [<env>]                          # registro: bucket e credenziali pronte o mancanti
/storage check <env> <target>                     # credenziali, raggiungibilita', TLS
/storage list <env> <target> [<prefisso>]         # oggetti: chiave, dimensione, data, etag (--no-recursive, --max)
/storage stat <env> <target> <chiave>             # metadati di un oggetto
/storage download <env> <target> <chiave> [<dest>]    # un oggetto, o una cartella se la chiave termina con /
/storage presign <env> <target> <chiave> [<secondi>]  # link pre-firmato di sola lettura (default 3600, massimo 604800)
/storage renew-link <URL>                         # nuovo link per l'oggetto di un link scaduto
/storage upload <env> <target> <file> [<chiave>]  # solo con object_storage_access.write.enabled: true: dry-run -> gate -> commit
/storage delete <env> <target> <chiave>           # idem: un oggetto alla volta
```

`<env>`: gli ambienti del registro (esempio: `test` · `staging` · `prod`). Quelli in `read_only_envs` (default
`prod`) sono **in sola lettura**: nessuna scrittura, nemmeno in dry-run; gli oggetti non vanno in cartelle versionate.
`<target>`: i bucket logici del registro (elenco aggiornato: `/storage targets`).

## Comportamento

1. **Boot** (Fase 1): target e credenziali da `targets`, primo `check` della sessione sul target. Un avviso TLS
   (`verify_tls: false` nel registro) e' la prima riga della risposta.
2. **Lettura** (Fase 2): `list` con prefisso prima di `stat` e `download`; mostra il comando che esegui.
   Un oggetto assente (exit 5 `not_found`) si riporta com'e'.
3. **Link**: `presign` e `renew-link` producono link di sola lettura con scadenza; consegnali a chi li ha chiesti,
   senza scriverli in file versionati.
4. **Scrittura** (spenta per default: `write_disabled`; mai su `read_only_envs`): `upload`/`delete --dry-run`, poi
   gate umano `AskUserQuestion` con ambiente, bucket, chiave e stato dell'oggetto, poi `--commit --token
   --human-gate-approved` solo dopo il sì esplicito (e `--confirm-env` sugli ambienti protetti). Se l'oggetto cambia
   dopo il dry-run (`object_changed`) si riparte da capo. Il token da solo non basta.
5. **Scrittura non ammessa** (spenta o ambiente in sola lettura): prepara per chi ha titolo cio' che serve
   (file, chiave, azione) e fermati; nessun tentativo con altre utenze o altri strumenti.

## Prerequisiti

- `factory.config.yaml → object_storage_access.enabled: true`
- Python con `pyyaml` e `boto3` (`tools/requirements.txt`)
- Rete raggiungibile (VPN se il proprio ambiente la richiede) e certificato TLS valido (`ca_file` nel registro se l'endpoint usa una CA privata)
- Registro `tools/object_storage/storage-targets.yaml` (copia di `tools/object_storage/storage-targets.example.yaml`) e
  file credenziali `object_storage_access.env_file` (default `.env.object-storage`, gitignored) con le variabili
  citate dal registro

Per indagini lunghe in più passi in sola lettura, delega all'agente `storage-operator`. Il gate, il token
e il commit restano sempre nella sessione principale.
