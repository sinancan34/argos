# Recorder commands

Run in `agent/`.

## Setup (once)

```bash
mkdir recordings
```

## New recording

```bash
id="anasayfa-gtm"
prompt="Open the emlakjet.com home page. GTM container GTM-MRDH2NZ must load."
```

```bash
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" > "recordings/$id.json"
```

## Feedback

```bash
id="anasayfa-gtm-3c0c9116"
prompt="Not right: ... it should be ..."
```

```bash
sid=$(jq -er .session_id "recordings/$id.json") && claude -p "$prompt" --resume "$sid" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" > "recordings/$id.json"
```

## Session log

```bash
jq -r 'select(.type=="user" or .type=="assistant") | .type as $t | (.message.content | if type=="string" then [{type:"text",text:.}] else . end)[] | if .type=="text" then "\($t): \(.text)" elif .type=="tool_use" then "\($t) → \(.name) \(.input|tojson|.[0:160])" else empty end' ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/"$(jq -r .session_id "recordings/$id.json")".jsonl
```
