#!/usr/bin/env bash
# =============================================================================
# capture_screenshot.sh — deterministic tool capture_screenshot (EP-008, ADR-063 §D)

# =============================================================================
#
# Part of the UX/UI Review capability (EP-008), aligned to the pattern

# [[thin-agents-fat-skills-refactor]]: this is the TOOL (deterministic logic, no LLM).

# The `screenshot-capture-protocol` skill and the `ux-ui-reviewer` agent call it

# to collect real visual evidence — this file DOES NOT judge: it just outputs pure JSON.

#
# Backing executable for the `capture_screenshot` tool declared in `ux-ui-reviewer.md`.

# Resolves root cause #1 of ADR-063 §Context (tool_uses: 0 from no backing

# executable). Fail-loud on missing dependencies: no silent degradation (ADR-063 §A).

#
# ADR refs: ADR-063 §D (backing eseguibile), ADR-063 §A (fail-loud),
#           ADR-008 (Playwright via Bash, no MCP).
# Wiki: wiki/concepts/ux-ui-review-capability.md  [[ux-ui-review-capability]]
#
# -----------------------------------------------------------------------------
# INPUT CONTRACT (CLI)

#   --target <string>              URL http/https | percorso file
#   --viewports <string>           viewport da catturare, csv (default "desktop,mobile")
#                                  recognized values: desktop (1280x800), mobile (375x812),

#                                  tablet (768x1024), custom WxH (es. "1440x900")
#   --out <dir> output directory (default: current directory)
#   --stable-ms <int>              finestra di stabilita' (ms): la pagina e' "stabile" quando
#                                  altezza del documento, lunghezza del testo e numero di nodi
#                                  non cambiano per questo tempo (default 1000)
#   --settle-timeout <int>         tetto massimo (ms) dell'attesa di stabilita' per viewport,
#                                  oltre il quale si scatta comunque (default 10000)

#
# OUTPUT CONTRACT (stdout, pure JSON)

#   { target, stabile, screenshots:[{viewport, width, height, path, stabile, attesa_ms, motivo?}] }
#   Prima di scattare: load + networkidle (best effort) + stabilita' del DOM (vedi sopra).
#   `stabile: true`  -> la pagina e' rimasta ferma per --stable-ms prima dello scatto.
#   `stabile: false` -> scatto su timeout (--settle-timeout): `motivo` dice perche'. Lo screenshot
#                       puo' essere NON idratato: chi giudica deve dichiararlo, non ignorarlo.
#   `stabile` di primo livello = AND di tutti i viewport. Campi aggiunti: i consumer esistenti
#   (che leggono viewport/width/height/path) non si rompono.
#
# EXIT CODES
#   0 captures completed

#   1 technical error (missing prerequisite, target not reachable, etc.)

# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# 1. CLI argument parsing
# ---------------------------------------------------------------------------
TARGET=""
VIEWPORTS="desktop,mobile"
OUT_DIR="."
STABLE_MS="1000"
SETTLE_TIMEOUT="10000"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"; shift 2 ;;
    --viewports)
      VIEWPORTS="${2:-desktop,mobile}"; shift 2 ;;
    --out)
      OUT_DIR="${2:-.}"; shift 2 ;;
    --stable-ms)
      STABLE_MS="${2:-1000}"; shift 2 ;;
    --settle-timeout)
      SETTLE_TIMEOUT="${2:-10000}"; shift 2 ;;
    *)
      echo "ERRORE: argomento sconosciuto '$1'. Uso: capture_screenshot.sh --target <url|path> [--viewports desktop,mobile] [--out <dir>] [--stable-ms N] [--settle-timeout N]" >&2
      exit 1 ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "ERRORE: --target è obbligatorio. Uso: capture_screenshot.sh --target <url|path> [--viewports desktop,mobile] [--out <dir>] [--stable-ms N] [--settle-timeout N]" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Check prerequisites — fail-loud, no silent degradation (ADR-063 §A+§D)

# ---------------------------------------------------------------------------
if ! command -v node &>/dev/null; then
  echo "Tool capture_screenshot richiede Node.js: non trovato." >&2
  echo "Installare Node.js (https://nodejs.org) e riprovare. (ADR-063 §D)" >&2
  exit 1
fi

if ! npx playwright --version >/dev/null 2>&1; then
  echo "Tool capture_screenshot richiede Playwright: non trovato o non configurato." >&2
  echo "Eseguire: npm i -D @playwright/test && npx playwright install chromium" >&2
  echo "Verificare la disponibilità dei tool / l'ambiente di render (ADR-063 §D)." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# 3. Creating output directory

# ---------------------------------------------------------------------------
mkdir -p "$OUT_DIR"

# ---------------------------------------------------------------------------
# 4. Capture multi-viewport screenshot via Playwright (Node inline snippet)

#    Mappa viewport presets → dimensioni; supporta formato custom WxH.
#    Output: Pure JSON with array screenshots.
# ---------------------------------------------------------------------------
TARGET="$TARGET" VIEWPORTS="$VIEWPORTS" OUT_DIR="$OUT_DIR" STABLE_MS="$STABLE_MS" SETTLE_TIMEOUT="$SETTLE_TIMEOUT" node <<'NODE'
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const target = process.env.TARGET;
const viewportsStr = process.env.VIEWPORTS || 'desktop,mobile';
const outDir = path.resolve(process.env.OUT_DIR || '.');

// Preset viewport → { width, height }
const VIEWPORT_PRESETS = {
  desktop: { width: 1280, height: 800 },
  mobile:  { width: 375,  height: 812 },
  tablet:  { width: 768,  height: 1024 },
};

function parseViewport(v) {
  if (VIEWPORT_PRESETS[v]) return { name: v, ...VIEWPORT_PRESETS[v] };
  // Custom WxH
  const m = v.match(/^(\d+)x(\d+)$/);
  if (m) return { name: v, width: parseInt(m[1], 10), height: parseInt(m[2], 10) };
  process.stderr.write('ERRORE: viewport non riconosciuto: ' + v + '. Valori accettati: desktop, mobile, tablet, WxH (es. 1440x900)\n');
  process.exit(1);
}

function toUrl(t) {
  if (/^https?:\/\//i.test(t)) return t;
  return 'file://' + path.resolve(t);
}

function safeName(s) {
  return s.replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 40);
}

const stableMs = parseInt(process.env.STABLE_MS, 10);
const settleTimeout = parseInt(process.env.SETTLE_TIMEOUT, 10);
if (!(stableMs >= 0) || !(settleTimeout > 0)) {
  process.stderr.write('ERRORE: --stable-ms deve essere >= 0 e --settle-timeout > 0 (interi, ms)\n');
  process.exit(1);
}

// Attende che la pagina sia ferma: la firma (altezza, lunghezza testo, numero nodi) non cambia
// per stableMs. Soglia fissa evitata: una pagina che idrata in 4 s e una in 400 ms funzionano
// entrambe. Su timeout NON fallisce: ritorna stabile=false con la ragione.
async function waitStable(page) {
  const t0 = Date.now();
  let motivo = null;
  try {
    await page.waitForLoadState('networkidle', { timeout: Math.min(settleTimeout, 15000) });
  } catch (_) {
    motivo = 'networkidle non raggiunto entro il timeout';
  }
  const sig = () => page.evaluate(() => {
    const d = document;
    return [
      Math.max(d.documentElement.scrollHeight, d.body ? d.body.scrollHeight : 0),
      d.body ? d.body.innerText.length : 0,
      d.getElementsByTagName('*').length,
    ].join('|');
  });
  let last = await sig();
  let since = Date.now();
  while (true) {
    const now = Date.now();
    if (now - since >= stableMs) {
      return { stabile: motivo === null, attesa_ms: now - t0, motivo: motivo || undefined };
    }
    if (now - t0 >= settleTimeout) {
      return { stabile: false, attesa_ms: now - t0,
               motivo: (motivo ? motivo + '; ' : '') + 'pagina ancora in cambiamento allo scadere di ' + settleTimeout + ' ms (screenshot potenzialmente non idratato)' };
    }
    await page.waitForTimeout(200);
    const cur = await sig();
    if (cur !== last) { last = cur; since = Date.now(); }
  }
}

const viewports = viewportsStr.split(',').map(v => v.trim()).filter(Boolean).map(parseViewport);

(async () => {
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const screenshots = [];

    for (const vp of viewports) {
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
      });
      const page = await context.newPage();
      await page.goto(toUrl(target), { waitUntil: 'load', timeout: 30000 });

      const st = await waitStable(page);

      const ts = Date.now();
      const filename = `screenshot_${safeName(vp.name)}_${ts}.png`;
      const filepath = path.join(outDir, filename);
      await page.screenshot({ path: filepath, fullPage: true });
      await context.close();

      screenshots.push({
        viewport: vp.name,
        width: vp.width,
        height: vp.height,
        path: filepath,
        stabile: st.stabile,
        attesa_ms: st.attesa_ms,
        ...(st.motivo ? { motivo: st.motivo } : {}),
      });
    }

    const result = { target, stabile: screenshots.every(x => x.stabile), screenshots };
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    await browser.close();
    process.exit(0);
  } catch (err) {
    if (browser) { try { await browser.close(); } catch (_) {} }
    process.stderr.write('ERRORE tecnico durante la cattura screenshot: ' + (err && err.message ? err.message : String(err)) + '\n');
    process.exit(1);
  }
})();
NODE
