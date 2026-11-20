---
id: ADR-EP003-001
title: "Formato di db_schemas: indice degli archivi, stati derivati, marcatura «non verificato» e citazioni"
status: accepted
created: 2026-11-20
deciders: [utente, lead-architect]
satisfies: [US-019]
supersedes: []
pending_clarification: []
---

# ADR-EP003-001 — Formato di `db_schemas/`

## Contesto

`db-dev` lavora su schemi documentati in `design_&_architecture/db_schemas/`, che al 2026-11-20 è vuota. US-019 chiede un indice di tutti gli archivi dell'inventario e dello store applicativo, con stato di documentazione, posizione, scrittore e lettore, identificatori con la loro derivazione e relazioni fra archivi; ogni relazione o campo non noto va marcato «non verificato» con rimando al gap, senza ometterlo né inventarlo. [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-019-indice-db-schemas-e-relazioni/US-019.md §Acceptance Criteria]

Le storie US-020..US-024 dichiarano `depends_on: [US-019]` nel frontmatter: le loro schede di dettaglio devono usare lo stesso formato dell'indice. Parte della conoscenza è ancora nei gap e arriva da EP-002 (in particolare US-014 per lo store applicativo); fino ad allora i punti relativi restano «non verificati». [^src: management/kanban/EP-003-schemi-attuali-layer-persistenza/US-023-schema-store-applicativo/US-023.md §Business Rules]

Il formato è quindi un contratto per cinque storie e per `db-dev`, mentre il contenuto dell'indice cambia a ogni chiusura di gap. Questo ADR fissa il formato; l'indice resta un documento vivo.

## Decisione

### §A Struttura della cartella

| File | Storia | Contenuto |
|---|---|---|
| `README.md` | US-019 | Indice: archivi, archivi fuori inventario, identificatori, relazioni, discrepanze note, mappa delle schede, storico aggiornamenti |
| `vettoriali.md` | US-020 | Indice vettoriale corrente e legacy, file di revisione |
| `archivi-progetto.md` | US-021 | Archivi di dati di progetto elencati da US-021 |
| `chat-sessioni-cronologia.md` | US-022 | Chat, sessioni agente, cronologia dei file |
| `store-applicativo.md` | US-023 | Store applicativo |
| `versioni-e-compatibilita.md` | US-024 | Versioni di formato e regole di compatibilità, trasversali |

- Nasce subito solo `README.md`. Le schede si scrivono con la loro storia: niente file segnaposto, perché un file vuoto sembrerebbe documentazione. Il README le elenca come «da scrivere».
- Ogni archivio dell'indice appartiene a una sola scheda. Una derivazione condivisa da due schede (ad esempio il nome dei file di revisione e di cronologia) sta una volta sola nel README, sezione Identificatori, e le schede vi rimandano.
- Nomi dei file in minuscolo con `-`, per contenuto e non per numero di storia; la corrispondenza file-storia sta nel README.

### §B Tabella degli archivi

- Colonne: `# | Archivio | Posizione (ambito) | Scrittore | Lettore | Stato | Scheda | Fonte`. L'ambito è `progetto` o `applicativo`.
- Una riga per ogni riga della tabella di inventario della wiki, nello stesso ordine, con numero stabile `A01..`. L'unità di conteggio è la riga della tabella di inventario (decisione dell'utente del 2026-11-20).
- I file o le cartelle citati in wiki ma fuori dall'inventario vanno in una tabella separata con numero `X01..`, non conteggiati. Un `Xnn` confermato come archivio diventa il primo `Ann` libero; la riga `X` resta con il rimando.
- I numeri non si riassegnano.
- I campi degli archivi non stanno nell'indice ma nelle schede, per non duplicarli.
- Un preambolo vale per tutte le righe con ambito `progetto`: creazione della cartella dati e limite del campione letto.

### §C Stato derivato

Lo stato di una riga si **deriva** dai marcatori presenti nella riga, non si sceglie a parte:

| Stato | Condizione |
|---|---|
| `documentato` | nessun marcatore «non verificato» nella riga |
| `parziale` | almeno un marcatore nella riga; le incognite di schema non legate a una colonna vanno nella cella Stato |
| `non verificato` | l'esistenza stessa come archivio non è stabilita (solo righe `X`) |

La stessa regola vale per le tabelle degli identificatori e delle relazioni. Lo stato è scritto in chiaro, senza grassetto: il grassetto è riservato al marcatore (§D).

### §D Marcatura «non verificato»

Sintassi esatta, un solo gap o più gap separati da virgola e spazio:

```text
**non verificato** [gap: <slug>]
**non verificato** [gap: <slug-1>, <slug-2>]
```

Regex di controllo: `\*\*non verificato\*\* \[gap: [a-z0-9-]+(, [a-z0-9-]+)*\]`

- Lo slug deve corrispondere a un gap già presente in `wiki/gaps.md` al momento della scrittura. Senza gap non si marca: prima si apre il gap (append, `wiki-gap-protocol`), poi si scrive il marcatore.
- Il marcatore va nella cella del dato ignoto, non in una nota generica di riga. Fanno eccezione solo i due avvisi del preambolo (§B).
- Nel diagramma delle relazioni l'unica abbreviazione ammessa è `n.v.` sull'etichetta di un arco tratteggiato, sempre coperta da una riga della tabella delle relazioni con il marcatore completo.
- I qualificatori della fonte («dai commenti di...», «nel campione») si riportano con il loro senso e non sono marcatori.
- Un marcatore si rimuove solo quando il gap è chiuso **e** la storia che porta la nuova conoscenza è aggiornata (§F). La rimozione si registra nello storico del README.

### §E Identificatori e relazioni

- **Identificatori**: tabella `# | Identificatore | Forma e derivazione | Generato da | Usato in | Stato | Fonte`, numeri stabili `I1..`. Entrano gli identificatori condivisi fra archivi o richiamati da US-019 (progetto, pagina nel formato corrente e legacy, hash usati come nomi di file, chat, sessione) e i riferimenti a sorgenti e pagine usati da più archivi. Gli identificatori interni a un solo archivio vanno nella scheda.
- **Relazioni**: tabella `# | Da | A | Via | Regola | Stato | Fonte`, numeri stabili `R1..`. «Da» è l'archivio, o l'entità esterna, che definisce l'identificatore; «A» è chi lo usa. Le conseguenze sui rischi non entrano nell'indice: si rimanda alle storie di EP-004.
- **Diagramma**: mermaid `flowchart`, derivato dalla tabella delle relazioni, che fa fede. Ogni arco appartiene a una riga `R`; ogni riga `R` ha almeno un arco. Linea continua per relazioni `documentato` o `parziale`, tratteggiata con `n.v.` per relazioni `non verificato`. Gli archivi senza relazioni desumibili dalla wiki non compaiono nel diagramma e il README lo dichiara.

### §F Citazioni

- Nei file di `db_schemas/` si citano solo storie o ADR: `[^src: management/kanban/EP-*/US-*/US-*.md §<sezione>]`, in cascata come da `citation-rules`. Niente `[^src: wiki/...]` e niente wikilink.
- La cella Fonte usa una forma breve (`US-019 §Fonti`). Subito sotto ogni tabella un blocco «Fonti della tabella» riporta la citazione completa di ogni forma breve usata.
- La wiki compare solo come slug di gap nei marcatori e in una sezione finale «Contesto di lettura (non citazioni)», con gli slug delle pagine in backtick, dichiarati non normativi.
- Un dato presente in wiki ma in nessuna storia non entra nell'indice: lo si segnala al product-manager perché lo porti in una storia.

### §G Aggiornamento

- Il README porta nel frontmatter `wiki_snapshot: <AAAA-MM-GG>`, la data dello stato della wiki che riflette.
- Un aggiornamento avviene quando un gap citato viene chiuso e la storia relativa è aggiornata: si aggiornano le righe, si ricalcola lo stato (§C), si aggiorna `wiki_snapshot` e si accoda una riga allo storico (data, righe toccate, gap chiusi).
- Lo scrittore è `lead-architect`, con la stessa disciplina di proposta e OK. Questo ADR non cambia; una revisione del formato è un nuovo ADR che lo sostituisce.

## Alternative valutate

| Alternativa | Motivo scartata |
|---|---|
| Un file per archivio | 17 file più i candidati, per un contenuto che le storie raggruppano già in cinque schede; la navigazione peggiora senza vantaggio |
| Diagramma `erDiagram` | Suggerisce chiavi esterne e cardinalità relazionali che la wiki non dà: gli archivi sono file, le relazioni sono identificatori condivisi |
| Indice in YAML o JSON leggibile da script | Sovradimensionato per un indice di documentazione; il marcatore con regex fissa basta per i controlli automatici |
| Solo README, senza ADR | Il formato vincola US-020..US-024 e `db-dev`, mentre il README cambia a ogni chiusura di gap: serve un contratto stabile separato dal contenuto |
| Omettere i punti ignoti o rinviarli alle schede | Viola US-019: ogni punto non noto va marcato, non omesso |

## Conseguenze

- US-020..US-024 scrivono le schede con colonne, stati, marcatore e citazioni di questo ADR.
- Lo stato di ogni archivio è verificabile a script: si contano i marcatori nella riga.
- Gli esiti di EP-002 (estrazioni in corso, TSK-005 e TSK-006) entrano con un aggiornamento del README, senza toccare questo ADR.
- La cascata delle citazioni può richiedere che il product-manager aggiorni una storia prima che un dato nuovo entri nell'indice.
- Id con prefisso di epica: un `ADR-001` locale renderebbe ambigua la citazione di `design_&_architecture/decisions/ADR-001.md` presente in una skill del master (`.claude/skills/references/premortem/fase-4-parallel-deep-dives.md`). Si usa la forma già presente in questa factory (`ADR-EP039-001`).

## Assunzioni

Nessuna assunzione «da confermare». Unità di conteggio degli archivi: la riga della tabella di inventario della wiki, decisa dall'utente il 2026-11-20. Le discrepanze fra le pagine wiki restano nel README, sezione «Discrepanze note», e nel gap `llm-wiki-archivi-sommario-conteggi`.

## Pending clarifications

Nessuna. Q_004 riguarda solo US-018 e Q_005 solo EP-004 (US-025..US-033): nessuna delle due tocca US-019.

## Cross-link

- Indice: `design_&_architecture/db_schemas/README.md`
- US-019: `management/kanban/EP-003-schemi-attuali-layer-persistenza/US-019-indice-db-schemas-e-relazioni/US-019.md`
- Storie vincolate: US-020, US-021, US-022, US-023, US-024 (EP-003)
- Skill: `citation-rules`, `wiki-gap-protocol`
