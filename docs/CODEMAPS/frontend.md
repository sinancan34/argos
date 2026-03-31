<!-- Generated: 2026-04-01 | Files scanned: 30 | Token estimate: ~800 -->

# Frontend (Extension) Architecture

## Page Tree (TanStack Router, hash-based)

```
/#/                              → ScenarioListPage (index.tsx)
/#/scenarios/new                 → NewScenarioPage (scenarios/new.tsx)
/#/scenarios/:scenarioId/edit    → EditScenarioPage (scenarios/$scenarioId/edit.tsx)
```

## Component Hierarchy

```
RootLayout (__root.tsx)
└── ScenarioListPage (169 lines)
    ├── TableToolbar (131 lines) — search, status filter, bulk actions
    ├── ScenarioTable (425 lines) — data grid, pagination, status toggle, actions
    └── ExecutionDialog (407 lines) — real-time step/validation progress

ScenarioForm (206 lines) — used by new + edit pages
├── StepBuilder (258 lines) — drag-drop step list (@dnd-kit)
│   └── CommandParamsFields (115 lines) — dynamic param inputs
│       └── SelectorField (78 lines) — CSS/XPath input + element picker
└── ValidationBuilder (392 lines) — URL checks + param checks per provider
```

## Entrypoints

```
entrypoints/
├── sidepanel/main.tsx     — React root, QueryClient, Router
├── background/index.ts    — Message/port listener, picker state
│   ├── orchestrator.ts    (334 lines) — Step execution loop
│   ├── network-capture.ts (41 lines)  — webRequest listener
│   └── validator.ts       (76 lines)  — URL/param matching
├── content/index.ts       — EXEC_CLICK handler, CONTENT_READY signal
└── picker.content/index.ts — Element picker overlay + selector gen
```

## Execution Messaging Protocol

```
Side Panel                 Background                Content Script
    │                          │                          │
    ├─EXECUTE_STEPS──────────▶│                          │
    │  or EXECUTE_SCENARIO     │                          │
    │                          ├─(create tab, navigate)──▶│
    │                          │◀─CONTENT_READY───────────┤
    │◀─STEP_START──────────────┤                          │
    │                          ├─EXEC_CLICK──────────────▶│
    │                          │◀─{success/error}─────────┤
    │◀─STEP_SUCCESS────────────┤                          │
    │  or STEP_ERROR           │                          │
    │                          ├─(capture network)        │
    │                          ├─(evaluate validations)   │
    │◀─EXECUTION_COMPLETE──────┤                          │
```

## State Management

| Layer | Tool | Scope |
|-------|------|-------|
| Server state | TanStack Query (retry:1, stale:30s) | Scenario CRUD |
| Form state | React Hook Form + Zod | Create/edit forms |
| UI state | React useState | Modals, selections, pagination |
| Cross-context | chrome.runtime ports + messages | Execution flow |

## Lib Modules

```
lib/api/
├── client.ts      — ky instance (prefixUrl: VITE_API_BASE_URL/api/v1)
├── scenarios.ts   — getScenarios, getScenario, createScenario, updateScenario, deleteScenario
└── errors.ts      — parseApiError() for error envelope parsing

lib/executor/
├── types.ts       — StepResult, ValidationResult, ParamCheckResult
├── matchers.ts    (109 lines) — checkUrlMatch, checkParamMatch, parseQueryParams
└── actionability.ts (159 lines) — waitForActionable (visibility → stability → click)

lib/hooks/
├── use-scenarios.ts    — TanStack Query hooks with auto-invalidation
└── use-element-picker.ts — Picker lifecycle management

lib/messaging/
├── types.ts       — Message type definitions (ExecuteSteps, StepStart, etc.)
└── protocol.ts    — connectExecutionPort() → {send, disconnect}

lib/picker/
├── types.ts              — PickerSelectorResult
├── selector-generator.ts — generateSelectors() via @medv/finder
└── picker-content-script.ts (126 lines) — Overlay + mouseover tracking

lib/schemas/scenario.ts   — Zod schemas mirroring backend Pydantic
lib/commands.ts            — COMMAND_MAP, commandValues from shared/commands.json
lib/validation-registry.ts — Field defs + Zod builders from shared/*.json
```

## UI Components (shadcn/Radix)

alert-dialog, button, checkbox, combo-input, dialog, dropdown-menu,
input, label, select, separator, switch, table, textarea
