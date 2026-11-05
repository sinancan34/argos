# Recorder commands

Run from any directory.

## Setup (once)

```bash
mkdir /Users/snncn/projects/sinancan34/argos/agent/recordings
```

## New recording

```bash
id="anasayfa-gtm";
instruction="Open the emlakjet.com home page. GTM container GTM-MRDH2NZ must load.";
```

```bash
cd /Users/snncn/projects/sinancan34/argos/agent && id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$instruction" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --tools "" --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output.steps > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## Feedback

```bash
id="anasayfa-gtm-3c0c9116";
instruction="Not right: ... it should be ...";
```

```bash
cd /Users/snncn/projects/sinancan34/argos/agent && claude -p "$instruction" --resume "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --tools "" --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output.steps > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## Session log

```bash
cd /Users/snncn/projects/sinancan34/argos/agent && jq -r 'select(.type=="user" or .type=="assistant") | .type as $t | (.message.content | if type=="string" then [{type:"text",text:.}] else . end)[] | if .type=="text" then "\($t): \(.text)" elif .type=="tool_use" then "\($t) → \(.name) \(.input|tojson|.[0:160])" else empty end' "recordings/$id.session.jsonl"
```
