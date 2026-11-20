# Come si legge il costo: store, operatore ed etichetta di affidabilita'

Questo documento spiega che cosa misurano i due contatori di costo del toolkit, perche'
danno numeri diversi e come leggere l'esito di `cost_alert.py reconcile`. Non contiene
campioni: i valori vanno letti sul proprio ambiente.

## Cosa misura lo store

Lo store (`analytics/events/*.jsonl`) contiene gli eventi che il collettore
(`harvest-session-tokens.py`) scrive quando si esegue un harvest: un evento per sessione,
modello e ambito (principale o subagente), con i token cumulati per voce (input, output,
lettura dalla cache, scrittura in cache, di cui a un'ora). Il costo dello store e' la somma
di quegli eventi a listino (`analytics/pricing.yaml`). Lo stesso task registrato piu' volte
con totali cumulati si conta una volta sola: si sommano le differenze tra un evento e il
precedente.

Lo store e' quindi **quanto e' stato raccolto**, non quanto e' stato consumato.

## Cosa misura il contatore dell'operatore

I transcript di Claude Code (`~/.claude/projects/<cartella>/`, sessione principale piu'
`subagents/`) sono scritti da Claude Code a ogni risposta, per ogni cartella di lavoro. Il
conteggio dell'operatore somma i token di tutte le cartelle sotto la radice indicata con
`--transcripts-root` (default `~/.claude/projects`), una risposta per `message.id`, e li
prezza a listino: la scrittura in cache si prezza come (`cache_write` - parte a 1h) alla
tariffa a 5 minuti piu' la parte a 1h alla tariffa a 1h.

Il contatore dell'operatore e' **quanto e' stato consumato su questa macchina**, dalla
persona che la usa.

## Perche' i due numeri differiscono

- **Sessioni senza harvest.** Lo store si popola solo con un harvest esplicito: il lavoro non
  raccolto non c'e'. E' la causa normale di una differenza.
- **Subagenti.** Il lavoro dei subagenti entra nello store solo se l'harvest li legge; su
  alcune versioni di Claude Code l'output dei subagenti risulta sottostimato nei transcript
  stessi. Per questo una versione non verificata rende il confronto `non verificabile`.
- **Cache.** Le letture dalla cache sono la voce piu' grande in token e la meno costosa per
  token; chi confronta con un contatore esterno deve sapere se quel contatore le include.
  `reconcile` riporta lo scarto sia con sia senza le letture dalla cache.
- **Cartelle.** I transcript sono per cartella di avvio: worktree e cloni hanno cartelle
  proprie. Il confronto usa le cartelle della factory (progetto corrente, suoi checkout e
  worktree) piu' quelle attribuite dagli alias di configurazione (sotto); il totale su tutte le
  cartelle e' riportato a parte.
- **Transcript ripuliti e altre macchine.** Claude Code ripulisce i transcript vecchi; lo
  store puo' contenere eventi di altre macchine. Nessuno dei due casi e' visibile da qui.

## Come leggere `reconcile`

```
cost_alert.py reconcile [--period session|daily|weekly|monthly] [--transcripts-root <dir>] [--json]
```

Mostra, per il periodo: il costo dell'operatore su tutte le cartelle, quello attribuito alla
factory, il costo dello store, lo scarto con e senza letture dalla cache (positivo = lo store
sta sotto l'operatore) e l'etichetta.

| Etichetta | Significato |
|---|---|
| `affidabile` | lo store sta sotto l'operatore di non piu' della soglia (anche sopra: per esempio perche' contiene altre macchine) |
| `sottostima` | lo store sta sotto l'operatore di piu' della soglia: il costo dello store e' un minimo, non un totale |
| `non verificabile` | manca il termine di confronto: nessun transcript leggibile nella finestra, listino non caricato, versione di Claude Code non verificata, nessun consumo attribuito alla factory |

L'etichetta si decide sul confronto a listino pieno, perche' lo store prezza anche le
letture dalla cache; lo scarto senza cache e' informativo. `check` e `breakdown` riportano la
stessa etichetta, quando e' calcolabile, senza cambiare il loro esito. Accanto a ogni consuntivo
si riporta l'etichetta: un costo `sottostima` non si usa come totale.

## La soglia di sottostima

`analytics.reconcile.underestimate_threshold` in `factory.config.yaml` (default `0.05`: 5%).
**Il valore e' provvisorio e va confermato dopo due settimane di misura**: finche' non e'
confermato, un `affidabile` al limite della soglia va letto con cautela. Se la chiave manca si
usa il default; un valore fuori da 0-1 si scarta con un avviso.

## Gli alias delle cartelle

`analytics.reconcile.worktree_aliases` e' una lista di espressioni regolari sui **nomi delle
cartelle dei transcript**. Una cartella il cui nome corrisponde si attribuisce alla factory,
oltre a quelle riconosciute dal progetto e dai suoi worktree. Serve quando un clone o un
worktree vive in un percorso che il nome della factory non lascia indovinare. Default: lista
vuota (nessun alias); le espressioni non valide si scartano con un avviso.
