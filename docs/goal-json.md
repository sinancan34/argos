# Goal JSON Biçimi

Goal dosyası, senaryo başarıyla bittikten sonra yakalanan network isteklerinde hangi pixel'lerin aranacağını tanımlar.

Dosya, kriterlerden oluşan bir dizidir. **Her kriter ayrı değerlendirilir ve ayrı raporlanır.** Örnekler: [goal-1.json](../scenarios/kariyer-net/goal-1.json), [goal-2.json](../scenarios/kariyer-net/goal-2.json), [goal-3.json](../scenarios/kariyer-net/goal-3.json).

```bash
env/bin/python run.py ../scenarios/kariyer-net/scenario-1.json --goal ../scenarios/kariyer-net/goal-1.json
```

## Kriter

```json
{
  "provider": {"name": "ga4", "params": []},
  "conditions": [
    {"key": "en", "match": "exact", "value": "page_view"},
    {"key": "ep.search_id", "match": "exists"}
  ]
}
```

| Alan | Zorunlu | Açıklama |
|---|---|---|
| `provider` | Evet | Hangi isteklere bakılacağı |
| `conditions` | Evet | Parametre koşulları. Hepsi AND ile bağlıdır. Boş dizi, isteğin görülmesini yeterli sayar. |

## `provider`

| `name` | `params` | Hangi istekler |
|---|---|---|
| `providers.json` içindeki ad (`ga4`, `gtm`, `meta`) | Boş `[]` | Dosyadaki URL kurallarına uyanlar |
| `custom` | Tek bir `url` koşulu | Bu koşula uyanlar |

`custom` örneği:

```json
{
  "provider": {
    "name": "custom",
    "params": [
      {"key": "url", "match": "contains", "value": "analytics.tiktok.com/api/v2/pixel"}
    ]
  },
  "conditions": []
}
```

`url` koşulunda `exists` kullanılamaz.

## Koşul

```json
{"key": "en", "match": "exact", "value": "page_view"}
```

| Alan | Zorunlu | Açıklama |
|---|---|---|
| `key` | Evet | Parametre adı, istekte göründüğü gibi (`en`, `ep.city`, `cd[buttonText]`) |
| `match` | Evet | Eşleşme tipi |
| `value` | `exists` dışında evet | Beklenen değer. Sayılar da metin olarak yazılır (`"4586649"`). `exists` ile yazılmaz. |

Parametre bir event'te birden fazla kez geçiyorsa değerlerinden birinin uyması yeterlidir.

### GA4 ürün parametreleri

GA4'ün `pr1`, `pr2` gibi birleşik ürün parametreleri nokta ile adreslenir. Bunun için ayrı bir ayar gerekmez:

```text
pr1=id4586649~nmgraphic-design-specialist~loistanbul~k0sort_score_flag~v0no
```

| `key` | Değer |
|---|---|
| `pr1` | Birleşik değerin tamamı |
| `pr1.id` | `4586649` |
| `pr1.nm` | `graphic-design-specialist` |
| `pr1.lo` | `istanbul` |
| `pr1.sort_score_flag` | `no` |

Her parçanın ilk iki karakteri alan adı, kalanı değerdir. `k0` ve `v0` gibi numaralı parçalar özel parametredir ve `k` parçasındaki adla adreslenir.

## Eşleşme tipleri

| `match` | Anlamı | Örnek |
|---|---|---|
| `exact` | Birebir aynı | `{"key": "en", "match": "exact", "value": "page_view"}` |
| `contains` | İçeriyor | `{"key": "ep.city", "match": "contains", "value": "istanbul"}` |
| `startsWith` | Bununla başlıyor | `{"key": "dl", "match": "startsWith", "value": "https://www.kariyer.net/is-ilani/"}` |
| `endsWith` | Bununla bitiyor | `{"key": "dl", "match": "endsWith", "value": "-4586649"}` |
| `regex` | Regex eşleşiyor | `{"key": "epn.item_id", "match": "regex", "value": "^\\d+$"}` |
| `exists` | Parametre var | `{"key": "ep.search_id", "match": "exists"}` |

Karşılaştırmalar büyük-küçük harf duyarlıdır. `regex`, Python `re.search` ile çalışır; ters bölü JSON içinde iki kez yazılır.

## Provider tanımları

Hazır provider'lar [runner/providers.json](../runner/providers.json) dosyasındadır. Bir URL'yi değiştirmek veya yeni provider eklemek için yalnızca bu dosya düzenlenir, kod değişmez.

```json
{
  "ga4": {
    "urls": [
      {"match": "regex", "value": "^https?://[^/]+/g/collect"},
      {"match": "startsWith", "value": "https://sgtm.example.com/events"}
    ]
  }
}
```

Bir provider'ın birden fazla URL kuralı olabilir; **kurallardan birine** uyan istek seçilir. `match` değerleri yukarıdakilerle aynıdır, yalnızca `exists` kullanılamaz. `custom` adı ayrılmıştır.

## Değerlendirme

1. Senaryonun tüm adımları başarılı olmalıdır. Bir adım başarısızsa goal'lar değerlendirilmez.
2. `stop_browser` adımından hemen önce tüm açık sekmelerin istekleri okunur. Senaryoda bu adım yoksa son adımdan sonra okunur. Goal'ların hepsi sağlanana kadar istekler yaklaşık 2 saniyede bir yeniden okunur, en fazla 60 saniye beklenir. Sağlanırsa beklemeden devam edilir. Bu bekleme yalnızca son adımdan sonra çalışır; sayfadan erken ayrılındığı veya pixel kodu hazır olmadan tıklandığı için hiç gönderilmeyen bir event'i kurtarmaz.
3. Her kriter için provider'a uyan istekler seçilir.
4. Her istek event'lere ayrılır: POST gövdesi yoksa adres parametreleri tek event'tir, gövde varsa her satır ayrı event'tir ve adres parametreleriyle birleşir. JSON'da bu ayrım yazılmaz.
5. Tüm koşulları **tek bir event** sağlıyorsa kriter geçer. Farklı event'lerdeki parametreler birleştirilmez.

**Denetlenmeyenler:**
- İsteğin yanıt durumu. Gerçek GA4 istekleri 204 aldığı halde `net::ERR_ABORTED` ile `failed` görünebiliyor.
- Base64 kodlu POST gövdesi. Bu isteklerde yalnızca adres parametreleri kullanılır.
- Event'in kaç kez gittiği ve hangi adımdan sonra gittiği.

## Sonuç

Tüm kriterler geçerse `status` `success` ve çıkış kodu 0, biri bile kalırsa `status` `fail` ve çıkış kodu 1 olur.

```json
{
  "status": "fail",
  "steps": 7,
  "recorded_requests": 258,
  "goals": [
    {
      "goal": 1,
      "status": "pass",
      "provider": {"name": "ga4", "params": []},
      "conditions": [{"key": "en", "match": "exact", "value": "page_view"}],
      "matched_events": 1,
      "url": "https://analytics.google.com/g/collect?..."
    },
    {
      "goal": 2,
      "status": "fail",
      "provider": {"name": "meta", "params": []},
      "conditions": [{"key": "ev", "match": "exact", "value": "Share"}],
      "requests": 2,
      "events": 2,
      "closest_url": "https://www.facebook.com/tr/",
      "closest": [
        {"key": "ev", "match": "exact", "expected": "Share", "actual": "PageView", "passed": false}
      ]
    }
  ]
}
```

| Alan | Açıklama |
|---|---|
| `recorded_requests` | Tüm sekmelerde kaydedilen toplam istek sayısı. `0` ise pixel değil, kayıt incelenmelidir. |
| `goal` | Kriterin dosyadaki sıra numarası |
| `matched_events`, `url` | Geçen kriterde uyan event sayısı ve ilk isteğin adresi |
| `requests`, `events` | Kalan kriterde provider'a uyan istek ve event sayısı. `requests: 0` isteğin hiç görülmediğini gösterir. |
| `closest_url`, `closest` | Kalan kriterde en çok koşulu sağlayan event ve koşul sonuçları |
| `page_requests` | Kalan kriterde sayfanın kendi kaydında (`performance`) provider'a uyan istek sayısı. `requests: 0` iken bu değer sıfırdan büyükse aracın kaydı şüphelidir. Sıfır olması kesin kanıt değildir: form ile iframe'e gönderilen Meta istekleri bu kayıtta görünmeyebilir. |
| `warnings` | Varsa okuma uyarıları (okunamayan POST gövdesi, silinmiş eski kayıtlar) |

Goal dosyası veya `providers.json` hatalıysa tarayıcı açılmadan `status: error` döner.
