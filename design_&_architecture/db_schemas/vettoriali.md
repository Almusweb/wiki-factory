---
id: db-schemas-vettoriali
title: "Scheda vettoriali: indice LanceDB v2 e v1, revisioni di embedding"
status: draft
created: 2026-11-23
updated: 2026-11-23
satisfies: [US-020]
decision_refs: [ADR-EP003-001]
wiki_snapshot: 2026-11-20
---

# Scheda vettoriali — indice LanceDB e revisioni di embedding

> Schema delle due tabelle dell'indice vettoriale di llm-wiki (A01 corrente, A02 legacy) e del file di revisione di embedding (A03): colonne, tipi, nullabilità, significato, versione e comportamento su errore. I punti non noti sono marcati e rimandano al gap.

> **In scrittura fino a TSK-034.** Mancano la validazione dell'id di pagina, i limiti di dimensione e la sezione A03. Il README non è ancora aggiornato.

## Perimetro

La scheda documenta gli archivi A01, A02 e A03 dell'indice `README.md`, come risultano dalle storie citate alla data di `wiki_snapshot`. Non propone interventi sul codice. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Acceptance Criteria]

Questi dati stanno nel README e la scheda non li ripete:
- scrittore, lettore e stato di ogni archivio (sezione Archivi, righe A01..A03);
- id di pagina corrente e legacy (I3, I4), `chunk_id` (I5), nome del file di revisione (I6);
- relazioni R4 (pagine → A01), R5 (A01 → A02), R6 (A01 → A03), R7 (configurazione di embedding → A01, A03).

## Convenzioni

- Norma: ADR-EP003-001 (marcatore §D, citazioni §F).
- Il layout di questa scheda è il modello delle schede di `db_schemas/` (decisione dell'utente del 2026-11-23, nessun ADR). Per ogni archivio: Posizione, Campi, Regole del dato, Versione, Archivio mancante o illeggibile, Effetto della scrittura successiva. Poi le regole comuni agli archivi, il contesto di lettura e lo storico.
- Tabella dei campi: `Campo | Tipo | Nullabile | Significato | Fonte`. Nella colonna Nullabile: `no`, `sì` oppure il marcatore.
- I tipi sono quelli della fonte (`u32`, `f32`, «testo»). Il tipo fisico di LanceDB non è riportato se la fonte non lo dà.
- Un dato presente in wiki ma in nessuna storia non entra nella scheda: la sottosezione lo dichiara e rimanda alla segnalazione al product-manager (ADR-EP003-001 §F).

## A01 — Tabella LanceDB v2 `wiki_chunks_v2`

### Posizione

- Database LanceDB in `.llm-wiki/lancedb`, nella cartella del progetto; tabella `wiki_chunks_v2`. Scrittore e lettore: README, riga A01. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]
- Una riga per chunk di pagina: relazione R4 del README.

### Campi

| Campo | Tipo | Nullabile | Significato | Fonte |
|---|---|---|---|---|
| `chunk_id` | testo | no | Id del chunk, usato solo per debug; derivazione in I5 del README | US-020 §Fonti; US-020 §Business Rules |
| `page_id` | testo | no | Id della pagina nel formato corrente; forma e validazione in I3 del README | US-020 §Fonti; US-020 §Business Rules |
| `chunk_index` | `u32` | no | Indice del chunk nella pagina | US-020 §Fonti; US-020 §Business Rules |
| `chunk_text` | testo | no | Testo del chunk | US-020 §Fonti; US-020 §Business Rules |
| `heading_path` | testo | no | Significato e forma **non verificato** [gap: llm-wiki-vettoriali-colonne-non-dichiarate] | US-020 §Fonti; US-020 §Business Rules |
| `vector` | lista a lunghezza fissa di `f32` | no | Vettore di embedding del chunk; dimensione in «Regole del dato» | US-020 §Fonti; US-020 §Business Rules |

Lo schema letto non ha colonne per immagini. Stato dello schema multimodale: **non verificato** [gap: llm-wiki-multimodale-stato]. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Business Rules]

Fonti della tabella:
- US-020 §Business Rules: [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Business Rules]
- US-020 §Fonti: [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]

### Regole del dato

- La dimensione di `vector` è fissata dal primo chunk di una scrittura. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Business Rules]
- Coerenza della dimensione al cambio di modello: **non verificato** [gap: llm-wiki-embedding-cambio-modello]. Legame con la configurazione di embedding: R7 del README. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Acceptance Criteria]

### Versione

- Solo il suffisso `_v2` del nome della tabella; nessun campo di versione. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]
- Compatibilità con la tabella v1: R5 del README. Regole trasversali: `versioni-e-compatibilita.md` (US-024).

### Archivio mancante o illeggibile

- Non gestito: un errore di apertura è propagato come stringa.
- Su tabella assente, ricerca e conteggio restituiscono vuoto o 0.

[^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]

### Effetto della scrittura successiva

Non documentato qui: nessuna storia lo porta. Segnalato al product-manager il 2026-11-23 (ADR-EP003-001 §F).

## A02 — Tabella LanceDB v1 `wiki_vectors` (legacy)

### Posizione

- Stesso database di A01, tabella `wiki_vectors`. Scrittore e lettore: README, riga A02. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]
- Una riga per pagina. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]
- RS espone ancora `vector_upsert`. Chiamanti e scrittura effettiva: **non verificato** [gap: llm-wiki-vector-v1-chiamanti] (README, discrepanza D4). TS usa la tabella solo per il conteggio e per l'eliminazione. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]

### Campi

| Campo | Tipo | Nullabile | Significato | Fonte |
|---|---|---|---|---|
| `page_id` | **non verificato** [gap: llm-wiki-vettoriali-colonne-non-dichiarate] | **non verificato** [gap: llm-wiki-vettoriali-colonne-non-dichiarate] | Id della pagina nel formato legacy, uguale al nome base del file della pagina; forma in I4 del README | US-020 §Fonti; US-020 §Business Rules |
| `vector` | **non verificato** [gap: llm-wiki-vettoriali-colonne-non-dichiarate] | **non verificato** [gap: llm-wiki-vettoriali-colonne-non-dichiarate] | Vettore della pagina | US-020 §Fonti; US-020 §Business Rules |

Fonti della tabella:
- US-020 §Business Rules: [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Business Rules]
- US-020 §Fonti: [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]

### Regole del dato

- Dimensione di `vector` e regola che la fissa: **non verificato** [gap: llm-wiki-vettoriali-colonne-non-dichiarate].
- Rimozione delle righe v1 e della tabella: R5 del README.

### Versione

`_v1` implicito. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]

### Archivio mancante o illeggibile

Come A01: un errore di apertura è propagato come stringa; su tabella assente, ricerca e conteggio restituiscono vuoto o 0. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-020-schema-archivi-vettoriali/US-020.md §Fonti]

### Effetto della scrittura successiva

Non documentato qui: nessuna storia lo porta. Segnalato al product-manager il 2026-11-23 (ADR-EP003-001 §F).

## Contesto di lettura (non citazioni)

Pagine wiki da cui US-020 ricava i dati. Non sono fonti della scheda.
- `llm-wiki-schema-dati`: schema LanceDB v2 e v1
- `llm-wiki-archivi-persistenza`: righe di inventario delle due tabelle
- `gaps`: gap citati nei marcatori

## Storico aggiornamenti

| Data | Modifica | Gap chiusi |
|---|---|---|
| 2026-11-23 | Prima stesura, sezioni A01 e A02 (TSK-033); layout modello delle schede per decisione dell'utente, senza ADR; aperto il gap `llm-wiki-vettoriali-colonne-non-dichiarate` | nessuno |
