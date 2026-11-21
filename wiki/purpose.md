---
type: purpose
domain: "Wiki tecnica di llm_wiki, applicazione desktop di terzi (GPL v3) usata dal maintainer in tre linee: upstream allineato su main, branch di hotfix per PR al maintainer upstream, branch personale di customizzazione; serve a capire il comportamento dell'app per linea e a valutare l'impatto di ogni release upstream sulle personalizzazioni"
priority_entity_types: [concept, entity, synthesis, source]
tone: mixed
exclusions: [valori-di-credenziali-e-segreti, dati-personali, dati-dell-attivita-lavorativa-del-maintainer-non-riguardanti-il-codice, contenuto-del-repo-del-cliente-riprodotto-alla-lettera, conclusioni-legali-sulla-licenza]
---

# Purpose

> **Stato: accettato in forma provvisoria dal maintainer il 2026-11-21.** I punti marcati
> «da confermare» restano aperti e non sono decisioni. Il modello a fork unica potrebbe
> cambiare: il maintainer valuta un repo privato separato (una copia, non una fork) per il
> lavoro personale, ancora da decidere.
>
> Scritto il 2026-11-21 da `wiki-keeper` per deroga puntuale del maintainer (vedi la sezione
> finale). Le etichette sono tre:
> **[dettatura]** trascrive le direttive dette dal maintainer;
> **[proposta della sessione principale, da confermare]** indica ciò che la sessione
> principale ha aggiunto nel brief e che il maintainer non ha detto;
> **[deduzione, da confermare]** indica ciò che ha aggiunto `wiki-keeper`. Dove un fatto
> viene dal repo o dalla configurazione e non da una dettatura, lo si dichiara. Il maintainer
> resta sovrano: questo file è contesto, non un gate.

## Dominio [dettatura]

`code_repos/llm_wiki` è una fork del maintainer (`Almusweb/llm_wiki`) di
<https://github.com/nashsu/llm_wiki> **[dettatura]**. Il progetto è di terzi, sotto GNU General
Public License v3.0: non è dettato, è un fatto del repo già registrato in wiki (**fatto osservato
in wiki**, [[llm-wiki-licenza-e-standard]]).
La wiki documenta il comportamento di questa applicazione desktop e il modo in cui la fork
viene usata, non il progetto di terzi in astratto. **[deduzione, da confermare]** Nota di contesto
da quanto già in wiki: il pattern «LLM Wiki» (descritto in [[pattern-llm-wiki]]) e
l'applicazione ([[llm-wiki-app]]) sono cose distinte; non confonderli.

## Le tre linee di lavoro [dettatura]

La fork si usa in tre modi. Ogni affermazione in wiki si riferisce a una sola linea.

| Linea | Branch | Scopo | Cosa la wiki documenta per questa linea |
|---|---|---|---|
| **1. Upstream allineato** | `main` | Resta allineato al repo padre. A ogni release upstream il maintainer sincronizza la fork su `main`. | Il comportamento dell'app **così come rilasciata upstream**, con la versione: architettura, moduli, persistenza, API, sicurezza, licenza. Le differenze tra una release e la successiva. |
| **2. Hotfix e bug** | branch dedicati di hotfix/bug (nome libero, uno per intervento) | Correggere difetti e proporre PR al maintainer upstream. | Il difetto (evidenza, file e simboli, condizioni), la correzione proposta e lo stato della PR. Solo il comportamento di `main` interessato dal difetto. |
| **3. Personalizzazione** | branch personale del maintainer, a suo uso esclusivo (**oggi `develop`, da confermare**) | Nuove funzionalità che integrano nell'app desktop funzioni di supporto all'attività lavorativa del maintainer. | Le funzionalità aggiunte, i punti di innesto nel codice upstream, e per ogni release upstream l'impatto sull'integrazione. |

Stato osservato oggi (2026-11-21), non dettato: la factory legge il branch `develop`
(`.factory-branches.yaml`, `factory.config.yaml` `code_paths[].vcs.base_branch`), e `main` e
`develop` puntano allo stesso commit (release v0.6.13, `e08cfce`). **Da confermare:** che il
branch personale sia `develop` e che resti tale. Se il nome cambia, vanno aggiornati questo
file e la configurazione della factory (non la wiki per prima).

## Regola di provenienza [proposta della sessione principale, da confermare]

Ogni affermazione sul comportamento dell'app dichiara a quale linea si riferisce, perché
upstream e custom non si confondano:

- **upstream su `main`**: indicare la versione (es. «upstream v0.6.13, commit `e08cfce`»);
- **personalizzazione**: indicare il branch personale e, quando serve, il commit.

Conseguenze pratiche per l'ingest **[deduzione, da confermare]**:

- ogni source page di `repo-sync` riporta in apertura linea, branch e commit letti; una fetta
  letta su un branch non dichiarato non si ingerisce senza segnalare il gap;
- finché `main` e il branch personale coincidono (oggi: v0.6.13) il testo vale per entrambe
  le linee e lo si dice una volta, in modo esplicito; dal primo commit di divergenza le
  pagine non possono più restare ambigue;
- le pagine già in wiki descrivono `e08cfce` (release v0.6.13, letto come `develop`): vanno
  lette come «upstream v0.6.13, identico alla personalizzazione al momento della lettura»;
  non vanno riscritte per questo, ma ogni nuovo `## Aggiornamenti` porta la linea;
- un comportamento osservato solo sul branch personale non entra mai in una pagina che
  descrive upstream, e viceversa; se serve confrontarli, una sezione dedicata con le due
  linee affiancate.

## Pull request upstream

Dettato è solo che i branch di hotfix/bug servono a proporre PR al maintainer upstream
**[dettatura]**. Il resto di questa sezione non è dettatura.

- **[proposta della sessione principale, da confermare]** Le PR verso upstream **partono da
  `main`** (non dal branch personale): dedotto dal modello di branch.
- **[proposta della sessione principale, da confermare]** **Non contengono personalizzazioni**:
  solo la correzione o la proposta. Dedotto dal modello di branch.
- **Nessuna traccia della factory** nel repo `llm_wiki` (origine: regole già in vigore sul
  repo cliente, `ai_attribution_policy.suppress_ai_traces: true` in `factory.config.yaml`;
  non viene da questa dettatura): niente ID kanban (EP/US/TSK), niente
  riferimenti a regole o documenti della factory, niente attribution AI né `Co-Authored-By`
  (vedi `ai_attribution_policy.suppress_ai_traces: true` in `factory.config.yaml`; i commit
  nel repo del cliente si fanno con `tools/vcs/sm_commit.py`).
- Conseguenza per la wiki **[deduzione, da confermare]**: la wiki può citare una PR e il suo
  stato; non riproduce nel repo `llm_wiki` nulla di ciò che la wiki sa della factory. La
  direzione è a senso unico: il legame fra ID kanban e PR vive solo qui, non lì.

## Caso d'uso ricorrente: sync-release → analisi d'integrazione [dettatura]

A ogni release upstream **[dettatura]**:

1. il maintainer sincronizza la fork su `main` (linea 1);
2. si analizza l'integrazione delle novità sul branch personale (linea 3).

**[proposta della sessione principale, da confermare]** La wiki deve rendere questa analisi
rapida e verificabile. Per ogni release, la wiki dovrebbe poter rispondere a:

- cosa cambia tra la release precedente e la nuova (moduli, formati dati, API, dipendenze,
  licenza, persistenza e migrazioni);
- quali personalizzazioni toccano i punti cambiati e che impatto hanno (conflitto, adattamento,
  nessuno);
- se qualche correzione di hotfix (linea 2) è stata assorbita da upstream, e quindi può
  uscire dal branch personale.

Forma attesa **[deduzione, da confermare]**: una pagina `synthesis` per release
(`syntheses/llm-wiki-integrazione-<versione>`), con la tabella «modulo toccato / personalizzazione
coinvolta / impatto / azione», che cita le source page di `repo-sync` delle due versioni
confrontate. Non esiste ancora: la wiki oggi copre una sola release (v0.6.13) e nessuna
personalizzazione.

## Vincolo di contesto: licenza [proposta della sessione principale, da confermare]

Non dettato. Il progetto è di terzi, sotto GNU General Public License v3.0: è un fatto del
repo, registrato in wiki (**fatto osservato**, [[llm-wiki-licenza-e-standard]]). La wiki lo
riporta come **vincolo di contesto** e, **[proposta della sessione principale, da confermare]**,
**non trae conclusioni legali**: niente giudizi sulla distribuzione della fork o delle personalizzazioni, niente
interpretazioni della GPL. Gli ingest si limitano a registrare fatti verificabili (testo
della licenza, anomalie come la licenza dichiarata dal server MCP) e rimandano le
conclusioni a una valutazione del maintainer.

## Tipi di entità prioritari [deduzione, da confermare]

Dall'esame delle pagine esistenti, l'ingest privilegia, in ordine:

1. **`concept`**: moduli e meccanismi dell'app (persistenza, ingest, agente, API locale,
   sicurezza, versioni e migrazioni, rischi);
2. **`entity`**: l'applicazione e i suoi componenti nominati ([[llm-wiki-app]], [[llm-wiki-mcp-server]]);
3. **`synthesis`**: confronti e valutazioni trasversali (oggi
   [[llm-wiki-sintesi-rischi-persistenza]]; domani le analisi di integrazione per release);
4. **`source`**: un riassunto per ogni estrazione di `repo-sync`, con linea, branch e commit.

Le pagine della famiglia «Factory» (meta-framework, non riguarda l'applicazione) restano
separate dall'applicazione e non si mescolano alla provenienza per linea.

## Tono e convenzioni [deduzione, da confermare]

- `mixed`: descrittivo e cauto per il comportamento dell'app (ogni claim ha evidenza, file e
  simbolo, e distingue «osservato», «dedotto», «non verificato»); prescrittivo solo per le
  regole di questo file.
- Esiti di verifica con le etichette già in uso: confermato per lettura, non conclusivo,
  smentito; distinguere sempre lettura da esecuzione.
- Nessuna gravità o priorità presentata come decisa: sono proposte fino alla decisione del
  maintainer.

## Esclusioni

| Esclusione | Origine |
|---|---|
| Valori di credenziali e segreti (token, chiavi API, password): si citano solo i nomi di campo | **[deduzione, da confermare]**; coerente con la pratica già in uso nei log di ingest e con [[llm-wiki-sicurezza]] |
| Dati personali (nomi o contatti di persone oltre agli autori già citati dalle fonti pubbliche del progetto) | **[deduzione, da confermare]** |
| Dati dell'attività lavorativa del maintainer che non riguardano il codice (clienti, progetti, contenuti professionali che motivano le personalizzazioni) | **[deduzione, da confermare]**: la wiki descrive le funzionalità, non il contesto di lavoro che le giustifica |
| Contenuto del repo del cliente riprodotto alla lettera (codice, testi) | **[deduzione, da confermare]**; coerente con il raw che riporta solo nomi, simboli e firme |
| Conclusioni legali sulla licenza | **[proposta della sessione principale, da confermare]** (vedi sopra) |

## Deroga alla regola «solo il maintainer scrive purpose.md»

Per `.claude/agents/wiki-keeper.md` e PATTERN-capabilities.md §34.4 nessun agente scrive
`purpose.md`. Il maintainer ha deciso il 2026-11-21 che per questa factory il file lo scriva
`wiki-keeper`, a partire dalle direttive da lui dettate: è una deroga puntuale per questo
file, non un cambio permanente della regola. Il contenuto è del maintainer: `wiki-keeper` lo
ha trascritto e strutturato, il maintainer lo approva. Le modifiche successive tornano al
maintainer, salvo nuova deroga.
