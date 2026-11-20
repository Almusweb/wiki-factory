---
description: "Alias di /storage: legge gli oggetti dei bucket S3-compatibili (MinIO e simili) degli ambienti del registro, capability opt-in object_storage_access. Stessi argomenti, stesso protocollo e stessi gate di /storage."
argument-hint: "come /storage: targets · check · list · stat · download · presign · renew-link · upload · delete"
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# /minio

Argomenti utente: `$ARGUMENTS`

Alias sottile di `/storage`: esegui `.claude/commands/storage.md` con gli stessi argomenti, senza differenze di
sintassi, di protocollo (`.claude/skills/object-storage-access-protocol.md`) o di gate. La scrittura resta
spenta per default e, se accesa, passa da dry-run, token e gate umano nella sessione principale.
