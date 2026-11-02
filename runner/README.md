# Runner

Senaryo JSON dosyasını [nodriver MCP](../docs/nodriver-mcp-commands.md) üzerinden sırayla çalıştırır. JSON biçimi için [scenarios/README.md](../scenarios/README.md).

## Kurulum

```bash
cd runner
python3.12 -m venv env
env/bin/pip install -r requirements.txt
```

## Çalıştırma

Nodriver MCP sunucusu ayrı başlatılmış olmalıdır.

```bash
env/bin/python run.py ../scenarios/kariyer-net/scenario-1.json
```

Sunucu başka bir adresteyse:

```bash
env/bin/python run.py ../scenarios/kariyer-net/scenario-1.json --mcp-url http://127.0.0.1:8011/mcp
```

Senaryo başarılı olduğunda pixel kontrolü yapmak için goal dosyası verilir. Biçim ve sonuç için [docs/goal-json.md](../docs/goal-json.md).

```bash
env/bin/python run.py ../scenarios/kariyer-net/scenario-1.json --goal ../scenarios/kariyer-net/goal-1.json
```

## Sonuç

Sonuç stdout'a JSON olarak yazılır.

| Durum | `status` | Çıkış kodu |
|---|---|---|
| Tüm adımlar başarılı | `success` | 0 |
| Bir adım başarısız | `fail` | 1 |
| Dosya okunamadı, biçim hatalı veya sunucuya ulaşılamadı | `error` | 1 |

Başarılı:

```json
{"status": "success", "steps": 8}
```

Adım hatası:

```json
{
  "status": "fail",
  "step": 7,
  "action": "wait_for",
  "params": {"selector": "button[data-test=\"share-button\"]", "target_id": "$new_tab"},
  "response": {"status": "fail", "data": {"selector": "time ran out while waiting for ..."}}
}
```

`response`, MCP sunucusunun yanıtıdır. Hata sonrası kalan adımlar çalışmaz ve `stop_browser` çağrılır. Tarayıcı kapatılamazsa sonuca `cleanup` alanı eklenir.

## Test

```bash
env/bin/python -m pytest
```
