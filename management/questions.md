---
created: 2026-11-20
updated: 2026-11-20
status: open
---

# Questions — wiki-factory

## [APERTE]

### Q_004 — Dati per misurare dimensioni e crescita degli archivi
**Origine:** [[llm-wiki-archivi-persistenza]]
**Tipo:** Requisito incompleto
**Impatto:** BASSO
**Bloccante:** soft
**Domanda:** su quali progetti si misurano dimensioni e crescita degli archivi? I dati reali del cliente sono utilizzabili, con quale autorizzazione, oppure serve un progetto sintetico?
**Epiche bloccate:** EP-002
**Storie bloccate:** US-018
[^src: wiki/gaps.md §2026-11-20 17:06 — llm-wiki-archivi-dimensioni]

---

### Q_005 — Quale ruolo Sync scrive i report di verifica di EP-004 in `raw/`
**Origine:** [[llm-wiki-rischi-persistenza]]
**Tipo:** Requisito incompleto
**Impatto:** MEDIO
**Bloccante:** soft
**Domanda:** l'utente ha deciso (2026-11-20 17:53) che il report di ogni verifica di EP-004 va scritto come raw in `raw/` da un ruolo Sync dedicato, da definire, e poi ingerito da `wiki-keeper`. Quale ruolo Sync scrive i report di verifica di EP-004 in `raw/`: un nuovo sub-agent o l'estensione di uno esistente? Con quali strumenti (senza Bash e per sola lettura del codice, come da Q_003)? Quale naming dei file e quale voce di manifest? Lo stesso canale vale per la sintesi di US-033?
**Epiche bloccate:** EP-004
**Storie bloccate:** US-025, US-026, US-027, US-028, US-029, US-030, US-031, US-032, US-033
[^src: wiki/concepts/llm-wiki-rischi-persistenza.md §Contesto]

---

## [CHIUSE]

### Q_001 — Canale e destinatario della segnalazione al master, e dove conservare l'esito
**Origine:** [[master-difetti-rilevati]]
**Tipo:** Requisito incompleto
**Impatto:** MEDIO
**Bloccante:** soft
**Domanda:** come si segnalano al master i difetti (issue, pull request, documento condiviso, altro) e a chi? Dove si conserva in questa factory la copia dell'esito di ogni segnalazione, in modo che il `wiki-keeper` possa ingerirla?
**Epiche bloccate:** EP-001
**Storie bloccate:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012
**Data risoluzione:** 2026-11-20 17:36
**Risposto da:** l'utente
**Decisione:** documento locale. Per ogni difetto si produce un report nella factory, in `deliverables/`, e la segnalazione al master la fa l'utente con il canale che preferisce. L'esito si conserva come documento nella factory.
**Epiche/Storie sbloccate:** EP-001; US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012 (`pending_clarification` svuotato, criteri di accettazione adeguati)
[^src: wiki/concepts/master-difetti-rilevati.md §Contesto]

---

### Q_002 — Perimetro dei «dettagli del cliente» da escludere dalle segnalazioni
**Origine:** [[factory-decisioni-di-configurazione]]
**Tipo:** Requisito incompleto
**Impatto:** MEDIO
**Bloccante:** soft
**Domanda:** l'utente chiede segnalazioni senza dettagli del cliente. Rientrano nei dettagli da escludere: il nome del progetto e del repository di codice, i percorsi, gli hash dei commit, i nomi utente, il nome di questa factory? Le riproduzioni si fanno solo su un caso neutro minimo?
**Epiche bloccate:** EP-001
**Storie bloccate:** US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012
**Data risoluzione:** 2026-11-20 17:36
**Risposto da:** l'utente
**Decisione:** va escluso tutto. Nessun nome o URL del repository di codice, nessun percorso, hash, nome utente né il nome di questa factory. Si riproduce sempre su un caso neutro, con factory o fixture neutra.
**Epiche/Storie sbloccate:** EP-001; US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010, US-011, US-012 (`pending_clarification` svuotato, criteri di accettazione adeguati)
**Addendum (2026-11-20 17:53, risposta dell'utente):** percorsi. Nei report di EP-001 sono ammessi i percorsi dei file del master oggetto del difetto; restano esclusi quelli della factory e del repository di codice. Conferma dell'interpretazione del product-manager, che precisa e non sostituisce la risposta del 2026-11-20 17:36.
[^src: wiki/concepts/factory-decisioni-di-configurazione.md §Politica sul repository di codice]

---

### Q_003 — Metodo di verifica ammesso per i rischi di persistenza
**Origine:** [[llm-wiki-rischi-persistenza]]
**Tipo:** Requisito incompleto
**Impatto:** ALTO
**Bloccante:** soft
**Domanda:** i rischi in wiki sono deduzioni dal codice letto. Oltre alla lettura completa del codice, quali metodi di verifica sono ammessi: osservare l'applicazione in esecuzione su un progetto di prova non del cliente; scrivere test di caratterizzazione nel repository del cliente (che è già un intervento sul codice); tenere eventuali test fuori dal repository del cliente? Quale ambiente di esecuzione è disponibile?
**Epiche bloccate:** EP-004
**Storie bloccate:** US-025, US-026, US-027, US-028, US-029, US-030, US-031, US-032
**Data risoluzione:** 2026-11-20 17:36
**Risposto da:** l'utente
**Decisione:** solo lettura del codice. Niente osservazione dell'app in esecuzione, niente test di caratterizzazione, nessuna modifica al repository del cliente.
**Epiche/Storie sbloccate:** EP-004; US-025, US-026, US-027, US-028, US-029, US-030, US-031, US-032 (`pending_clarification` svuotato; criteri riscritti come analisi statica; esito «non conclusivo» ammesso quando la sola lettura non basta)
[^src: wiki/concepts/llm-wiki-rischi-persistenza.md §Contesto]

---
