---
type: lint-report
date: 2026-11-20
scope: scoped, solo Check 2 + citation audit
files: [wiki/concepts/master-difetti-rilevati.md, wiki/concepts/llm-wiki-archivi-persistenza.md]
heal_eligible_count: 0
heal_eligible_categories: []
---

# Sweep rescan, Check 2 (2026-11-20)

Euristica del run 3: a riga, >=20 parole (senza marcatori di citazione), nessun `[^src:]`/`[^code:]`/wikilink in [riga, riga+3]; righe di tabella e `Storie collegate` non valutate. Scan eseguito con script locale sui due file (stato: modifiche non committate, `git diff --stat`: 8 righe aggiunte a master-difetti, 8/-1 a archivi-persistenza).

## Esito per item

| Item | Riga attuale | Esito | Motivo |
|---|---|---|---|
| W8 | master-difetti 18 (94 parole) | ANCORA PRESENTE | riga invariata; nessuna citazione in 18-21. La citazione e' stata messa nel blocco `## Aggiornamenti` (righe 119-125), fuori finestra. Il blocco dichiara l'esenzione per metodo (fix suggerito dal run 3), ma l'euristica meccanica la segnala ancora |
| W9 | 37 (36 parole) | ANCORA PRESENTE | stesso motivo: citazione a riga 41 (fuori finestra +3) e ora anche riga 122 |
| W10 | 65 (24) | ANCORA PRESENTE | citazione a riga 69, fuori finestra; nuova citazione solo a riga 123 |
| W11 | 79 (23->26) | ANCORA PRESENTE | citazione a riga 83, fuori finestra; nuova a riga 124 |
| W12 | 93 (23) | ANCORA PRESENTE | citazione a riga 97, fuori finestra; nuova a riga 125 |
| W13 | archivi-persistenza 49 (27) | ANCORA PRESENTE | riga invariata, nessuna citazione in 49-52; la fonte e' a riga 125 (blocco sweep), che dichiara il finding come «testo invariato» |
| W15 r.28 (`project.json`) | archivi-persistenza 28 | CHIUSO | riga ora dice «RS lo legge ... (`lib.rs:436-448`, `api_server.rs:877-884`)» con `[^src: ...persistenza-a.md §Cartella dati di progetto]` nella stessa riga; coerente con raw-a riga 57. Contraddizione annotata in `## Contradictions` (riga 131). Resta aperta la parte W15 su sommario riga 13 («17 archivi», «una sola versione»), esplicitamente rinviata (riga 127) |

Nota: il blocco `## Aggiornamenti` aggiunge solo citazioni lontane dalle righe segnalate; per chiudere W8-W13 con questa euristica la citazione va a fine blocco/riga entro 3 righe (W9-W13) oppure l'esenzione per W8 va accettata dal report principale. Nessun nuovo candidato introdotto dalle righe aggiunte (tutte con citazione). Riga 117 di master-difetti (`Storie collegate`) esclusa come nel run 3.

## Verifica citazioni nuove

| Citazione | Esito | Letto |
|---|---|---|
| `[^code: CLAUDE.md:77]` | OK | riga 77: riga tabella «**Evidenza** ... ipotesi ... Non puo' motivare uno skip» |
| `[^code: CLAUDE.md:95]` | OK (debole) | riga 95: «nessun altro file li ridefinisce. Il prefisso di namespace negli ID e' **opzionale**, ...»: la riga esiste e supporta il prefisso opzionale; il nome `ai_policy.py` e' nelle righe precedenti, non in 95 |
| `[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]` | OK | file esiste, `## Insight` riga 78; voce 3 a riga 84 coincide col testo |
| `[^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]` | OK | `### Schemi e campi` riga 268 |
| `[^src: ...persistenza-a.md §Cartella dati di progetto `.llm-wiki/`]` | OK | `## ...` riga 45; riga 57 contiene `lib.rs:436-448` e `api_server.rs:877-88x` |
| `[[2026-11-20-repo-llm_wiki-persistenza-{a,b,c}]]` (blocco archivi) | OK | esistono in `wiki/sources/` |

Nessun auto-fix applicato. `wiki/log.md` non toccato.

## Iterazione 2 (2026-11-21)

Stessa euristica, stesso script, stessi due file (modifiche non committate; letto `git diff -U0`). Il testo delle righe e' invariato: e' stata solo aggiunta la citazione in fondo alla riga.

| Item | Riga | Citazione in riga | Esito |
|---|---|---|---|
| W8 | master-difetti 18 | `[^src: raw/sessions/session-2026-11-20-16-3649aa67.md §Insight]` (la riga porta anche `[^code: CLAUDE.md:77]`, v. sotto) | CHIUSO (lo scan non la segnala piu') |
| W9 | 37 | `[^src: ...§Insight]` | CHIUSO |
| W10 | 65 | `[^src: ...§Insight]` | CHIUSO |
| W11 | 79 | `[^src: ...§Insight]` | CHIUSO |
| W12 | 93 | `[^src: ...§Insight]` | CHIUSO |
| W13 | archivi-persistenza 49 | `[^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]` | CHIUSO |

Nota W8: la citazione di riga 18 e' presente (`grep` sulla riga: `[^src: ...§Insight]` e `[^code: CLAUDE.md:77]`). La lettura grezza dell'output ha mostrato 2 marcatori sulla riga 18, nessuno sulle altre oltre al singolo `[^src]`. Nessun valore dedotto a memoria.

### Nuovi candidati dalle righe aggiunte

Lo scan segnala 2 nuove righe, entrambe note di metodo del keeper aggiunte in questa iterazione (WARNING, igiene, non heal-eligible):

- **W17** `wiki/concepts/master-difetti-rilevati.md` riga 128 (35 parole): «Iterazione 2 di sweep-reviews: le citazioni sono state spostate ...», sotto `### Aggiornamento (v2026-11-21)` (riga 127); nessuna citazione in 128-131. Nota di processo, non affermazione sul raw: candidata a esenzione o a un wikilink/`[^src]` alla riga stessa.
- **W18** `wiki/concepts/llm-wiki-archivi-persistenza.md` riga 127 (25 parole): «Aggiornamento (v2026-11-21), iterazione 2: la citazione della riga 49 e' spostata ...»; nessuna citazione in 127-130. Stesso carattere. Nota: prima dell'aggiunta la riga 127 era «Non toccati e rinviati» e la finestra raggiungeva la citazione a riga 130; l'inserimento ha spostato la finestra (ora «Non toccati e rinviati», riga 128, 25 parole, finestra 128-131, e' coperta dalla citazione a riga 131; non segnalata).

Riga 117 di master-difetti (`Storie collegate`) esclusa come nel run 3. Nessun altro candidato nei due file: lo scan produce solo 117 (esclusa), 128, 127.

### Citazioni nuove

- `[^src: ...session-2026-11-20-16-3649aa67.md §Insight]` sulle righe 18/37/65/79/93: file esistente, `## Insight` a riga 78 (verificato nel passo precedente); voci 3 (riga 84) coincide.
- `[^src: raw/2026-11-20-repo-llm_wiki.md §Schemi e campi]` riga 49: `### Schemi e campi` a riga 268 (verificato nel passo precedente).
- `[^code: CLAUDE.md:77]` (riga 18): invariata dal passo precedente, riga 77 e' la riga «Evidenza ... ipotesi». Non ricontrollato un cambiamento di CLAUDE.md: `git status` non lo indica modificato.
- Le citazioni sono generiche per sezione (§Insight): per le voci 5, 9, 11 il raw non ha evidenza di comando, quindi la fonte supporta l'affermazione come «dichiarata», coerente con il testo di stato.

Nessun auto-fix. `wiki/log.md` non toccato.
