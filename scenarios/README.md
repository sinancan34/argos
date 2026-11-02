# Senaryo JSON Biçimi

Bu belge `scenario-*.json` dosyalarını anlatır. `goal-*.json` biçimi için [docs/goal-json.md](../docs/goal-json.md).

Her dosya sırayla çalıştırılan adımlardan oluşan bir dizidir:

```json
{"action": "click_element", "params": {"selector": "a[data-test=\"ad-card-item\"]"}}
```

- `action`: Nodriver MCP komutunun adı.
- `params`: Komuta gönderilen argümanlar. Komutlar için [docs/nodriver-mcp-commands.md](../docs/nodriver-mcp-commands.md).
- Eleman yalnızca `selector` ile bulunur.
- `timeout` destekleyen her action'da zorunludur: `click_element`, `wait_for`, `send_keys`, `clear_input`, `set_value`, `select_option`, `send_file`. Değer 0 ile 60 saniye arasında olmalıdır. Bu süre elemanın aranacağı süredir, ayrıca `wait_for` eklemek gerekmez.

## Bekleme

Runner her iki adım arasında 1 ile 5 saniye arasında rastgele bekler. Ayrıca `sleep` adımı gerekmez.

Goal verilmişse `stop_browser` öncesinde pixel istekleri en fazla 60 saniye beklenir.

## Yeni sekme: `$new_tab`

`target_id` her koşuda değiştiği için JSON'a yazılamaz. Tıklamayla açılan sekme için `target_id` değeri olarak `$new_tab` kullanılır:

```json
{"action": "wait_for", "params": {"selector": "h1", "target_id": "$new_tab"}}
```

Çalıştırıcı bu değeri, `new_targets` listesi dolu dönen son `click_element` yanıtındaki ilk sekmenin `targetId` değeriyle değiştirir. Böyle bir yanıt yoksa adım başarısız sayılır.

`target_id` verilmeyen adımlar ilk sekmede çalışır.
