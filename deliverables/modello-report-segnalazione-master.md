---
tipo: modello
stato: bozza
us: US-012
tsk: TSK-001
creato: 2026-11-20
---

# Modello di report per segnalare un difetto del master

Questo documento definisce il modello unico con cui si descrive un difetto del meta-framework
(il master) e il vocabolario con cui se ne registra l'esito. Ogni storia di difetto
(US-001..US-011, e US-034) produce un report che segue questo modello e non ne cambia la
struttura.

## 1. Che cos'è un report

- Il report è un documento in `deliverables/`, un file per difetto. Nome:
  `deliverables/segnalazione-master-<NN>-<slug>.md`, con `<NN>` il numero del difetto nella
  wiki (`master-difetti-rilevati`).
- Il report è la **copia conservata dell'esito**. Il `wiki-keeper` lo può ingerire.
- La **segnalazione al master la fa l'utente**, con il canale che preferisce, partendo dal
  report. Questa factory non apre issue né pull request sul master.
- Il report **descrive e non corregge**. Un workaround locale si cita come workaround, mai
  come correzione proposta.
- Il frontmatter del report è tracciamento interno: non fa parte del testo da inviare.

## 2. Vocabolario di esito

Ogni report dichiara uno e un solo esito. L'esito si sceglie dall'evidenza, non dalla
convinzione di chi scrive.

| Esito | Significato | Cosa conta come evidenza |
|---|---|---|
| **confermato** | Il difetto si riproduce sul caso neutro, alla versione del master indicata. | Il comando eseguito sul caso neutro e il suo esito (exit code, righe di output pertinenti) che mostrano il sintomo. Se il difetto è una lacuna di un documento del master, la ricerca eseguita sul file del master e il suo risultato. |
| **smentito** | Sul caso neutro, alla versione del master indicata, il comportamento è quello atteso. | Il comando eseguito e il suo esito che mostrano il comportamento atteso. Vale per la versione indicata: se il difetto è stato corretto a monte, lo si scrive. |
| **non conclusivo** | Non si è potuto né riprodurre né escludere il difetto. | Che cosa è stato eseguito, con l'esito, e perché non decide (caso neutro non costruibile, ambiente non disponibile, esito ambiguo). |

Regola di evidenza: **un'affermazione sull'ambiente senza il comando eseguito e il suo
esito è un'ipotesi**, anche se è scritta come una certezza. Un'ipotesi non può dichiarare
«confermato» né «smentito»: al massimo porta a «non conclusivo».

## 3. Caso neutro, ambiente e versione del master

- **Caso neutro.** La riproduzione avviene sempre su un caso neutro: una factory creata
  apposta dall'installer del master, oppure una fixture minima. Il report dice come
  costruirlo con i soli comandi del master, così il master può ripeterlo. Non si riproduce
  mai su una factory o su un repository di un cliente.
- **Ambiente in termini neutri.** Famiglia e versione del sistema operativo, shell, codifica
  della console, versioni di Python e di git, e le variabili d'ambiente che contano per il
  difetto. Niente nomi utente né percorsi locali: si usano segnaposto come `<home>`,
  `<factory-neutra>`, `<master>`.
- **Versione del master verificata.** È sempre indicata, con la data della verifica: il
  difetto potrebbe essere già corretto a monte. Si indica come tag di release o versione
  del PATTERN (`pattern_version`). Prima di consegnare il report all'utente, si ripete la
  verifica sulla versione più recente del master disponibile in locale e si riportano
  entrambe le versioni se differiscono.

## 4. Dettagli esclusi e percorsi ammessi

Dal testo del report sono esclusi, per categoria:

1. nome o URL del repository di codice;
2. percorsi della factory e del repository di codice, e ogni altro percorso locale assoluto;
3. hash di commit;
4. nomi utente (utente del sistema, autore git, contributor);
5. nome di questa factory.

Sono **ammessi** i percorsi dei file del master che sono oggetto del difetto (per esempio lo
strumento che fallisce o il protocollo con la lacuna), scritti relativi alla radice del
master.

**L'elenco dei valori concreti da cercare non si scrive in nessun file versionato.** Sta in
un file locale non versionato: fuori dal repository, oppure in un percorso escluso da git,
controllato prima dell'uso con `git check-ignore -v <file-valori>` (exit 0 = escluso).

## 5. Verifica finale

Prima di consegnare il report all'utente, si eseguono due ricerche sul report e se ne
riporta l'esito nella sezione «Verifica dei dettagli esclusi». **Si riportano i comandi
con i segnaposto e gli exit code, mai i valori.**

1. Valori esclusi, dal file locale:
   `grep -n -i -F -f <file-valori> <report>` → atteso exit 1 (nessuna occorrenza).
2. Forme generiche (percorsi assoluti e stringhe esadecimali da 7 a 40 caratteri):
   `grep -n -E '[A-Za-z]:[\\/]|/home/|/Users/|\b[0-9a-f]{7,40}\b' <report>` → atteso exit 1;
   un'occorrenza si controlla a mano e, se è un dettaglio escluso, si toglie.

Con un'occorrenza nei valori esclusi il report non si consegna finché non è corretta.

## 6. Modello da copiare

```markdown
---
tipo: segnalazione-master
difetto: <NN>
us: <US-NNN>
tsk: <TSK-NNN>
esito: confermato | smentito | non conclusivo
versione_master: <tag o pattern_version>
verificato_il: <AAAA-MM-GG>
consegnato_all_utente: <AAAA-MM-GG o vuoto>
---

# <Titolo breve del difetto>

## Sintomo
<Che cosa succede, osservato. Una o due frasi.>

## Comportamento atteso
<Che cosa dovrebbe succedere, e dove il master lo dichiara, se lo dichiara.>

## File del master coinvolti
- `<percorso relativo alla radice del master>`

## Ambiente
- Sistema operativo: <famiglia e versione>
- Shell e codifica della console: <...>
- Python / git: <versioni>
- Variabili d'ambiente rilevanti: <nome=valore, solo se contano per il difetto>

## Versione del master verificata
<tag o pattern_version>, verificata il <AAAA-MM-GG>.
<Se rieseguita sulla versione più recente: versione ed esito.>

## Caso neutro
<Come costruirlo con i soli comandi del master.>

## Passi di riproduzione
1. <comando>
2. <comando>

## Evidenza
| Comando | Esito |
|---|---|
| `<comando eseguito>` | <exit code e righe di output pertinenti> |

## Esito
**<confermato | smentito | non conclusivo>**: <perché, con rimando alle righe di Evidenza.>

## Proposta di gravità
**<alta | media | bassa>**: <motivo>. È una proposta: la gravità la decide il master.
- alta: blocca un flusso del framework e non c'è workaround;
- media: il flusso funziona con un workaround, o una funzione è degradata;
- bassa: documentazione, messaggi o casi marginali.

## Workaround locale
<Se esiste: che cosa si fa in locale per aggirare il difetto. Non è una correzione proposta.
Altrimenti: «nessuno».>

## Verifica dei dettagli esclusi
| Ricerca | Comando | Esito |
|---|---|---|
| Valori esclusi | `grep -n -i -F -f <file-valori> <report>` | exit <N>, <K> occorrenze |
| Forme generiche | `grep -n -E '<pattern della sezione 5>' <report>` | exit <N>, <K> occorrenze controllate |
| File valori non versionato | `git check-ignore -v <file-valori>` oppure «fuori dal repository» | <esito> |
```

## 7. Verifica di questo modello

Eseguita su questo file prima della consegna. Esiti nella sezione `## Chiusura` di TSK-001.
