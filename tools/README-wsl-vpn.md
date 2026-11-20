# Raggiungere da WSL gli ambienti dietro la VPN aziendale

Guida per chi lavora nella factory da **WSL2 su Windows**: con la VPN accesa il browser di Windows apre
gli ambienti interni (test, collaudo), ma da WSL (Playwright, curl, npm, script Python) gli stessi indirizzi vanno in timeout.
La soluzione è un piccolo proxy che gira su Windows, in ascolto solo sulla macchina locale: WSL gli
passa il traffico e lui lo fa uscire dalla rete di Windows, dove la VPN funziona.

Tutto passa da un comando: `python3 tools/env/wsl_proxy.py`.

Su macOS, su Linux nativo e su Windows fuori da WSL questa guida non serve.

---

## In breve

```bash
python3 tools/env/wsl_proxy.py start             # avvia il proxy (una volta per sessione di lavoro)
python3 tools/env/wsl_proxy.py status --url https://<host-interno>/   # controlla che l'host risponda attraverso il proxy
eval "$(python3 tools/env/wsl_proxy.py env)"     # variabili per curl, npm e Chromium in questa shell

# Playwright: config locale con il proxy, accanto a quella di partenza (non va in git)
python3 tools/env/wsl_proxy.py playwright-config tests/e2e/playwright.config.staging.ts
cd tests/e2e && npx playwright test -c playwright.config.staging.proxy.local.ts

python3 tools/env/wsl_proxy.py stop              # a fine lavoro (rifiuta se qualcuno lo sta usando)
```

---

## Perché da WSL non si arriva

Tre fatti, verificati il 17/11/2026 in una factory derivata, su una postazione con un client VPN a tunnel separato
(split tunneling) attivo:

1. **Gli host interni non passano dal tunnel della VPN.** Un nome interno può risolversi in un indirizzo
   come `100.64.0.1` e, anche su Windows, la tabella di routing lo manda sul Wi-Fi, non
   sull'adattatore della VPN. Su Windows funziona lo stesso perché un componente di rete di
   Windows intercetta quel traffico e lo instrada: lo vede solo chi è un processo Windows.
2. **WSL in modalità `mirrored` condivide le interfacce di Windows, ma non quell'intercettazione.** Da WSL
   la connessione verso `100.64.0.1` esce dal router di casa e va in timeout. Anche forzare una route
   sull'interfaccia della VPN (`ip route add 100.64.0.0/10 dev eth0`) non serve: il tunnel risponde per le
   sue reti, ma `100.64.0.1` non è una di quelle.
3. **I processi Windows lanciati da WSL invece passano.** `curl.exe` di Windows, eseguito da WSL, riceve
   risposta dall'host interno. Quindi basta un processo Windows che faccia da tramite: il proxy.

Con `networkingMode=mirrored`, `127.0.0.1` è lo stesso indirizzo per Windows e per WSL: un proxy in
ascolto su `127.0.0.1` lato Windows è raggiungibile da WSL senza esporre nulla in rete.

```
WSL (Playwright, curl, npm)  ──►  127.0.0.1:18765  ──►  winproxy.py (Python di Windows)  ──►  VPN  ──►  host interni
```

---

## Prerequisiti

| Cosa | Come verificarlo | Se manca |
|---|---|---|
| WSL2 con `networkingMode=mirrored` | `%USERPROFILE%\.wslconfig`, sezione `[wsl2]` | aggiungi `networkingMode=mirrored`, poi da Windows `wsl --shutdown` e riapri WSL |
| VPN attiva su Windows | il browser di Windows apre l'host interno | collegati alla VPN |
| Python 3.8+ **installato su Windows** (non l'alias dello Store) | da WSL: `cmd.exe /c where python py` mostra un percorso fuori da `WindowsApps` | installa da python.org (vedi `tools/README-windows.md`), oppure indica il tuo con `WSL_PROXY_WINDOWS_PYTHON` |
| Python 3 in WSL | `python3 --version` | `sudo apt install python3` |
| `curl` in WSL (consigliato) | `curl --version` | senza curl la prova di `status` usa Python |

Non servono permessi di amministratore, né su Windows né in WSL (niente `sudo`), e non serve
installare pacchetti Python: il proxy usa solo la libreria standard.

---

## Uso passo passo

### 1. Avvia il proxy

```bash
python3 tools/env/wsl_proxy.py start
```

Il comando:

- trova il Python di Windows (`where python py`, scartando gli alias dello Store);
- copia `tools/env/winproxy.py` in `%TEMP%\factory-wsl-proxy\` se manca o se è cambiato;
- sceglie la porta: `18765` di default, o la prima libera fra le 20 successive (con `--port N` ne indichi
  un'altra);
- avvia il proxy come processo Windows nascosto, staccato da WSL: resta acceso anche se chiudi la shell;
- aspetta che la porta risponda e salva lo stato in `~/.local/state/factory-wsl-proxy/state.json`
  (porta, PID Windows, percorso del log).

Lanciarlo di nuovo non apre un secondo proxy: riporta quello già acceso. Ci vogliono circa 10 secondi,
quasi tutti per l'avvio di PowerShell.

### 2. Verifica

```bash
python3 tools/env/wsl_proxy.py status --url https://<host-interno>/
# proxy attivo su 127.0.0.1:18765 (pid Windows 11748); https://<host-interno>/ -> HTTP 302
```

Qualunque codice HTTP (anche 302, 401 o 404) vuol dire che l'host è raggiungibile. L'host si indica con
`--url https://...` oppure, una volta per tutte, con la variabile `WSL_PROXY_CHECK_URL`. Senza nessuno dei due la
prova si salta e il comando lo dice (`"check": "skipped"` con `--json`): il master non cabla un host, perché
dipende dalla rete di chi usa la factory. `--no-check` mostra solo lo stato.

### 3. Fai passare il traffico dal proxy

**curl, npm, Python, la maggior parte degli strumenti da riga di comando** leggono le variabili standard:

```bash
eval "$(python3 tools/env/wsl_proxy.py env)"
curl -sS -o /dev/null -w '%{http_code}\n' https://<host-interno>/
```

`env` imposta `HTTPS_PROXY`, `HTTP_PROXY` (anche in minuscolo), `NO_PROXY=localhost,127.0.0.1,::1` e
`WSL_PROXY_URL`. Se in `~/.cache/ms-playwright/syslibs/` ci sono le librerie estratte per Chromium, aggiunge
anche `LD_LIBRARY_PATH`: senza quelle, su WSL Chromium di Playwright non parte (`libnspr4.so` mancante).
Le variabili valgono solo per la shell in cui fai `eval`.

**Playwright** non legge `HTTPS_PROXY` per il browser: serve `use.proxy` nella config. Il comando la
genera per te, accanto alla config di partenza, senza toccarla:

```bash
python3 tools/env/wsl_proxy.py playwright-config tests/e2e/playwright.config.staging.ts
# -> tests/e2e/playwright.config.staging.proxy.local.ts
cd tests/e2e
npx playwright test -c playwright.config.staging.proxy.local.ts
```

La config generata importa quella di partenza e aggiunge solo il proxy (con `localhost` escluso, così i
test su `localhost:3000` continuano a funzionare). Prende l'indirizzo da `WSL_PROXY_URL` se c'è, altrimenti
dalla porta del momento in cui è stata generata. I file `*.proxy.local.ts` sono nel `.gitignore` di radice:
non finiscono nei commit. Rigenerarla è innocuo: se il contenuto è uguale il file non viene riscritto.

**Node `fetch` e altri client** che non leggono le variabili d'ambiente vanno configurati a mano con
`http://127.0.0.1:<porta>` (la porta la mostra `status`).

### 4. Ferma il proxy

```bash
python3 tools/env/wsl_proxy.py stop
```

Se il proxy ha connessioni aperte (un'altra chat o un altro terminale sta facendo un giro di test), `stop`
**non lo ferma** e lo dice, con exit 1. Aspetta che i giri finiscano. `--force` lo ferma comunque:
usalo solo se sai che nessuno lo sta usando.

Il proxy si spegne anche al riavvio di Windows o chiudendo la sessione utente: al giro successivo basta
un nuovo `start`.

---

## Più chat o più terminali insieme

Sulla stessa postazione basta **un solo proxy** per tutti: chi arriva dopo esegue `start`, trova quello
acceso e usa la stessa porta. Lo stato sta nella home WSL, quindi è condiviso fra le shell della stessa
distribuzione. Prima di fermarlo, `stop` controlla che nessuno lo stia usando.

---

## Problemi frequenti

| Sintomo | Causa probabile | Cosa fare |
|---|---|---|
| `non sei in WSL` | stai lanciando da macOS, Linux nativo o Windows | il proxy non serve: usa la rete direttamente |
| `networkingMode di WSL e' 'nat'` | WSL è in modalità NAT: `127.0.0.1` di WSL non è quello di Windows | imposta `networkingMode=mirrored` in `%USERPROFILE%\.wslconfig`, poi `wsl --shutdown` |
| `Python di Windows non trovato` | solo l'alias dello Store o nessun Python | installa Python su Windows, oppure `export WSL_PROXY_WINDOWS_PYTHON='C:\percorso\python.exe'` |
| `porta 18765 occupata: uso 18766` | un altro programma usa la porta (su alcune postazioni è occupata anche la 3128) | niente: il comando ha scelto la successiva. `env` e `status` usano la porta giusta |
| `nessuna porta libera fra ...` | 21 porte occupate di fila | `start --port 28765` |
| `il proxy ... non ascolta ... dopo 10s` | Python di Windows fallisce all'avvio | leggi il log indicato (in `%TEMP%\factory-wsl-proxy\`) |
| `status` dice `NON raggiungibile` | VPN spenta o scaduta lato Windows, oppure host sbagliato | controlla la VPN dal browser di Windows; prova `--url` con un host che conosci |
| Timeout con curl o Playwright, ma `status` va | le variabili o la config del proxy non sono in uso | `eval "$(... env)"` nella shell giusta; per Playwright usa la config `.proxy.local.ts` |
| `error while loading shared libraries: libnspr4.so` | mancano le librerie di sistema di Chromium in WSL | rifai `eval "$(... env)"` (imposta `LD_LIBRARY_PATH`), oppure installa le librerie con `sudo npx playwright install-deps chromium` |
| La copia del proxy in `%TEMP%` è stata cancellata (pulizia disco) | normale manutenzione di Windows | nessuna azione: `start` la ricopia da sé |
| `proxy in uso (N connessioni aperte)` allo stop | un altro giro sta passando dal proxy | aspetta; `--force` solo se sei sicuro |
| `timeout dopo 30s: powershell.exe ...` | Windows molto lento o PowerShell bloccato da una policy | riprova; se si ripete, segnalalo con l'output del comando |

Comandi utili per indagare:

```bash
python3 tools/env/wsl_proxy.py status --json                        # stato completo, con PID e log
cat ~/.local/state/factory-wsl-proxy/state.json                     # stato salvato
cmd.exe /c "type %TEMP%\factory-wsl-proxy\winproxy-18765.log"       # log del proxy (metodo e host, nessun contenuto)
```

---

## Limiti e sicurezza

- **Solo sulla macchina locale.** Il proxy ascolta su `127.0.0.1`: non è raggiungibile da altre postazioni
  né dalla rete di casa o dell'ufficio.
- **Non legge il traffico.** Le connessioni HTTPS passano cifrate end-to-end (metodo `CONNECT`): il proxy
  non vede URL completi, header, cookie o corpi. Nel log scrive solo metodo e host di destinazione.
- **Nessuna credenziale.** Né il comando né il proxy leggono o salvano credenziali; quelle delle utenze di
  test restano dove la factory le tiene e le usano i test, come prima.
- **Non cambia cosa puoi fare sugli ambienti.** Il proxy dà a WSL la stessa raggiungibilità di Windows, niente
  di più. Le regole della factory restano quelle di sempre: letture sugli ambienti condivisi, e qualunque
  scrittura (dati, rilasci, configurazioni) solo con il suo gate umano.
- **Non tocca la VPN.** Non avvia, non ferma e non configura il client VPN e non modifica la rete di
  Windows o di WSL.
- **Non è un servizio di sistema.** Non si avvia da solo con Windows: lo accendi quando serve e lo spegni
  a fine lavoro.
- **Non serve per tutto.** Gli host pubblici (Internet, GitHub, npm) funzionano già da WSL; il proxy li
  inoltra comunque se le variabili sono impostate, senza effetti collaterali.

---

## File

| File | Ruolo |
|---|---|
| `tools/env/wsl_proxy.py` | comando: `start`, `stop`, `status`, `env`, `playwright-config` (`--json` su tutti) |
| `tools/env/winproxy.py` | il proxy, eseguito dal Python di Windows; solo libreria standard |
| `tools/tests/test_wsl_proxy.py`, `tools/tests/test_winproxy.py` | test (`python3 -m pytest tools/tests/test_wsl_proxy.py tools/tests/test_winproxy.py`): non servono Windows né VPN |
| `.gitignore` (radice) | esclude le config generate `*.proxy.local.ts` |

Exit code del comando: `0` ok; `1` esito negativo (proxy non attivo, in uso, host non raggiungibile);
`2` errore (non WSL, Python di Windows assente, rete non `mirrored`, comando Windows in timeout).
