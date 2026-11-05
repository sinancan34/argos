# Recorder trial runs (Layer 2)

How to turn a written test instruction into a scenario JSON with `claude -p`, give feedback on the result, and
review the session afterwards. The output is forced into
[recorder-output.schema.json](recorder-output.schema.json).

## Output schema

The root must be an object: `--json-schema` is sent to the API as a tool input schema, which refuses an array root.
The scenario itself sits in `steps`.

| Field | Content |
|---|---|
| `status` | `complete` (every step ran and its pixels were seen), `needs_input` (steps rest on assumed answers), `blocked` (the site could not be driven) |
| `questions[]` | `{question, why, assumed_answer}`: what the instruction left open. In `-p` the model cannot ask, so it assumes an answer and lists it here. |
| `assumptions[]` | Every choice the instruction did not state: observed-only values, consent handling, which list item was used, a pixel that did not fire. |
| `steps[]` | The scenario format the runner reads ([overview.md](overview.md#scenario-format)), unchanged. |

What the schema enforces:

- `action` is one of the user-behavior tools only: `browser_navigate`, `browser_navigate_back`, `browser_click`,
  `browser_hover`, `browser_type`, `browser_fill_form`, `browser_select_option`, `browser_press_key`,
  `browser_mouse_wheel`, `browser_drag`, `browser_wait_for`, `browser_tabs`, `browser_handle_dialog`.
- `params` matches that tool's input schema from the pinned catalog
  (`@playwright/mcp@0.0.84`, [tool_catalog.json](../src/argos_agent/playwright_mcp/tool_catalog.json)).
- `target`, `startTarget`, `endTarget` are never a snapshot ref (`e12`).
- `provider.name` is `ga4` or `gtm`, `params` is `[]`.
- `exists` takes no `value`; `gt` and `lt` take a number; every other match takes a non-empty string.

The schema's `description` fields also tell the model how to record (real user actions only, stable locators via
`browser_generate_locator`, criteria from the requests it saw, no `exact` on values that change per run), so no
separate system prompt is needed.

The schema was generated once from the tool catalog and has no `$schema` key: Claude Code rejects
`draft/2020-12`. When the pinned server is updated, the tool params in it must be regenerated.

## Commands

Run from `agent/`. The flags: only the pinned Playwright MCP (`--strict-mcp-config`, so the locators found behave
the same in the runner) with a visible browser, no tool but the browser (`--allowedTools mcp__playwright`), and the
output schema. Each recording is named by its session id, which the command prints first.

Once, before the first recording:

```bash
mkdir recordings
```

### Record

Replace `YOUR INSTRUCTION`:

```bash
id=$(uuidgen | tr A-Z a-z) && echo "id: $id" && claude -p "YOUR INSTRUCTION" --session-id "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" > "recordings/$id.json"
```

Writes the full `claude` output to `recordings/<id>.json`.

### Feedback

Replace `<id>` with the printed id and write the feedback. It continues that recording's session, so the model keeps
its context, and overwrites `recordings/<id>.json`:

```bash
id=<id> && claude -p "Not right: ... it should be ..." --resume "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" > "recordings/$id.json"
```

### Read the result

```bash
jq '{cost_usd: .total_cost_usd} + (.structured_output | {status, questions, assumptions})' recordings/<id>.json
```

### Extract and validate the scenario

```bash
jq '.structured_output.steps' recordings/<id>.json > recordings/<id>.scenario.json && .venv/bin/validate recordings/<id>.scenario.json
```

### Run the scenario

```bash
.venv/bin/runner recordings/<id>.scenario.json
```

## Reviewing a session

Every run is saved to `~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/<id>.jsonl`, kept for 30
days by default. It holds the instruction, every tool call with its params, the model's text between calls and each
feedback turn.

```bash
jq -r 'select(.type=="user" or .type=="assistant") | .type as $t | (.message.content | if type=="string" then [{type:"text",text:.}] else . end)[] | if .type=="text" then "\($t): \(.text)" elif .type=="tool_use" then "\($t) → \(.name) \(.input|tojson|.[0:160])" else empty end' ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/<id>.jsonl
```

Not kept: the thinking text. Thinking blocks are stored empty, and `showThinkingSummaries` applies to interactive
sessions only. The model's reasons show in `questions`, `assumptions` and its text between tool calls.

## Limits

- `--json-schema` works with `-p` only. Interactive `claude` and the desktop app have no documented way to force a
  schema; the Agent SDK has `outputFormat`.
- The model is `opus`. Trial runs on `sonnet` cost about $0.25 for an emlakjet home page recording and $0.26 to
  $0.46 for a feedback turn; `opus` costs more.
