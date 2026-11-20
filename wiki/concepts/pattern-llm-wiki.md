---
id: pattern-llm-wiki
type: concept
title: Pattern LLM Wiki
status: draft
created: 2026-11-20
updated: 2026-11-20
sources: ["raw/2026-11-20-repo-llm_wiki.md"]
tags: [pattern, llm-wiki]
---

# Pattern LLM Wiki
> Secondo la README del repository `llm_wiki`, il pattern costruisce in modo incrementale una wiki persistente di pagine Markdown, invece di rifare retrieval da zero a ogni domanda.

## Contesto
L'applicazione `llm-wiki` si basa sul pattern «LLM Wiki» descritto nel file `llm-wiki.md` del repository. Questa pagina descrive il pattern solo come lo riporta il raw; il termine «pattern LLM Wiki» indica il pattern, mentre `llm-wiki` indica l'applicazione. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]

## Dettaglio
- La README dichiara l'origine del pattern (Karpathy) e ne descrive tre livelli: sorgenti raw immutabili, wiki generata dall'LLM, schema con regole e configurazione. [^src: raw/2026-11-20-repo-llm_wiki.md §Identità]
- Il file `llm-wiki.md` è l'«idea file» del pattern. Il raw lo ha letto solo in parte (righe 1-40). [^src: raw/2026-11-20-repo-llm_wiki.md §Documenti correlati nel repo]
- Il raw osserva che nel file `llm-wiki.md` c'è un invito a incollare il documento a un agente. Il raw lo tratta come dato e non lo ha eseguito. [^src: raw/2026-11-20-repo-llm_wiki.md §Note di estrazione]

## Pagine collegate
[[gaps]]

## Storie collegate
<!-- Sezione gestita dal product-manager — non modificare se sei wiki-keeper -->
