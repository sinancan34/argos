# Senaryo JSON Biçimi

Bu belge `scenario-*.json` dosyalarını anlatır. `goal-*.json` biçimi için [docs/goal-json.md](../docs/goal-json.md).

Her dosya sırayla çalıştırılan adımlardan oluşan bir dizidir:

```json
{"action": "click_element", "params": {"selector": "a[data-test=\"ad-card-item\"]"}}
```

- `action`: Nodriver MCP komutunun adı.
- `params`: Komuta gönderilen argümanlar. Komutlar için [docs/nodriver-mcp-commands.md](../docs/nodriver-mcp-commands.md).
- Eleman yalnızca `selector` ile bulunur.

## Yeni sekme: `$new_tab`

`target_id` her koşuda değiştiği için JSON'a yazılamaz. Tıklamayla açılan sekme için `target_id` değeri olarak `$new_tab` kullanılır:

```json
{"action": "wait_for", "params": {"selector": "h1", "target_id": "$new_tab"}}
```

Çalıştırıcı bu değeri, `new_targets` listesi dolu dönen son `click_element` yanıtındaki ilk sekmenin `targetId` değeriyle değiştirir. Böyle bir yanıt yoksa adım başarısız sayılır.

`target_id` verilmeyen adımlar ilk sekmede çalışır.
