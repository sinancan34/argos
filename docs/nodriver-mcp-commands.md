# Nodriver MCP Komutları

Bu belge `nodriver-mcp` sunucusunun sunduğu 27 komutu ve tüm parametrelerini anlatır.

**Kaynak:** Yalnızca çalışan kod kullanıldı (`mcp-servers/nodriver/src/nodriver_mcp/` ve kurulu `nodriver==0.50.3`). Docstring'ler ve yorumlar okunmadan önce AST ile ayıklandı. Kod dışında kalan davranışlar, yani Chrome'un bir CDP komutuna nasıl yanıt verdiği, bu belgenin kapsamında değildir.

## Sunucu

| Ayar | Varsayılan | Açıklama |
|---|---|---|
| Taşıma | `http` | Kodda sabit, adres `http://<host>:<port>/mcp` |
| `NODRIVER_MCP_HOST` | `127.0.0.1` | Boş değer varsayılana döner |
| `NODRIVER_MCP_PORT` | `8000` | Sayı değilse veya 0-65535 dışındaysa sunucu başlamaz |
| `NODRIVER_MCP_NETWORK_CAPTURE` | `1` | `0` ise network kaydı kapanır |

Sağlık kontrolü: `GET /health`.

## Ortak kurallar

### Yanıt biçimi

| `status` | Alanlar | Ne zaman |
|---|---|---|
| `success` | `data` | Komut tamamlandı |
| `fail` | `data` (hatalı alan → mesaj) | Çağıranın verdiği değer veya durum sorunlu |
| `error` | `message`, varsa `code` ve `data` | Beklenmeyen hata |

Tüm komutlarda ortak yanıtlar:

| Durum | Yanıt |
|---|---|
| Tarayıcı açık değil (`start_browser` hariç) | `fail`, anahtar `browser` |
| Şemaya uymayan argüman | `fail`, anahtar `arguments` |
| Sunucu yaşam döngüsü çalışmamış | `error`, kod `lifespan_missing` |
| Beklenmeyen hata | `error`, kod `<komut>_failed` (`start_browser` ve `stop_browser` kendi kodlarını kullanır) |

### Süre sınırı

Her komutun sunucu tarafında 60 saniyelik süre sınırı vardır. `start_browser` için bu süre 120 saniyedir.

Bir tarayıcı işlemi başka komutlarla aynı kilidi kullanır. Bu nedenle komutlar sırayla çalışır.

### Ortak parametre: `target_id`

| Tip | Varsayılan | Açıklama |
|---|---|---|
| `string \| null` | `null` | İşlem yapılacak sekmenin Chrome `targetId` değeri. `null` ise ilk `page` hedefi kullanılır. |

Eşleşen sekme yoksa `fail`, anahtar `target_id` döner. `list_tabs`, `navigate` ve `stop_browser` dışındaki tüm tarayıcı komutlarında bulunur. Değer her koşuda değiştiği için aşağıdaki tablolarda tekrar yazılmadı.

### Ortak parametreler: eleman bulma

`click_element`, `send_keys`, `clear_input`, `set_value`, `select_option` ve `send_file` bu parametreleri kullanır:

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `selector` | `string \| null` | `null` | CSS selector. Eşleşen ilk eleman alınır. |
| `text` | `string \| null` | `null` | Metne göre arama. `send_keys` komutunda adı `find_text`. |
| `uid` | `integer \| null` | `null` | Chrome `backendNodeId` değeri. Doğrudan çözülür, arama ve bekleme yapılmaz. |
| `best_match` | `boolean` | `true` | Yalnızca metin aramasında. `true` ise uzunluğu aranan metne en yakın eleman, `false` ise ilk eleman alınır. |
| `return_enclosing_element` | `boolean` | `true` | Yalnızca metin aramasına iletilir, ama nodriver içinde kullanılmaz. Etkisi yoktur. |
| `timeout` | `number` | `10` | Elemanın aranacağı süre (saniye). `uid` için geçerli değildir. |

**Tam olarak bir tane** eleman bulucu verilmelidir (`selector`, `text` veya `uid`). Aksi halde `fail` döner.

**`timeout` nasıl çalışır:** Yanıt bekleme süresi değildir. Eleman bulunana kadar DOM yaklaşık 0,5 saniyede bir sorgulanır. Bulunursa işlem hemen yapılır. Süre dolarsa `fail` döner: `no element matched within <timeout>s`.

Bu komutlar başarılı olduğunda `target` ve `node` döndürür. `node`, Chrome'un eleman için verdiği `DOM.Node` nesnesidir.

### Dosya yazma: `filename`

`get_content`, `evaluate_javascript`, `take_snapshot`, `query_ax_tree` ve `list_network_requests` komutlarında bulunur.

Verilirse sonuç sunucunun çalıştığı makinede bu yola UTF-8 olarak yazılır ve yanıtta içerik yerine `path` döner. Üst dizinler oluşturulur, var olan dosyanın üzerine yazılır. Yazılamazsa `fail`, anahtar `filename` döner.

---

## Tarayıcı

### `start_browser`

Chrome'u `nodriver.start()` ile başlatır ve tüm açık sekmelerde network kaydını açar.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `user_data_dir` | `string \| null` | `null` | Chrome profil dizini |
| `headless` | `boolean` | `false` | Pencere olmadan çalıştırır |
| `browser_executable_path` | `string \| null` | `null` | Chrome çalıştırılabilir dosyasının yolu |

**Yanıt:** `pid`, `host`, `port`, `headless`, `user_data_dir`, `uses_custom_data_dir`, `browser_executable_path`, `websocket_url`, `info`.

**Hatalar:**
- Tarayıcı zaten açıksa `fail`, anahtar `browser`.
- Verilen yolda Chrome bulunamazsa `fail`, anahtar `browser_executable_path`.
- Yol verilmemişse ve Chrome bulunamazsa `error`, kod `browser_not_found`.
- Diğer hatalarda `error`, kod `browser_start_failed`.

### `stop_browser`

Tarayıcıyı kapatır ve en fazla 10 saniye kapanmasını bekler. Parametresi yoktur.

**Tüm network kayıtları silinir.** Kayıtlar gerekiyorsa bu komuttan önce okunmalıdır.

**Yanıt:** Kapatılan tarayıcının `start_browser` ile aynı alanları.

**Hatalar:** `error`, kod `browser_stop_failed` veya `browser_stop_timeout`.

---

## Gezinme

### `navigate`

Bir adrese gider ve açık sekmelerde network kaydını açar.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `url` | `string` | `chrome://welcome` | Gidilecek adres |
| `new_tab` | `boolean` | `false` | Yeni sekmede açar |
| `new_window` | `boolean` | `false` | Yeni pencerede açar |

**Yanıt:** `target`.

**Dikkat:**
- `Page.navigate` yanıtındaki `errorText` kod tarafından atılır. Adres yüklenemese bile bu alan yüzünden `fail` dönmez.
- `Browser.get` içinde sayfa yükleme olayı bekleyen bir çağrı yoktur. Sonraki adım için `wait_for` kullanılmalıdır.
- `new_tab` veya `new_window` kullanılsa bile `target_id` verilmeyen sonraki komutlar ilk `page` hedefinde çalışır.

### `back`

`window.history.back()` çalıştırır. Önce sekmenin network kaydını açar.

**Yanıt:** `target`. Komut, geçmişte gidilecek sayfa olup olmadığını denetlemez.

### `forward`

`window.history.forward()` çalıştırır. Önce sekmenin network kaydını açar.

**Yanıt:** `target`. Komut, geçmişte gidilecek sayfa olup olmadığını denetlemez.

### `reload`

`Page.reload` gönderir. Önce sekmenin network kaydını açar.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `ignore_cache` | `boolean \| null` | `true` | Önbelleği yok sayar |
| `script_to_evaluate_on_load` | `string \| null` | `null` | `Page.reload` komutuna iletilen JavaScript |

**Yanıt:** `target`.

---

## Eleman işlemleri

Bu bölümdeki komutların eleman bulma parametreleri yukarıda anlatılmıştır.

### `click_element`

Elemanın konumu alınabilirse o noktayı kısa süre işaretler, ardından JavaScript ile `el.click()` çağırır (`user_gesture=true`). Gerçek fare olayı göndermez.

| Ek parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `include_children` | `boolean` | `true` | `false` ise yanıttaki `node` içinden `children` çıkarılır |

**Yanıt:** `target`, `node`, `new_targets`. `new_targets`, tıklamadan sonra listede yeni görünen sekmelerdir.

`node` tıklamadan önce alınır.

### `send_keys`

Elemana `focus()` çağırır, ardından metnin her karakteri için ayrı bir `char` tipi tuş olayı gönderir. Metni sonuna ekler, var olan değeri silmez. Yalnızca `char` olayı gönderdiği için Enter gibi adlandırılmış tuş olayı üretmez.

| Ek parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `text` | `string` | Zorunlu | Yazılacak metin |
| `find_text` | `string \| null` | `null` | Metne göre eleman bulucu (diğer komutlardaki `text`) |

**Yanıt:** `target`, `node`.

### `clear_input`

JavaScript ile `element.value = ""` atar. `input` veya `change` olayı göndermez.

**Yanıt:** `target`, `node`.

### `set_value`

Elemanın `value` özelliğine değeri atar ve son değeri okur.

| Ek parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `value` | `string` | Zorunlu | Yazılacak değer |
| `dispatch_events` | `boolean` | `false` | `true` ise değer prototipteki `value` setter'ı ile yazılır ve baloncuklanan `input` ile `change` olayları gönderilir |

**Yanıt:** `target`, `node`, `value`.

### `select_option`

Eleman `OPTION` ise `selected = true` yapar ve baloncuklanan `change` olayı gönderir.

**Dikkat:** Eleman `OPTION` değilse hiçbir şey yapmaz ve yine `success` döner. Selector `<select>` elemanını değil `<option>` elemanını göstermelidir.

**Yanıt:** `target`, `node`. Etkili olup olmadığı `node.nodeName` değerinden anlaşılır.

### `send_file`

`DOM.setFileInputFiles` ile dosya input'una dosya yollarını verir.

| Ek parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `file_paths` | `string[]` | Zorunlu | Dosya yolları. Kod varlıklarını denetlemez. |

**Yanıt:** `target`, `node`.

---

## Bekleme

### `wait_for`

Eleman bulunana kadar yaklaşık 0,5 saniyede bir sorgular.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `selector` | `string \| null` | `null` | CSS selector |
| `text` | `string \| null` | `null` | Metne göre arama, ilk eşleşme alınır |
| `timeout` | `number` | `10` | Bekleme süresi (saniye) |
| `include_children` | `boolean` | `true` | `false` ise yanıttaki `node` içinden `children` çıkarılır |

**Tam olarak bir tane** eleman bulucu verilmelidir (`selector` veya `text`). `uid` desteklenmez.

**Yanıt:** `target`, `node`. Süre dolarsa `fail`, anahtar `selector` veya `text`.

### `sleep`

Belirtilen süre bekler ve aynı anda sekme listesini yeniler.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `t` | `number` | `1` | Bekleme süresi (saniye) |

**Yanıt:** `target`.

---

## Sayfa okuma

### `get_content`

Belgenin tamamının HTML'ini (`outerHTML`) okur.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `filename` | `string \| null` | `null` | Sonucu dosyaya yazar |

**Yanıt:** `target`, `length` ve `content` ya da `path`.

### `evaluate_javascript`

Sayfa bağlamında tek bir JavaScript ifadesi çalıştırır (`user_gesture=true`, `allow_unsafe_eval_blocked_by_csp=true`).

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `expression` | `string` | Zorunlu | Çalıştırılacak ifade |
| `await_promise` | `boolean` | `false` | Dönen promise'in sonucunu bekler |
| `return_by_value` | `boolean` | `false` | Sonucu `value` biçiminde ister |
| `filename` | `string \| null` | `null` | Sonucu JSON olarak dosyaya yazar |

**Yanıt:** `target`, `shape`, `length` ve `result` ya da `path`.

| `shape` | Anlamı |
|---|---|
| `tree` | Chrome'un derin serileştirilmiş değeri (varsayılan) |
| `value` | `return_by_value=true` ile dönen düz değer |
| `wrapper` | Çözülemeyen veya boş değerde tüm `RemoteObject` |

`return_by_value=true` iken `0`, `false`, `""` gibi yanlış değerler düz değer olarak değil `wrapper` olarak döner.

JavaScript hatası `fail`, anahtar `expression` olarak döner.

### `take_snapshot`

Erişilebilirlik ağacının tamamını alır ve her düğümü `uid=<id> <rol> "<ad>" <özellikler>` satırı olarak yazar.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `verbose` | `boolean` | `false` | `true` ise tüm düğümler filtrelenmeden yazılır |
| `depth` | `integer \| null` | `null` | Chrome'a iletilen en fazla derinlik |
| `frame_id` | `string \| null` | `null` | Okunacak frame |
| `filename` | `string \| null` | `null` | Sonucu dosyaya yazar |

Varsayılan filtre yok sayılan, gizli, adsız `none`/`generic`/`presentation`, `InlineTextBox` ve `LineBreak` düğümlerini çıkarır. Ayrıca üst düğümünün adıyla aynı olan `StaticText` satırlarını da atlar.

**Yanıt:** `target`, `node_count`, `dropped` ve `snapshot` ya da `path`. `dropped`, yazılmayan düğüm sayısıdır.

### `query_ax_tree`

Erişilebilirlik ağacında role veya ada göre arama yapar. Çağrı sırasında `Accessibility` alanını açar ve sonra kapatır.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `role` | `string \| null` | `null` | Aranacak rol |
| `accessible_name` | `string \| null` | `null` | Aranacak erişilebilir ad |
| `uid` | `integer \| null` | `null` | Aramanın kökü. `null` ise belgenin tamamı. |
| `filename` | `string \| null` | `null` | Sonucu dosyaya yazar |

**Yanıt:** `target`, `node_count` ve `matches` ya da `path`.

### `take_screenshot`

Önce 1 saniye bekler, ardından ekran görüntüsü alır.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `filename` | `string \| null` | `auto` | Kayıt yolu. `auto` veya boş ise ad, sekmenin adresi ve tarihten üretilir. |
| `format` | `jpeg \| png \| jpg \| null` | `jpeg` | Görüntü biçimi |
| `full_page` | `boolean \| null` | `false` | `true` ise görünür alanın dışını da yakalar |
| `as_base64` | `boolean \| null` | `false` | `true` ise dosyaya yazmaz, görüntüyü yanıtta döndürür |

**Yanıt:** `target` ve `path`. `as_base64=true` ise `target` ve `mime_type`; görüntü ayrı bir içerik bloğu olarak gelir.

---

## Network

Kayıt her sekme için ayrı tutulur. Sekme başına en fazla 5000 istek saklanır, aşılırsa en eskisi silinir. POST gövdesi kayda en fazla 65536 bayt olarak alınır.

### `list_network_requests`

Kaydedilen istekleri eskiden yeniye listeler.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `resource_types` | `string[] \| null` | `null` | Yalnızca bu türler. Tam eşleşme, büyük-küçük harf duyarlı. |
| `url` | `string \| null` | `null` | Adres bu metni içermeli. Büyük-küçük harf duyarsız düz metin araması. |
| `limit` | `integer \| null` | `null` | En yeni N kayıt. `null` ve dosya yoksa 100. `null` ve dosya varsa tümü. `0` boş liste. Negatifse `fail`. |
| `url_max_length` | `integer \| null` | `200` | Yanıttaki adresleri kısaltır. `null` ise kısaltmaz. Dosyaya yazılan kayıtları etkilemez. Negatifse `fail`. |
| `filename` | `string \| null` | `null` | Sonucu JSON olarak dosyaya yazar |

`resource_types` değerleri: `Document`, `Stylesheet`, `Image`, `Media`, `Font`, `Script`, `TextTrack`, `XHR`, `Fetch`, `Prefetch`, `EventSource`, `WebSocket`, `Manifest`, `SignedExchange`, `Ping`, `CSPViolationReport`, `Preflight`, `FedCM`, `Other`.

**Yanıt:** `target`, `request_count`, `matched_count`, `total_count`, `dropped` ve `requests` ile `url_truncated` ya da `path`.

Her kayıt: `requestId`, `method`, `url`, `resourceType`, `status`, `mimeType`, `state` (`pending`, `finished`, `failed`), `hasPostData`.

### `get_network_request`

Tek bir isteğin ayrıntılarını okur.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `request_id` | `string` | Zorunlu | `list_network_requests` yanıtındaki `requestId` |
| `include_response_body` | `boolean` | `false` | Yanıt gövdesini `response_body` olarak ekler |
| `include_record` | `boolean` | `true` | Tüm kaydı `record` olarak ekler |

**Yanıt:** `target`, listedeki kayıt alanları, `post_data` ve seçime göre `response_body` ile `record`. POST gövdesi yoksa `post_data` değeri `null` olur.

**Hatalar:** Kayıt yoksa `fail`, anahtar `request_id`. Yanıt gövdesi alınamazsa `fail`, anahtar `include_response_body`.

---

## Sekme ve pencere

### `list_tabs`

Sekme listesini yenileyip döndürür. Parametresi yoktur.

**Yanıt:** `tabs`.

### `close_tab`

Sekmeyi kapatır ve kapanan sekmelerin network kayıtlarını siler. Yalnızca `target_id` alır.

**Yanıt:** Kapatılan sekmenin `target` bilgisi.

### `activate`

Sekmeyi `Target.activateTarget` ile öne getirir. Yalnızca `target_id` alır.

**Yanıt:** `target`.

### `get_window`

Sekmenin penceresini okur. Yalnızca `target_id` alır.

**Yanıt:** `target`, `windowId`, `bounds`.

### `set_window_state`

Pencere durumunu değiştirir.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `state` | `normal \| minimized \| maximized \| fullscreen` | `normal` | Yeni durum |

**Dikkat:** Kod her çağrıda boyutu değiştirir. `normal` için pencereyi `(0, 0)` konumunda 1280×720 yapar. Diğer durumlarda önce bu sıfırlamayı yapar, sonra durumu uygular.

**Yanıt:** `target`.

### `set_window_size`

Pencereyi `normal` durumda taşır ve boyutlandırır.

| Parametre | Tip | Varsayılan | Açıklama |
|---|---|---|---|
| `left` | `integer` | `0` | Soldan piksel |
| `top` | `integer` | `0` | Üstten piksel |
| `width` | `integer` | `1280` | Genişlik |
| `height` | `integer` | `1024` | Yükseklik |

**Yanıt:** `target`. Gerçek boyut yanıtta yoktur, `get_window` ile okunur.

---

## Sunucuda olmayan işlemler

Sunucuda bu işlemler için komut yoktur:

- Hover ve gerçek fare hareketi
- Scroll
- Adlandırılmış tuş gönderme (Enter, Tab, ok tuşları)
- Mobil cihaz, user agent veya touch emülasyonu
