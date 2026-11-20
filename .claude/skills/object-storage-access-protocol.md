---
name: object-storage-access-protocol
description: "Protocollo di accesso agli oggetti dei bucket S3-compatibili (capability opt-in object_storage_access) con le credenziali personali di un file env locale scelte per ambiente. Elenco, metadati e download di oggetti o cartelle, link pre-firmati di lettura e rinnovo di un link scaduto. TLS verificato per default. Ambienti in read_only_envs mai scritti; scrittura (upload, delete) SPENTA per default (object_storage_access.write.enabled) e, se accesa, solo dopo dry-run, token, gate umano R.14 ed etag invariato, con copia di sicurezza dell'oggetto e audit append-only. Tool: tools/object_storage/object_storage_access.py."
---

# Protocollo di accesso agli oggetti dei bucket — 5 fasi

Skill procedurale della capability `object_storage_access` (`factory.config.yaml → object_storage_access`).
Invocata da `/storage` (alias `/minio`) e dall'agente `storage-operator`. Tutte le operazioni passano da
`tools/object_storage/object_storage_access.py`: **mai** `aws`, `mc`, `boto3` o URL firmati a mano,
mai credenziali in chiaro in chat, nei comandi o nei file.

## Fonti

| Cosa | Dove |
|---|---|
| Endpoint e bucket per ambiente | `tools/object_storage/storage-targets.yaml` (copia di `storage-targets.example.yaml`, che ha solo endpoint e bucket fittizi) |
| Credenziali | file `object_storage_access.env_file` (default `.env.object-storage`, **gitignored: verificarlo prima di compilarlo**), unica fonte; i nomi delle variabili per target stanno nel registro |
| TLS | verificato per default; `ca_file` dell'endpoint nel registro (PEM non versionato, `tools/object_storage/certs/` gitignored); `verify_tls: false` solo se scritto esplicitamente, con avviso a ogni uso |
| Ambienti in sola lettura | `factory.config.yaml → object_storage_access.read_only_envs` (default `prod`) |
| Scrittura | `factory.config.yaml → object_storage_access.write.enabled` (default `false`) |
| Politiche (ambienti protetti, TTL, cartelle, scadenza dei link, timeout, audit) | `factory.config.yaml → object_storage_access` |
| Dipendenza | `boto3` (`tools/requirements.txt`), importata solo a capability accesa |

## Invocazione del tool

```bash
PY=python3; command -v python3 >/dev/null && python3 -c '' 2>/dev/null || PY=python
$PY tools/object_storage/object_storage_access.py <sottocomando> ...
```

Su Windows `python3` può essere l'alias dello Store che non esegue nulla: il ripiego su
`python` è voluto. Il tool scrive JSON su stdout e diagnostica su stderr. Con la capability spenta risponde
`capability_disabled` (exit 0), senza connettersi e senza importare `boto3`.

| Exit | Significato | Cosa fare |
|---|---|---|
| 0 | ok (anche `capability_disabled`) | — |
| 1 | uso/config (target ignoto, credenziali assenti, registro mancante, `boto3_missing`, chiave non scaricabile) | riportare `error` + `message` e le variabili attese se presenti |
| 2 | connessione/autenticazione (`auth_failed`, `tls_error`, `connection_failed`) | rete/VPN richiesta dal proprio ambiente, certificato TLS o credenziali; mai riprovare in loop |
| 4 | gate: `write_disabled`, `read_only_env`, token, TTL, `human_gate_required`, `confirm_env_required`, `object_changed`, `protected_dest` | `write_disabled`: la scrittura e' spenta, non aggirarla; scritture: rifare dry-run e gate da capo; su `read_only_envs` nessuna scrittura |
| 5 | errore S3 (`not_found`, permesso negato) | riportarlo; un oggetto assente e' un fatto, non un errore da aggirare |
| 6 | timeout | restringere il `--prefix` o `--max`; non insistere |

---

## Fase 1 — Boot

1. `object_storage_access.enabled: false` → ABORT pulito (lo dice anche il tool, `capability_disabled`).
2. Risolvi **ambiente** e **target** (il bucket logico del registro). Se l'utente non li indica, o sono
   ambigui, chiedi. Non scegliere mai `prod` per default. Gli alias sono quelli del registro: non inventarne.
3. `object_storage_access.py targets --env <env>`: il target esiste? Le credenziali sono pronte? Se no →
   stop con le variabili da aggiungere al file env.
4. Prima operazione della sessione su un target: `object_storage_access.py check <env> <target>`, poi riporta in
   una riga bucket, esito della connessione e `tls_verified`. Un avviso `warning` (TLS non verificato) va
   riportato all'utente, non ignorato.

## Fase 2 — Lettura

Prima l'elenco, poi i metadati, poi il contenuto:

```bash
$PY tools/object_storage/object_storage_access.py list     <env> <target> [--prefix P] [--no-recursive] [--max N]
$PY tools/object_storage/object_storage_access.py stat     <env> <target> --object <chiave>      # dimensione, data, etag, tipo
$PY tools/object_storage/object_storage_access.py download <env> <target> --object <chiave> [--dest D]
$PY tools/object_storage/object_storage_access.py presign  <env> <target> --object <chiave> [--expires S]
$PY tools/object_storage/object_storage_access.py renew-link --url <URL scaduto> [--expires S]
```

- `list` e' limitato da `list_max_keys`: con `--prefix` e `--max` restringi, non scaricare tutto per cercare.
- `download` di una chiave che termina con `/` scarica la cartella; il default e' `download_dir`
  (`.object-storage-state/downloads`, gitignored). Le chiavi che uscirebbero dalla cartella di destinazione sono
  rifiutate (`unsafe_key`).
- `presign` firma un link di **sola lettura** con scadenza `default_link_expires_s`; `--expires` da 1 a 604800
  secondi (limite SigV4: 7 giorni). Il link e' un segreto a scadenza: consegnalo a chi lo ha chiesto, non
  scriverlo in file versionati.
- `renew-link` rilegge bucket e chiave dall'URL e li accetta solo se il bucket e' nel registro
  (`bucket_not_in_registry` altrimenti).
- `--bucket` usa un altro bucket con le credenziali del target: solo su richiesta esplicita.

## Fase 3 — Presentazione

- Tabella markdown compatibile con il terminale, al massimo circa 30 righe. Per il resto indica conteggi e
  `truncated`.
- Cita sempre ambiente, bucket e chiave da cui viene il dato.
- Il contenuto di un oggetto puo' contenere dati personali: mostra solo cio' che serve alla domanda. Su ambienti
  protetti maschera di default, salvo richiesta esplicita dell'utente per il singolo valore.
- **Mai** copiare oggetti di ambienti protetti in `raw/`, `wiki/`, `deliverables/`, `management/`, `memory/`,
  kanban, log o commit: il tool rifiuta gia' `--dest` in quelle cartelle (`protected_dest`).
- Quando la lettura serve a un'indagine restituisci le evidenze nel blocco sotto.

### Blocco di evidenze (indagini)

```json
{"env": "test", "target": "documents", "bucket": "bucket-di-esempio-test",
 "window": {"from": "2026-11-05T09:00", "to": "2026-11-05T09:30", "tz": "UTC"},
 "ids": {"oggetto": "...", "entita": "..."},
 "findings": [{"claim": "...", "source": "object-storage", "where": "test/documents",
               "how": "list --prefix ... | stat ...", "evidence": "chiave, dimensione, data, etag"}],
 "not_verified": ["..."]}
```

Su ambienti protetti `findings` riporta chiavi, dimensioni e conclusioni, non contenuti in chiaro.

## Fase 4 — Scrittura (opt-in, gate umano R.14)

**Spenta per default.** Con `object_storage_access.write.enabled: false` il tool rifiuta `upload` e `delete`
(exit 4 `write_disabled`): non si aggira e non si propone di accenderla al posto dell'utente. Accenderla e' una
scelta esplicita del maintainer, nella config.

**Mai sugli ambienti in `read_only_envs` (default prod)**, nemmeno a scrittura accesa: il tool rifiuta, dry-run
compreso, prima di connettersi (exit 4 `read_only_env`). Una modifica li' si prepara per chi ha titolo e ci si ferma.
Negli altri ambienti la scrittura e' ammessa nei limiti dei permessi dell'utenza, sempre in tre passi. **`--commit`
richiede il token del dry-run, `--human-gate-approved` (il sì umano esplicito dato dopo il dry-run) e, sugli
ambienti protetti, `--confirm-env`. Un subagente non esegue mai `--commit` e non passa mai `--human-gate-approved`.**
Il `delete` agisce su un oggetto alla volta (una cartella e' rifiutata: `folder_delete`).

**4.1 Dry-run.**

```bash
$PY tools/object_storage/object_storage_access.py upload <env> <target> --file <F> [--object K] --dry-run
$PY tools/object_storage/object_storage_access.py delete <env> <target> --object K --dry-run
```

Legge lo stato dell'oggetto (assente, da sovrascrivere, da cancellare), registra la scrittura pendente e
restituisce `token` e `expires_at` (TTL `pending_ttl_minutes`).

**4.2 Gate.** Con `AskUserQuestion` (mai dedotto da messaggi precedenti, mai riusato fra scritture diverse),
mostra:

- ambiente + bucket + chiave;
- l'azione (upload o delete), il file (percorso, dimensione, hash) e lo stato dell'oggetto dal dry-run
  (assente, da sovrascrivere con quale etag e dimensione, da cancellare);
- scadenza del token.

Opzioni: «Esegui il commit» / «Annulla». Su un ambiente in `protected_envs` che non sia anche in `read_only_envs`
il gate e' **doppio**: prima la conferma come sopra, poi una seconda domanda separata che ripete ambiente e chiave
(«Confermi di nuovo: <azione> di <chiave> su <AMBIENTE>?»).

**4.3 Commit.** Solo dopo la conferma (o le due conferme):

```bash
$PY tools/object_storage/object_storage_access.py upload <env> <target> --file <F> [--object K] --commit \
  --token <token> --human-gate-approved [--confirm-env <env>]   # --confirm-env obbligatorio sugli ambienti protetti
```

Il tool esegue solo con lo stesso file e lo stesso oggetto del dry-run e solo se l'**etag dell'oggetto non e'
cambiato** dal dry-run (altrimenti exit 4 `object_changed`: si riparte da 4.1 con un nuovo gate). Prima salva una
copia dell'oggetto precedente in `state_dir`, dopo rilegge e verifica. Il token vale una volta sola.

**4.4 Traccia.** Il tool appende la scrittura confermata a `object_storage_access.audit_log` (append-only).
Riporta all'utente l'esito, il percorso della copia di sicurezza e quello dell'audit. Se la scrittura serve a un
TSK, cita l'evento nel TSK. Non duplicare in `wiki/log.md`: la wiki e' di wiki-keeper.

## Fase 5 — Chiusura

- Nessun dry-run lasciato pendente senza dirlo: se l'utente annulla, dichiara che il token scade da solo,
  perche' non c'e' niente da revocare.
- Mai credenziali, link pre-firmati di ambienti protetti o contenuti di oggetti protetti nel report di sessione.

## Invarianti

- **OS-1**: nessuna scrittura senza `write.enabled: true`, dry-run, token e gate umano esplicito sulla stessa
  invocazione. Un subagente non esegue mai `--commit` (R.14).
- **OS-2**: gli ambienti in `read_only_envs` non si scrivono mai, nemmeno in dry-run e nemmeno con un'utenza che
  ne avrebbe i permessi.
- **OS-3**: nessun segreto in output, argomenti di comando, file versionati o log; i link pre-firmati sono segreti a scadenza.
- **OS-4**: il commit procede solo con etag invariato; una copia di sicurezza precede ogni sovrascrittura o
  cancellazione e ogni scrittura confermata lascia una riga nell'audit.
- **OS-5**: TLS verificato per default; `verify_tls: false` e' una deroga dichiarata e segnalata, mai silenziosa.
- **OS-6**: gli oggetti di ambienti protetti non entrano nelle cartelle versionate della factory.
- **OS-7**: nessuna scrittura per sostenere o verificare un'analisi, e nessun riferimento ad AI, a Claude o alla
  factory nei file caricati sullo storage o nei metadati dell'oggetto.
