# Argos Agent — Overview

Argos Agent runs pixel-code test scenarios against live websites and reports whether the expected tracking
requests were sent. It is not a pure agent: runs are deterministic, and an LLM steps in only to author a
scenario or to repair one that no longer runs (for example, after a CSS selector changed).

## Goals

- **Deterministic runs.** A scenario JSON is executed the same way every time, with no LLM in the loop.
- **A report per run.** Every run ends in a machine-readable report: what ran, what was sent, which success
  criteria passed or failed.
- **Self-maintenance.** When a scenario can no longer be executed, an LLM updates the scenario JSON, the JSON is
  validated again, and the run is retried.

## Principles

1. **Exact MCP, nothing invented.** Every action in a scenario is a Playwright MCP tool call: the same tool name,
   the same argument names, the same argument types. The allowed tools and arguments come from the pinned
   server's own `tools/list` response, never from a hand-written list.
2. **Real user behavior only.** Scenarios do what a user would do on the page. No reloads, extra navigations or
   page rewrites to make a run pass. If the MCP server cannot do something, the run fails honestly.
3. **The MCP server is a black box.** Problems are diagnosed from tool inputs and outputs only.
4. **Pinned server.** One `@playwright/mcp` version is pinned. Scenarios are validated against that version's
   tool catalog, and the runner parses that version's text output.
5. **Criteria are never auto-healed.** A pixel that did not fire is a finding, not a maintenance task.

## Architecture

```mermaid
flowchart LR
  I["User intent"] --> L2["Layer 2 · Recorder (LLM)"]
  L2 -- "scenario JSON" --> L3["Layer 3 · Validator"]
  L3 -- "valid" --> S[("scenarios/*.json")]
  S --> L1["Layer 1 · Runner (deterministic)"]
  L1 --> R["Run report"]
  L1 -- "action failure" --> L2
  L1 & L2 & L3 <--> M[["@playwright/mcp (stdio)"]]
```

All three layers talk to the same Playwright MCP server over stdio. Layer 1 is a Python MCP client.

### Layer 1 — Runner (deterministic)

```bash
cd agent && python3.12 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/argos-run docs/scenario-example.json --headless [--wait 10]
```

1. Load the scenario JSON and check it statically (see Layer 3). An invalid scenario fails before the browser starts.
2. Start the pinned server, adding any launch options given for the run (see [Device emulation](#device-emulation)).
3. Run each step's actions in order as `tools/call` requests, with a random 1-5 s pause before every action but
   the first, as a user would pause.
4. Collect the current tab's network requests with `browser_network_requests` (`static: true`, `all: true`), and
   read POST bodies with `browser_network_request` (`part: "request-body"`). A step's requests are those listed
   after the step began.
5. Evaluate each step's success criteria against those requests, reading them again every 2 s until all pass or
   `--wait` seconds (default 10) run out.
6. Print the run report as JSON and exit with `0` on success, `1` on a failed action or criterion, `2` on an error.

### Layer 2 — Recorder (LLM)

- **Authoring:** given a user intent (for example "search for a rental flat in Istanbul and open the first
  listing"), the LLM drives the site through the same MCP tools, then writes a scenario JSON with the actions
  it took and success criteria for the pixel requests the intent should send.
- The LLM acts on snapshot refs (`e12`) while exploring. Refs change on every run, so before writing the JSON
  each ref is turned into a stable locator with `browser_generate_locator`, for example
  `getByRole('button', { name: 'Telefonu Göster' })`, which `target` accepts as-is.
- **Repair:** given a scenario and a failed run report, the LLM revisits the page and rewrites only the failing
  `actions`.

### Layer 3 — Validator

- **Static check:** the JSON matches the scenario format; every `action` names a tool in the pinned catalog;
  every `params` object validates against that tool's `inputSchema` with no extra properties; no snapshot
  refs are used as targets; every provider is known.
- **Run check:** the scenario is run once by Layer 1 and must pass.
- **Repair guard:** a repaired scenario must keep its `success_criteria` unchanged; any criteria change needs a
  human's approval.

## Self-maintenance loop

```
Layer 1 run ──success──▶ report
     │
     ├─ criteria failure ─▶ report as a finding (no repair)
     │
     └─ action failure (element not found, strict-mode violation, timeout)
            ▶ Layer 2 repairs actions ▶ Layer 3 validates ▶ Layer 1 runs again ▶ report
```

The report names the original failure and the repair, so a human can see what changed.

## Scenario format

A scenario file is a JSON array of steps, run in order. Full example:
[scenario-example.json](scenario-example.json) (emlakjet: home page → "En Yeni" tab → first listing → phone).

```json
[
  {
    "scenario": [
      { "action": "browser_navigate", "params": { "url": "https://www.emlakjet.com/" } }
    ],
    "success_criteria": [
      {
        "provider": { "name": "gtm", "params": [] },
        "conditions": [{ "key": "id", "match": "exact", "value": "GTM-MRDH2NZ" }]
      }
    ]
  },
  {
    "scenario": [
      { "action": "browser_mouse_wheel", "params": { "deltaX": 0, "deltaY": 300 } },
      { "action": "browser_click", "params": { "target": "text=\"En Yeni\"" } }
    ],
    "success_criteria": [
      {
        "provider": { "name": "ga4", "params": [] },
        "conditions": [
          { "key": "en", "match": "exact", "value": "view_item_list" },
          { "key": "pr1.id", "match": "regex", "value": "^\\d+$" }
        ]
      }
    ]
  }
]
```

- **`scenario[]`**: the step's actions, run in order. `action` is the Playwright MCP tool name and `params` its
  arguments, sent unchanged as the `name` and `arguments` of a `tools/call` request. The runner adds, renames or
  rewrites nothing.
- **`success_criteria[]`** (optional): judged against the requests sent while the step's actions ran. A
  criterion names a provider from `argos_agent/providers.json` (`ga4` or `gtm`, `params: []`), whose `urls`
  rules pick its requests; `conditions` then check one event of those requests. Match types: `exact`,
  `contains`, `startsWith`, `endsWith`, `regex`, `exists` (no `value`), `gt`, `lt` (numeric).
- **Events** are flat `{key: value}` maps with the keys the request sends, whichever provider picked it: the URL
  query alone, or merged with each POST body line (one event per line of a batch; a body value wins over a query
  value). An item `pr1=id123~nmName~k1item_price~v15350000` becomes `pr1.id`, `pr1.nm` and `pr1.item_price`
  (`5350000`: a `v` token is read with the index of the `k` token right before it); the raw `pr1` is dropped. `ep.*` keys work as-is. Every condition of a criterion must hold in the same event.

### Element targets

Every element param (`target`, `startTarget`, `endTarget`, `fields[].target`) is a single string. What the
pinned server accepts, checked by a black-box probe on a local page:

| Value | Accepted | Behavior |
|---|---|---|
| CSS, `:has()`, selector lists | yes | `aside[aria-label="İlan Sahibi"] button:has(.ee-icon-phone)` |
| `text="En Yeni"` | yes | exact text match |
| `text=En Yeni` | yes | case-insensitive substring; also matches "En Yeni İlanlar" |
| `… >> visible=true >> nth=0` | yes | first element a user can see; `>> nth=0` alone can pick a hidden copy and time out |
| `getByRole('button', { name: 'Telefonu Göster' })` | yes | the form `browser_generate_locator` returns |
| snapshot ref (`e12`) | yes, but not allowed | refs change on every run |
| `{"selector": …}` object or a list of candidates | no | not a string; rejected by the tool schema |

- A target must match exactly one element. Playwright runs in strict mode, so two matches fail the action.
- Use `>> visible=true >> nth=0` only when the step means "the first of a list" (the first listing, `pr1.lp = 1`).
- No fallback candidates. When a target stops matching, the self-maintenance loop replaces it.

### Device emulation

Device emulation is not part of the scenario file. Playwright MCP emulates devices through launch flags, not
tools, so a mobile run passes `--device` (or `--viewport-size` and `--user-agent`) to the runner, which hands it to
the server unchanged.

## Run report

A JSON object with:

- `status`: `success` (every action ran and every criterion passed), `fail` (an action or a criterion failed),
  or `error` (the scenario is invalid or the server could not be reached).
- For an action failure: the step and action number, the tool call as sent, and the server's error. A failed
  action ends the run; a failed criterion does not.
- For each criterion: `pass` with the matching request's `url`, its `body` (the whole batch, `null` for a request
  without one) and `checks`, the value each condition saw; or `fail` with `closest_url`, `closest_body` and
  `closest`, the event that met the most conditions and which ones it missed.
- Warnings, for example a POST body that could not be read.

## MCP server

- Package: `@playwright/mcp@0.0.84`, started with `npx` over stdio.
- The server itself is the source of truth. The tool catalog (`argos_agent/playwright_mcp/tool_catalog.json`)
  holds every tool of the pinned server with its `tools/list` input schema (72 tools, every capability on), and
  every launch option its `--help` lists (52 options). A param the server fills in with a default may be left
  out, as the server allows. Every tool, param and option in it can be called; anything else is refused before
  it is sent, since the server would reject it.
- [playwright.dev/mcp](https://playwright.dev/mcp/introduction) is a helper reference; where it and the server
  differ, the server wins.
- Fixed launch options, used unless a run gives the same flag: `--isolated` (in-memory profile, discarded after
  the run), `--caps=network,storage,testing,vision,pdf,devtools,config` (every tool callable), `--codegen=none`,
  `--output-max-size`.
- `python -m argos_agent.playwright_mcp.refresh` regenerates the catalog from the server; run it whenever the
  pinned version changes.

## Out of scope

- Whether the vendor received the hit, and the client's analytics data quality.
- Staging environments, self-signed certificates, region or proxy testing. Scenarios target live production
  sites and run unattended on a schedule.
- Changes to, or diagnosis inside, the MCP server.

## Roadmap

| Phase | Deliverable |
|---|---|
| 0 | This document |
| 1 | Layer 1 Runner: MCP client, tool catalog, scenario check, network capture, criteria, report |
| 2 | Layer 3 Validator: static check CLI, run check, repair guard |
| 3 | Layer 2 Recorder: authoring from intent, repair from a failed report, self-maintenance loop |
