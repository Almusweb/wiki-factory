# Check 4bi — dettaglio

Ambito: foglia di `lint-checks-kanban.md` §Check 4bi, letta solo quando serve.

`python3 tools/lint/check_tracciabilita_design.py --root .` (dentro `run-deterministic.py`). Sugli
artefatti creati da `design_traceability.required_from`: ADR `accepted` con `satisfies: [US-…]`; ID
di `satisfies`, `supersedes` e `decision_refs` esistenti; TSK `done` con almeno un `ACn` nella tabella
`## Chiusura`. Solo WARNING. Resta no-op senza un report W1 (`tools/analytics/design_w1_misure.py
--out wiki/lint/<data>-w1-design.md`) e con `required_from` non successivo alla sua data; si sospende,
dichiarandolo, se i finding superano `soglia_spegnimento`. Dopo 28 giorni senza alcun `decision_refs`
emette un INFO: è il criterio di dismissione del campo. Controlla la forma, non la pertinenza: un
`satisfies` valido può puntare alla US sbagliata. Con `design_traceability.premortem_pre_tpm: true` anche gli ADR `accepted` senza
`premortem: {data, report, esito}` valido (esito `invariato|modificato|ritirato`); a sottochiave spenta nessun effetto.
`--forza [--dal D]` misura a flag spento.

- [WARNING][adr-senza-satisfies|unknown-ref|chiusura-senza-ac|adr-senza-premortem][4bi] <ID>: <cosa manca> — <percorso>
