# Step Execution Engine — Design Spec

## Context

Argos has a complete scenario CRUD system with step builder UI, but no ability to actually execute steps in a browser tab. This spec defines the execution engine that opens a new tab and runs steps (goto, click) sequentially, reporting results back to the side panel in real-time.

## Requirements

1. **Two execution modes:**
   - **Step Test** — triggered during scenario create/edit to test individual steps. Returns per-step success/error.
   - **Scenario Run** — runs all steps end-to-end. Returns per-step results (validation execution deferred to a future phase).

2. **Triggering:** Side panel UI sends execution request via port-based messaging.
3. **Tab lifecycle:** A new tab is opened for execution and stays open after completion.
4. **Error handling:** Execution stops at first failure, reports which step failed and why.
5. **Results storage:** Frontend-only (no backend persistence in this phase).
6. **Command scope:** Only `goto` and `click` commands.

## Architecture

**Background-Orchestrated** — three-layer separation:

```
Side Panel (UI + trigger)
  ↕ chrome.runtime.connect (port)
Background Service Worker (orchestrator)
  ↕ chrome.tabs.sendMessage / chrome.tabs API
Content Script (DOM executor)
```

### Manifest Changes

```json
{
  "permissions": ["sidePanel", "activeTab", "tabs", "scripting", "webNavigation"],
  "host_permissions": ["<all_urls>"]
}
```

Note: `webNavigation` is required for `chrome.webNavigation.onCompleted` used in goto navigation.

## Messaging Protocol

### Side Panel → Background

| Message | Payload | Purpose |
|---------|---------|---------|
| `EXECUTE_STEPS` | `{ steps: Step[], stepTimeout: number }` | Step test mode |
| `EXECUTE_SCENARIO` | `{ steps: Step[], validations: Validation[], stepTimeout: number, validationTimeout: number }` | Full scenario run |

### Background → Side Panel (via port)

| Message | Payload | Purpose |
|---------|---------|---------|
| `STEP_START` | `{ stepId, stepIndex }` | Step is about to execute |
| `STEP_SUCCESS` | `{ stepId, stepIndex, duration }` | Step completed |
| `STEP_ERROR` | `{ stepId, stepIndex, error, duration }` | Step failed |
| `EXECUTION_COMPLETE` | `{ mode, success, stepResults[] }` | All done |

### Background → Content Script

| Message | Payload | Purpose |
|---------|---------|---------|
| `EXEC_CLICK` | `{ selectors: SelectorEntry[] }` | Click element using fallback selectors |

### Content Script → Background (response)

Returned via `sendResponse` callback of `chrome.runtime.onMessage`:

| Response | Payload |
|----------|---------|
| Click result | `{ success: boolean, error?: string }` |

## Step Params Shape

The `click` command stores its params as:

```typescript
// step.params for "click" command
{ selector: SelectorEntry[] }

// where SelectorEntry is:
{ strategy: "css" | "xpath" | "linkText", value: string }
```

The orchestrator extracts `step.params.selector` and passes it as the `selectors` field in `EXEC_CLICK`.

## Execution Flow

### Orchestrator (Background)

```
1. Receive EXECUTE_STEPS or EXECUTE_SCENARIO from port
2. Create new tab: chrome.tabs.create({ url: "about:blank", active: true })
3. Listen for chrome.tabs.onRemoved to detect tab closure
4. For each step in order:
   a. Send STEP_START to side panel via port
   b. Determine effective timeout: step.timeout ?? stepTimeout
   c. Execute command:
      - "goto": chrome.tabs.update(tabId, { url })
               → wait for chrome.webNavigation.onCompleted (frameId === 0 only)
               → after navigation, inject content script via chrome.scripting.executeScript
               → wait for CONTENT_READY response before proceeding
      - "click": chrome.tabs.sendMessage(tabId, EXEC_CLICK) → wait for response
   d. On success: send STEP_SUCCESS via port
   e. On error/timeout: send STEP_ERROR → send EXECUTION_COMPLETE(success: false) → stop
4. All steps passed → send EXECUTION_COMPLETE(success: true)
```

### Timeout & Cancellation

Each step runs within a `Promise.race([stepExecution, timeoutPromise])`:
- If timeout fires first → cancel any pending `webNavigation` listener, resolve as error
- If tab is closed (`chrome.tabs.onRemoved`) → immediately resolve as error: "Execution tab was closed"
- If port disconnects (side panel closed) → abort execution silently, clean up listeners

### DOM Executor (Content Script)

```
1. Register chrome.runtime.onMessage listener
2. Send CONTENT_READY response when listener is registered
3. On EXEC_CLICK message:
   a. For each selector in selectors[] (fallback order):
      - css: document.querySelector(value)
      - xpath: document.evaluate(value, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null)
      - linkText: find <a> elements, match textContent
   b. If found → element.click() → sendResponse({ success: true })
   c. No selector matched → sendResponse({ success: false, error: "No element found for any selector" })
```

### goto Navigation

Background handles `goto` entirely — no content script needed for navigation:

1. `chrome.tabs.update(tabId, { url })` — navigates the tab
2. Wait for `chrome.webNavigation.onCompleted` with matching `tabId` AND `frameId === 0` (main frame only, ignoring iframe navigations)
3. After main frame navigation completes, inject content script via `chrome.scripting.executeScript({ target: { tabId }, files: ["content-scripts/content.js"] })`
4. Wait for `CONTENT_READY` message from injected content script before proceeding to next step

### Content Script Injection Strategy

**Programmatic injection only** — the existing static content script declaration (`matches: ["<all_urls>"]`) in `content/index.ts` will be removed. Instead:

- Content script is injected via `chrome.scripting.executeScript` after each `goto` navigation completes
- This ensures a fresh script instance on each new page
- The script registers a `chrome.runtime.onMessage` listener and sends a `CONTENT_READY` acknowledgment
- The orchestrator waits for `CONTENT_READY` before sending any `EXEC_CLICK` messages (eliminates race condition)

## Result Types

```typescript
interface StepResult {
  stepId: string;
  command: string;
  status: "success" | "error";
  duration: number; // ms
  error?: string;
}

interface StepTestResult {
  mode: "step-test";
  success: boolean;
  stepResults: StepResult[];
}

interface ScenarioRunResult {
  mode: "scenario-run";
  success: boolean;
  stepResults: StepResult[];
  // validationResults: deferred to future phase
}

type ExecutionResult = StepTestResult | ScenarioRunResult;
```

## File Structure

```
extension/src/
├── lib/
│   ├── messaging/
│   │   ├── types.ts          # All message types (type-safe discriminated unions)
│   │   └── protocol.ts       # Port connect/send helpers for side panel usage
│   └── executor/
│       └── types.ts          # ExecutionResult, StepResult, StepTestResult, ScenarioRunResult
├── entrypoints/
│   ├── background/
│   │   ├── index.ts          # Existing + port connection listener dispatching to orchestrator
│   │   └── orchestrator.ts   # Step execution orchestrator logic
│   └── content/
│       └── index.ts          # DOM executor (click handler, element finder) — programmatic injection only
```

## Key Decisions

- **Port-based messaging** (`chrome.runtime.connect`) between side panel and background for real-time progress
- **One-shot messaging** (`chrome.tabs.sendMessage` / `chrome.runtime.onMessage`) between background and content script
- **Programmatic content script injection** via `chrome.scripting.executeScript` after each `goto` — removes static `matches` declaration
- **Content readiness handshake** — content script sends `CONTENT_READY` after injection, orchestrator waits before sending commands
- **Main frame filter** — `webNavigation.onCompleted` filtered by `frameId === 0`
- **Per-step timeout** — `step.timeout` overrides `stepTimeout` when defined
- **Fallback selector support** — tries selectors in order, first match wins
- **Tab closure detection** — `chrome.tabs.onRemoved` listener aborts execution
- **Port disconnect handling** — `port.onDisconnect` silently aborts execution
- **No validation execution** in this phase — only step execution

## Out of Scope

- Validation execution (dataLayer checks, etc.)
- Backend persistence of execution results (TestRun/TestRunResult)
- New commands beyond goto/click
- Side panel execution UI (progress indicators, result display)
- Automatic tab closing
