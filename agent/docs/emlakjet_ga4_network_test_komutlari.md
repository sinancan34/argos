# Emlakjet GA4 Network Test Komutları

## AS-01

```markdown
id="AS-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-02

```markdown
id="AS-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Son aramalar alanındaki bir aramaya tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_widget
- widget: 'son-aramalar||<LABEL>' biçiminde. LABEL: Kullanıcının son aramalar kısmında arama yaptığında gönderilmelidir. Boşluk yerine \"-\" kullanılmalıdır. Örn: \"satilik-daire\" \"kiralik-daire\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-03

```markdown
id="AS-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Şehirleri Keşfedin alanındaki bir şehre tıkla (ör. büyükşehirler > istanbul).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_widget
- widget: 'sehirleri-kesfedin||<LABEL>' biçiminde. LABEL: Tıklanan içerik bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Üst ve alt kategori arasında 2 tane uzun çizgi \"|\" yer almalıdır. Örn: \"buyuksehirler||istanbul\" \"sahil-sehirleri||balikesir\" \"populer-lokasyonlar||kadikoy\" Tüm Şehirleri Gör butonuna tıklandıysa \"tum-sehirleri-gor\" değeri beslenmelidir.
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-04

```markdown
id="AS-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Akıllı Emlak Deneyimi alanındaki bir kutuya tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_widget
- widget: 'akilli-emlak-deneyimi||<LABEL>' biçiminde. LABEL: Tıklanan kutu bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örn: \"yapay-zeka-ile-arama\" \"deger-ve-yatirim-raporu\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-05

```markdown
id="AS-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Gayrimenkul Kararlarınızı Güçlendirin alanındaki bir kutuya tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_widget
- widget: 'gayrimenkul-kararlarinizi-guclendirin||<LABEL>' biçiminde. LABEL: Tıklanan kutu bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örn: \"emlak-degeri\" \"danisman-bul\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-06

```markdown
id="AS-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Uzman Rehberlerimizle Evinizi Bulun alanındaki bir kutuya tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_widget
- widget: 'uzman-rehberlerimizle-evinizi-bulun||<LABEL>' biçiminde. LABEL: Tıklanan kutu bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örn: \"satin-alma-rehberi\" \"satis-rehberi\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-07

```markdown
id="AS-07";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan ilanlar bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: İlanın fiyat bilgisi gönderilmelidir.
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki pozisyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" Arsa için \"arsa\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name: 'anasayfa/one-cikan/<TAB_TURU>' biçiminde. TAB_TURU: Kullanıcının ilanı görüntülediği tab bilgisi gönderilmelidir. Örn: \"en-yeni\" , \"yatirim-potansiyeli\", \"fiyati-dusen-satilik\", \"geri-donus-suresi\", \"kira-geliri\"
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-08

```markdown
id="AS-08";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan ilanlar bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Tıklanılan ilanın fiyat bilgisi
  - item_id: Kullanıcının tıkladığı ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının tıkladığı ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının tıkladığı ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Tıklanılan ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Tıklanılan ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Tıklanılan ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Tıklanılan ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Tıklanılan ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Tıklanılan ilanın bulunduğu modülün id bilgisi
  - item_list_name: 'anasayfa/one-cikan/<TAB_TURU>' biçiminde. TAB_TURU: Kullanıcının ilanı görüntülediği tab bilgisi gönderilmelidir. Örn: \"en-yeni\" , \"yatirim-potansiyeli\", \"fiyati-dusen-satilik\", \"geri-donus-suresi\", \"kira-geliri\"
  - item_variant: Tıklanılan ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Tıklanılan ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-09

```markdown
id="AS-09";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan ilanlar içindeki Projeler sekmesi bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü Projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Projenin fiyat bilgisi gönderilmelidir.
  - item_id: Kullanıcının gördüğü Projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü Projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü Projenin o modüldeki pozisyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen Projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen Proje için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen Projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen Projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen Projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen Projenin bulunduğu modülün id bilgisi
  - item_list_name = anasayfa/one-cikan/projeler
  - item_variant: Görüntülenen Projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen Projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-10

```markdown
id="AS-10";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan ilanlar içindeki Projeler sekmesi bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Tıklanılan ilanın fiyat bilgisi
  - item_id: Kullanıcının tıkladığı ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının tıkladığı ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının tıkladığı ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Tıklanılan ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Tıklanılan ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Tıklanılan ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Tıklanılan ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Tıklanılan ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Tıklanılan ilanın bulunduğu modülün id bilgisi
  - item_list_name = anasayfa/one-cikan/projeler
  - item_variant: Tıklanılan ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Tıklanılan ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-11

```markdown
id="AS-11";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan danışmanlar bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının gördüğü danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü danışmanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü danışmanın o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Görüntülenen danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen danışmanın mahalle bilgisi. Örn: \"kazim-karabekir\"
  - item_list_id: Görüntülenen danışmanın bulunduğu modülün id bilgisi
  - item_list_name = anasayfa/one-cikan-danismanlar
  - location_id: Görüntülenen danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-12

```markdown
id="AS-12";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan danışmanlar bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Danışmanın ortalama satış fiyatı bilgisi gönderilmelidir.
  - item_id: Kullanıcının tıkladığı danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının tıkladığı danışmanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının tıkladığı danışmanın o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Tıklanılan danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Tıklanılan danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Tıklanılan danışmanın mahalle bilgisi. Örn: \"abdi-ipekci\"
  - item_list_id: Tıklanılan danışmanın bulunduğu modülün id bilgisi
  - item_list_name = anasayfa/one-cikan-danismanlar
  - location_id: Tıklanılan ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-13

```markdown
id="AS-13";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan bir ilan veya danışman kartında 'Telefonu Göster' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ana-sayfa

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = ana-sayfa
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand: \"ilan\" , \"danisman\" ya da \"proje\" seçeneklerinden hangisinde işlem yapıldıysa o bilgi gelmelidir.
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name: Kullanıcının telefonu göster butonuna tıkladığı modül bilgisi gönderilmelidir. Örn: \"one-cikan-danismanlar\" ya da \"one-cikan-ilanlar/en-yeni\", \"one-cikan-ilanlar/firsat\", \"one-cikan-ilanlar/fiyati-dusen-kiralik\", \"one-cikan-ilanlar/fiyati-dusen-satilik\", \"one-cikan-ilanlar/yatirim-skoru-yuksek\", \"one-cikan-ilanlar/projeler\"
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-14

```markdown
id="AS-14";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Öne çıkan bir kartta numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ana-sayfa

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand: \"ilan\" , \"danisman\" ya da \"proje\" seçeneklerinden hangisinde işlem yapıldıysa o bilgi gelmelidir.
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name: Kullanıcının telefonu göster butonuna tıkladığı modül bilgisi gönderilmelidir. Örn: \"one-cikan-danismanlar\" ya da \"one-cikan-ilanlar/en-yeni\", \"one-cikan-ilanlar/firsat\", \"one-cikan-ilanlar/fiyati-dusen-kiralik\", \"one-cikan-ilanlar/fiyati-dusen-satilik\", \"one-cikan-ilanlar/yatirim-skoru-yuksek\", \"one-cikan-ilanlar/projeler\"
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-15

```markdown
id="AS-15";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Öne çıkan bir ilan kartında Favori (kalp) butonuna tıkla ve favoriye eklendiğini doğrula.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- content_group = ana-sayfa
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

2) favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: Projenin mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ana-sayfa
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = favorites
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand: \"ilan\" , \"danisman\" ya da \"proje\" seçeneklerinden hangisinde işlem yapıldıysa o bilgi gelmelidir.
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name: Kullanıcının telefonu göster butonuna tıkladığı modül bilgisi gönderilmelidir. Örn: \"one-cikan-danismanlar\" ya da \"one-cikan-ilanlar/en-yeni\", \"one-cikan-ilanlar/firsat\", \"one-cikan-ilanlar/fiyati-dusen-kiralik\", \"one-cikan-ilanlar/fiyati-dusen-satilik\", \"one-cikan-ilanlar/yatirim-skoru-yuksek\", \"one-cikan-ilanlar/projeler\"
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = ana-sayfa
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-16

```markdown
id="AS-16";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Arama kutusunda serbest metinle ara (ör. 'satilik ev') ve aramayı başlat.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

search
- search_term: Kullanıcının arattığı kelime bilgisi gönderilmelidir. Boşluk veya özel karakterler yerine \"-\" kullanılmalıdır. Örn: \"satilik-ev\" ya da \"adana\"
- search_type: Kullanıcının yaptığı arama türü Örn: \"freetext\" \"TAB_TURU||structured||il\" \"TAB_TURU||structured||ilce\" \"TAB_TURU||structured||semt\" \"TAB_TURU||structured||mahalle\" \"TAB_TURU||structured||son-aramalar\" TAB_TURU: Kullanıcının aramayı hangi sekme / tab altında yaptığı bilgisi. Örn: \"satılık\", \"kiralik\", \"projeler\", \"danisman\" Eğer AI özelliğiyle arama yapıldıysa search_type parametresi \"ai\" değerini almalıdır.
- search_status: Kullanıcının yaptığı aratma türü Örn: \"default\" ya da \"map\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-17

```markdown
id="AS-17";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Masaüstü görünümde. Header menüsünde bir linke tıkla (ör. Satılık > Yeni İlanlar).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

header
- label: 'click||<LABEL>' biçiminde. LABEL: Kullanıcının tıkladığı menü bilgisi Örn: \"satilik||yeni-ilanlar\" \"kiralik||kiralik-konut\" \"danismanlar||emlak-danismanlari\" \"kesfet||demografi\" \"ilan-ver\" \"degerini-ogren\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-18

```markdown
id="AS-18";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Mobil görünümde. Hamburger menüyü aç, bir menü adımını seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

hamburger_menu
- label: Kullanıcının tıkladığı menü bilgisi Örn: \"satilik||yeni-ilanlar\" \"kiralik||kiralik-konut\" \"danismanlar||emlak-danismanlari\" \"kesfet||demografi\" \"ilan-ver\" \"degerini-ogren\" Hamburger menu ikonuna tıklandıysa \"hamburger-icon\" değerini; Emlakjet logosuna tıklandıysa \"emlakjet-logo\" değerini almalıdır.
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-19

```markdown
id="AS-19";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: Facade search alanında seviye seviye seçim yap (ör. Satılık > Konut > Tümü).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

facade_search
- action: Kullanıcının menülerden seçimi tamamladığında seçilen menülerin bilgisi gönderilmelidir. Boşluk veya özel karakterler yerine \"-\" kullanılmalıdır. Örn:\"seviye-1||satilik\" \"seviye-2||satilik-konut\" \"seviye-3||satilik-konut-tumu\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-20

```markdown
id="AS-20";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka: EmlakZeka widget'ının görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = view||widget
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-21

```markdown
id="AS-21";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka: Widget'a tıklayıp aç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||widget-open
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-22

```markdown
id="AS-22";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Widget açıldığında ilk sekmeyi gözle, sonra başka sekmeye geç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||tab-change
- menu: Kullanıcının tıkladığı tabin label bilgisi gönderilmelidir.. Boşluk veya özel karakterler yerine \"-\" kullanılmalıdır. Örn:\"ilan-ara\", \"degerleme\", \"danisman-bul-ve-sat\" \"bize-ulasin\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-23

```markdown
id="AS-23";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Sekmedeki bir öneriye tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||suggestion
- menu: Kullanıcının tıkladığı tabin label bilgisi gönderilmelidir.. Boşluk veya özel karakterler yerine \"-\" kullanılmalıdır. Örn:\"ilan-ara\", \"degerleme\", \"danisman-bul-ve-sat\" \"bize-ulasin\"
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-24

```markdown
id="AS-24";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Mesaj yaz ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||message-sent
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-25

```markdown
id="AS-25";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Sonucun dönmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = view||result
- total_item: Kullanıcının yaptığı arama sonucunda dönen ilan sayısı gönderilmelidir. String olarak gelmelidir ve ilan dönmemişse \"0\" olarak gelmelidir.
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-26

```markdown
id="AS-26";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Sonuçtaki bir ilana tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||item
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-27

```markdown
id="AS-27";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Konum butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||location
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-28

```markdown
id="AS-28";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Konum iznini ver.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||location-granted
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-29

```markdown
id="AS-29";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Ses butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||voice
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-30

```markdown
id="AS-30";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Mikrofon iznini ver.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||voice-granted
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-31

```markdown
id="AS-31";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Sesle arama yap.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||voice-message-sent
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## AS-32

```markdown
id="AS-32";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com ana sayfası

3. Bu sayfada alınacak aksiyon: EmlakZeka widget'ını aç. Kapat butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

emlakzeka_widget
- label = click||widget-close
- content_group = ana-sayfa

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-01

```markdown
id="IL-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-02

```markdown
id="IL-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: 'Filtrele' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

filtre
- label = click||filtrele
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-03

```markdown
id="IL-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Bir filtre seç ve 'Ara / Filtreleri Uygula' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

filtre
- label = click||filtreleri-uygula
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-04

```markdown
id="IL-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: 'Filtreleri Temizle' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

filtre
- label = click||filtreleri-temizle
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-05

```markdown
id="IL-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: 'Sırala' butonuna tıkla ve bir sıralama seçeneği seç (ör. fiyata göre artan).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) sort_by
- label = click||sırala
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) sort_by
- label: 'click||<LABEL_BILGISI>' biçiminde. LABEL_BILGISI: Yapılan sıralama bilgisi gönderilmelidir. Örn: \"fiyat-once-en-dusuk\" ya da \"akilli-siralama\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-06

```markdown
id="IL-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: 'Görünüm' butonuna tıkla ve görünümü değiştir (ör. tablo).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) list_by
- label = click||gorunum
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) list_by
- label: 'click||<LABEL_BILGISI>' biçiminde. LABEL_BILGISI: Yapılan sıralama bilgisi gönderilmelidir. Örn: \"satır\", \"tablo\" ya da \"kart\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-07

```markdown
id="IL-07";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. 'Aramayı Kaydet' butonuna tıkla ve kaydetme işlemini tamamla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = aramayi-kaydet
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

2) click_button
- label = arama-kaydedildi
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-08

```markdown
id="IL-08";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: İlan listesi bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
  - item_yeni_ilan: Dokümanda açıklama yok.
  - item_order_algorithm: Dokümanda açıklama yok.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-09

```markdown
id="IL-09";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: İlan listesi bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - item_yeni_ilan: Dokümanda açıklama yok.
  - item_order_algorithm: Dokümanda açıklama yok.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-10

```markdown
id="IL-10";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Listedeki proje kartları bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
  - item_yeni_ilan: Dokümanda açıklama yok.
  - item_order_algorithm: Dokümanda açıklama yok.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-11

```markdown
id="IL-11";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Listedeki proje kartları bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - item_yeni_ilan: Dokümanda açıklama yok.
  - item_order_algorithm: Dokümanda açıklama yok.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-12

```markdown
id="IL-12";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Benzer ilanlar bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme/benzer-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-13

```markdown
id="IL-13";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Benzer ilanlar bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme/benzer-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-14

```markdown
id="IL-14";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Listedeki bir ilan kartında 'Telefonu Göster' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = ilan-listeleme
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - item_yeni_ilan: Dokümanda açıklama yok.
  - item_order_algorithm: Dokümanda açıklama yok.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-15

```markdown
id="IL-15";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Listedeki bir ilan kartında numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - item_yeni_ilan: Dokümanda açıklama yok.
  - item_order_algorithm: Dokümanda açıklama yok.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-16

```markdown
id="IL-16";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Listedeki bir ilan kartında Favori (kalp) butonuna tıkla ve favoriye eklendiğini doğrula.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

2) favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: Projenin mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = favorites
  - currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - item_yeni_ilan: Dokümanda açıklama yok.
  - item_order_algorithm: Dokümanda açıklama yok.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-17

```markdown
id="IL-17";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Benzer ilanlar bölümündeki bir kartta 'Telefonu Göster' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = ilan-listeleme
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme/benzer-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-18

```markdown
id="IL-18";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Benzer ilanlar bölümündeki bir kartta numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme/benzer-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-19

```markdown
id="IL-19";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Benzer ilanlar bölümündeki bir kartta Favori (kalp) butonuna tıkla ve favoriye eklendiğini doğrula.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

2) favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: Projenin mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = favorites
  - currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-listeleme/benzer-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - item_one_cikan: İlan öne çıkansa true değilse false şeklinde gelmelidir.
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam ilan sayısı Örn:\"5\" ya da \"100\"
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-20

```markdown
id="IL-20";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: Listeleme sayfasındaki arama alanından yapılandırılmış arama yap (il/ilçe seç).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

search
- search_term: Kullanıcının arattığı kelime bilgisi gönderilmelidir. Boşluk veya özel karakterler yerine \"-\" kullanılmalıdır. Örn: \"satilik-ev\" ya da \"adana\"
- search_type: Kullanıcının yaptığı arama türü Örn: \"freetext\" \"TAB_TURU||structured||il\" \"TAB_TURU||structured||ilce\" \"TAB_TURU||structured||semt\" \"TAB_TURU||structured||mahalle\" \"TAB_TURU||structured||son-aramalar\" TAB_TURU: Kullanıcının aramayı hangi sekme / tab altında yaptığı bilgisi. Örn: \"satılık\", \"kiralik\", \"projeler\", \"danisman\" Eğer AI özelliğiyle arama yapıldıysa search_type parametresi \"ai\" değerini almalıdır.
- search_status: Kullanıcının yaptığı aratma türü Örn: \"default\" ya da \"map\"
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## IL-21

```markdown
id="IL-21";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan listeleme sayfası (ör. satılık konut listesi)

3. Bu sayfada alınacak aksiyon: 'Paylaş' butonuna tıkla, açılan seçeneklerden 'Linki kopyala'yı seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = paylas
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) share
- item_id: İlanın/projenin/danışmanın id bilgisi gönderilmelidir. id bilgisi olmadığı durumlarda bu bilgi string olmayacak şekilde null ya da undefined olarak gönderilmelidir.
- item_type = ilan
- method: Paylaşılan mecra bilgisi gönderilmelidir. Linki kopyalama için \"link-copy\" şeklinde atılsın.
- content_group = ilan-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- benzer_ilan: Sayfada benzer ilan listeleniyorsa \"yes\", yoksa \"no\" şeklinde gelmelidir.
- total_one_cikan: Listelenen öne çıkan ilan sayısı
- total_benzer_ilan: Sayfada görüntülenen toplam benzer ilan sayısı gönderilmelidir.
- oda_sayisi: Görüntülenen ilanların oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen ilanların minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen ilanların maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## HL-01

```markdown
id="HL-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da harita görünümlü ilan listeleme sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = harita-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## HL-02

```markdown
id="HL-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da harita görünümlü ilan listeleme sayfası

3. Bu sayfada alınacak aksiyon: Harita görünümünde arama yap.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

search
- search_term: Kullanıcının arattığı kelime bilgisi gönderilmelidir. Boşluk veya özel karakterler yerine \"-\" kullanılmalıdır. Örn: \"satilik-ev\" ya da \"adana\"
- search_type: Kullanıcının yaptığı arama türü Örn: \"freetext\" \"TAB_TURU||structured||il\" \"TAB_TURU||structured||ilce\" \"TAB_TURU||structured||semt\" \"TAB_TURU||structured||mahalle\" \"TAB_TURU||structured||son-aramalar\" TAB_TURU: Kullanıcının aramayı hangi sekme / tab altında yaptığı bilgisi. Örn: \"satılık\", \"kiralik\", \"projeler\", \"danisman\" Eğer AI özelliğiyle arama yapıldıysa search_type parametresi \"ai\" değerini almalıdır.
- search_status: Kullanıcının yaptığı aratma türü Örn: \"default\" ya da \"map\"
- content_group = harita-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- neighborhood: Bulunduğu sayfanın varsa mahalle bilgisi yoksa undefined değeri gönderilmeli Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-01

```markdown
id="ID-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

2) view_item
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- value = 0
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index = 0
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-02

```markdown
id="ID-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Sticky menüde bir sekmeye tıkla (ör. Özellikler).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_widget
- widget: 'sticky-menu||<MENU_BILGISI>' biçiminde. MENU_BILGISI: Kullanıcının tıkladığı sticky menü bilgisi gönderilmelidir. Örn: \"ozellikler\" \"semt-ozellikleri\" \"fiyat-trendi\" \"deger-analizi\" \"konum\"
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-03

```markdown
id="ID-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Değer analizi widget'ı görünene kadar kaydır.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

widget
- label = view||deger-analizi
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-04

```markdown
id="ID-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Yatırım potansiyeli widget'ı görünene kadar kaydır.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

widget
- label = view||yatirim-potansiyeli
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-05

```markdown
id="ID-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Galeride 'sonraki' okuna, sonra 'tam ekran' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_button
- label: 'galeri||<LABEL_BILGISI>' biçiminde. LABEL_BILGISI: Kullanıcının galeride aldığı aksiyon bilgisi. Örn: before, next ya da full-screen
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-06

```markdown
id="ID-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Galeride bir medya türüne tıkla (ör. video).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_widget
- widget: 'galeri||<LABEL_BILGISI>' biçiminde. LABEL_BILGISI: Kullanıcının galeride tıkladığı medya türü. Örn: fotoğraf, video, 3d-tur, sokak-gorunumu, drone-gorunumu
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-07

```markdown
id="ID-07";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Sayfayı aşağı kaydırarak detay widget'larını görünür yap.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_widget
- widget: Kullanıcının gördüğü widget bilgisi gönderilmelidir. Türkçe karakter, boşluk ya da büyük harf kullanılmamalıdır. Aşağıdak widget labellarını yazıyorum bunlar dışında widget mevcutsa aşağıdaki yapıya uygun şekilde isimlendirmesi yapılmalıdır. Örn: \"ozellikler\", \"aciklama\", \"konum-bilgisi\", \"fiyat-degisimi\", \"semt-ozellikleri\", \"benzer-ilanlar\", \"komsu-bolgeler\"
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-08

```markdown
id="ID-08";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: 'Telefonu Göster' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = ilan-detay
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index = 0
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-09

```markdown
id="ID-09";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index = 0
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-10

```markdown
id="ID-10";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Favori (kalp) butonuna tıkla ve favoriye eklendiğini doğrula.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

2) favorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: Projenin mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = favorites
  - discount = 0
  - index = 0
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-11

```markdown
id="ID-11";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Favoride olan bir ilanın favori butonuna tıklayarak favoriden çıkar.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_unfavorite
- item_id: İlanın ID bilgisi gönderilmelidir.
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-12

```markdown
id="ID-12";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: 'Paylaş' butonuna tıkla, açılan seçeneklerden 'Linki kopyala'yı seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = paylas
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

2) share
- item_id: İlanın/projenin/danışmanın id bilgisi gönderilmelidir. id bilgisi olmadığı durumlarda bu bilgi string olmayacak şekilde null ya da undefined olarak gönderilmelidir.
- item_type = ilan
- method: Paylaşılan mecra bilgisi gönderilmelidir. Linki kopyalama için \"link-copy\" şeklinde atılsın.
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = share
  - discount = 0
  - index = 0
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-13

```markdown
id="ID-13";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: 'Mesaj Gönder' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

click_message
- item_id: İlanın ID bilgisi gönderilmelidir.
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-14

```markdown
id="ID-14";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Mesaj formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) send_message
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = message
  - discount = 0
  - index = 0
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-15

```markdown
id="ID-15";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: 'WhatsApp' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_whatsapp
- item_id: İlanın ID bilgisi gönderilmelidir.
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = whatsapp
  - discount = 0
  - index = 0
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-16

```markdown
id="ID-16";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Benzer ilanlar bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay/benzer-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-17

```markdown
id="ID-17";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Benzer ilanlar bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay/benzer-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-18

```markdown
id="ID-18";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: İlgili ilanlar bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay/ilgili-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-19

```markdown
id="ID-19";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: İlgili ilanlar bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay/ilgili-ilanlar
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-20

```markdown
id="ID-20";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Bu ilana bakanlar bunlara da baktı bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay/bunlara-da-bakti
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## ID-21

```markdown
id="ID-21";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir ilan detay sayfası (URL'si /ilan/ ile başlar)

3. Bu sayfada alınacak aksiyon: Bu ilana bakanlar bunlara da baktı bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = ilan-detay/bunlara-da-bakti
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = ilan-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: İlanın 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: İlanın 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = ilan
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: İlanın ID bilgisi gönderilmelidir.
- gallery_type: İlanın fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"
- foto_adet: İlanda kaç tane fotoğraf bulunduğu bilgisi gönderilmelidir.
- ilan_firsat: İlanın fırsat ilanın olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat_dusen: İlanın fiyatı düşen ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_one_cikan: İlanın öne çıkan ilan olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- iyilestirilmis_ilan: İlanın iyileştirilme ilanı olup olmadığı bilgisi Örn: \"true\" ya da \"false\" şeklinde gönderilmelidir.
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir.
- iyilestirilmis_foto_adet: İlanın iyileştirilmiş fotosu varsa kaç adet olduğu bilgisi
- ilan_yayinlanma_tarihi: İlanın yayınlanma tarihi bilgisi gönderilmelidir.
- ilan_one_cikarilma_tarihi: İlan öne çıkan ilansa öne çıkarılma tarihi gönderilmelidir.
- ilan_uye_id: İlanın satıcısının ID bilgisi gelmelidir.
- ilan_uye_tip: İlanın satıcısının üyelik bilgisi Örn: \"kurumsal\", \"bireysel\"
- oda_sayisi: İlanın oda sayısı bilgisi gönderilmelidir.

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PL-01

```markdown
id="PL-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da proje listeleme sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (proje bazlı değil)
- content_group = proje-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam proje sayısı Örn:\"5\" ya da \"100\"
- total_one_cikan: Listelenen öne çıkan proje sayısı
- oda_sayisi: Görüntülenen projelerin oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen projelerin minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen projelerin maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PL-02

```markdown
id="PL-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da proje listeleme sayfası

3. Bu sayfada alınacak aksiyon: Proje listesi bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-listeleme
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (proje bazlı değil)
- content_group = proje-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam proje sayısı Örn:\"5\" ya da \"100\"
- total_one_cikan: Listelenen öne çıkan proje sayısı
- oda_sayisi: Görüntülenen projelerin oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen projelerin minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen projelerin maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PL-03

```markdown
id="PL-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da proje listeleme sayfası

3. Bu sayfada alınacak aksiyon: Proje listesi bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-listeleme
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (proje bazlı değil)
- content_group = proje-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_item: Kullanıcı listeleme sayfasında gördüğü toplam proje sayısı Örn:\"5\" ya da \"100\"
- total_one_cikan: Listelenen öne çıkan proje sayısı
- oda_sayisi: Görüntülenen projelerin oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen projelerin minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen projelerin maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PL-04

```markdown
id="PL-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da proje listeleme sayfası

3. Bu sayfada alınacak aksiyon: 'Sırala' butonuna tıkla ve bir seçenek seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) sort_by
- label = click||sırala
- content_group = proje-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_one_cikan: Listelenen öne çıkan proje sayısı
- oda_sayisi: Görüntülenen projelerin oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen projelerin minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen projelerin maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) sort_by
- label: 'click||<LABEL_BILGISI>' biçiminde. LABEL_BILGISI: Yapılan sıralama bilgisi gönderilmelidir. Örn: \"fiyat-once-en-dusuk\" ya da \"akilli-siralama\"
- content_group = proje-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_one_cikan: Listelenen öne çıkan proje sayısı
- oda_sayisi: Görüntülenen projelerin oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen projelerin minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen projelerin maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PL-05

```markdown
id="PL-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da proje listeleme sayfası

3. Bu sayfada alınacak aksiyon: 'Paylaş' butonuna tıkla, açılan seçeneklerden 'Linki kopyala'yı seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = paylas
- content_group = proje-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_one_cikan: Listelenen öne çıkan proje sayısı
- oda_sayisi: Görüntülenen projelerin oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen projelerin minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen projelerin maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

2) share
- item_id: İlanın/projenin/danışmanın id bilgisi gönderilmelidir. id bilgisi olmadığı durumlarda bu bilgi string olmayacak şekilde null ya da undefined olarak gönderilmelidir.
- item_type = proje
- method: Paylaşılan mecra bilgisi gönderilmelidir. Linki kopyalama için \"link-copy\" şeklinde atılsın.
- content_group = proje-listeleme
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Bulunduğu sayfanın 1. Derece kategori bilgisi Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Bulunduğu sayfanın 3. Derece kategori bilgisi Örn: \"koy-evi\" ya da \"konut\"
- city: Bulunduğu sayfanın varsa şehir bilgisi yoksa undefined değeri gönderilmeli Örn: \"kocaeli\"
- town: Bulunduğu sayfanın varsa ilçe bilgisi yoksa undefined değeri gönderilmeli Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- total_filter: Bulunduğu sayfada filtreleme işlemi yapılmışsa kaç farklı filtre kullanıldığı bilgisi gönderilmelidir. Örn:\"5\" ya da \"0\" şeklinde
- total_one_cikan: Listelenen öne çıkan proje sayısı
- oda_sayisi: Görüntülenen projelerin oda sayısı bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Oda tipleri arasında uzun çizgi \"||\" kullanılmalı Örneğin: \"studyo\" \"1+1||2+1\" \"3+1||4+1||4+2\"
- arama_kelimesi: Filtrelemede kullanıcının girdiği anahtar kelime bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı
- min_metrekare: Görüntülenen projelerin minimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"min\" \"70\"
- max_metrekare: Görüntülenen projelerin maksimum brüt metrekare bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Seçenekler arasında orta çizgi \"-\" kullanılmalı Örneğin: \"max\" \"140\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-01

```markdown
id="PD-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

2) view_item
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- value = 0
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-02

```markdown
id="PD-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: 'Telefonu Göster' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = proje-detay
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-03

```markdown
id="PD-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: Numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-04

```markdown
id="PD-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: 'Bilgi Al' formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) send_project_form
- project_name: Görüntülenen projenin adı gönderilmelidir.
- project_id: Görüntülenen projenin ID'si gönderilmelidir.
- project_company_name: Görüntülenen projenin firma adı gönderilmelidir.
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = form
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-05

```markdown
id="PD-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: 'Paylaş' butonuna tıkla, açılan seçeneklerden 'Linki kopyala'yı seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = paylas
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

2) share
- item_id: İlanın/projenin/danışmanın id bilgisi gönderilmelidir. id bilgisi olmadığı durumlarda bu bilgi string olmayacak şekilde null ya da undefined olarak gönderilmelidir.
- item_type = proje
- method: Paylaşılan mecra bilgisi gönderilmelidir. Linki kopyalama için \"link-copy\" şeklinde atılsın.
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = share
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = proje-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-06

```markdown
id="PD-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: Bölgedeki projeler bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay/bolgedeki-projeler
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-07

```markdown
id="PD-07";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: Bölgedeki projeler bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay/bolgedeki-projeler
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-08

```markdown
id="PD-08";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: Firmanın diğer projeleri bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay/firmanin-diger-projeleri
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## PD-09

```markdown
id="PD-09";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje detay sayfası

3. Bu sayfada alınacak aksiyon: Firmanın diğer projeleri bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = proje-detay/firmanin-diger-projeleri
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = proje-detay
- property_category: Bulunduğu sayfanın 2. Derece kategori bilgisi Örn: \"konut\" ya da \"is-yeri\"
- property_status: Projenin 1. Derece kategori bilgisi gönderilmelidir. Örn: \"satilik\" ya da \"kiralik\"
- property_subcategory: Projenin 3. Derece kategori bilgisi gönderilmelidir. Örn: \"koy-evi\" ya da \"konut\"
- item_type = proje
- city: Projenin şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: Projenin ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- item_id: Projenin ID bilgisi gönderilmelidir.
- gallery_type: Projenin fotoğraflarında 3d ve video var mı bilgisi Örn: ikisi de varsa: \"true||true\" Sadece 3d varsa: \"false||true\" Sadece video varsa: \"true||false\" İkisi de yoksa: \"false||false\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DL-01

```markdown
id="DL-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com emlak danışmanları listeleme sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- content_group = danisman-listeleme
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DL-02

```markdown
id="DL-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com emlak danışmanları listeleme sayfası

3. Bu sayfada alınacak aksiyon: Danışman listesi bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının gördüğü danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü danışmanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü danışmanın o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Görüntülenen danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen danışmanın mahalle bilgisi. Örn: \"baglarbasi\"
  - item_list_id: Görüntülenen danışmanın bulunduğu modülün id bilgisi
  - item_list_name = danisman-listeleme
  - location_id: Görüntülenen danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-listeleme
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DL-03

```markdown
id="DL-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com emlak danışmanları listeleme sayfası

3. Bu sayfada alınacak aksiyon: Danışman listesi bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Tıklanılan danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının tıkladığı danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının tıkladığı danışmanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının tıkladığı danışmanın o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Tıklanılan danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Tıklanılan danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Tıklanılan danışmanın mahalle bilgisi. Örn: \"osman-yilmaz\"
  - item_list_id: Tıklanılan danışmanın bulunduğu modülün id bilgisi
  - item_list_name = danisman-listeleme
  - location_id: Tıklanılan danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-listeleme
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DL-04

```markdown
id="DL-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com emlak danışmanları listeleme sayfası

3. Bu sayfada alınacak aksiyon: Bir danışman kartında 'Talep Gönder' formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının gördüğü danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü danışmanın ismi gönderilmelidir.
  - affiliation = form
  - discount = 0
  - index: Kullanıcının gördüğü danışman o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Görüntülenen danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen danışmanın mahalle bilgisi. Örn: \"kazim-karabekir\"
  - item_list_id: Görüntülenen danışmanın bulunduğu modülün id bilgisi
  - item_list_name = danisman-listeleme
  - location_id: Görüntülenen danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-listeleme
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DL-05

```markdown
id="DL-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com emlak danışmanları listeleme sayfası

3. Bu sayfada alınacak aksiyon: Bir danışman kartında 'Telefonu Göster' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = danisman-listeleme

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = danisman-listeleme
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = danisman-listeleme
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-listeleme
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DL-06

```markdown
id="DL-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com emlak danışmanları listeleme sayfası

3. Bu sayfada alınacak aksiyon: Bir danışman kartında 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = danisman-listeleme

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = danisman-listeleme
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-listeleme
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DL-07

```markdown
id="DL-07";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com emlak danışmanları listeleme sayfası

3. Bu sayfada alınacak aksiyon: Danışman arama alanında uzmanlık alanı seçip ara.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

search
- search_term: Kullanıcının arattığı kelime bilgisi gönderilmelidir. Boşluk veya özel karakterler yerine \"-\" kullanılmalıdır. Örn: \"satilik-ev\" ya da \"adana\"
- search_type: Kullanıcının yaptığı arama türü Örn: \"freetext\" \"TAB_TURU||structured||il\" \"TAB_TURU||structured||ilce\" \"TAB_TURU||structured||semt\" \"TAB_TURU||structured||mahalle\" \"TAB_TURU||structured||son-aramalar\" TAB_TURU: Kullanıcının aramayı hangi sekme / tab altında yaptığı bilgisi. Örn: \"satılık\", \"kiralik\", \"projeler\", \"danisman\" Eğer AI özelliğiyle arama yapıldıysa search_type parametresi \"ai\" değerini almalıdır.
- search_status: Kullanıcının yaptığı aratma türü Örn: \"default\" ya da \"map\"
- content_group = danisman-listeleme
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DD-01

```markdown
id="DD-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak danışmanı detay sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) page_view
- content_group = danisman-detay
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

2) view_item
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- value = 0
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının gördüğü danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü danışmanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü danışmanın o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Görüntülenen danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen danışmanın mahalle bilgisi. Örn: \"mevlana\"
  - item_list_id: Görüntülenen danışmanın bulunduğu modülün id bilgisi
  - item_list_name = danisman-detay
  - location_id: Görüntülenen danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-detay
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DD-02

```markdown
id="DD-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak danışmanı detay sayfası

3. Bu sayfada alınacak aksiyon: 'Numarayı Göster / Telefon Et' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = danisman-detay

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = danisman-detay
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının gördüğü danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü danışmanın ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü danışman o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Görüntülenen danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen danışmanın mahalle bilgisi. Örn: \"abdi-ipekci\"
  - item_list_id: Görüntülenen danışmanın bulunduğu modülün id bilgisi
  - item_list_name = danisman-detay
  - location_id: Görüntülenen danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-detay
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DD-03

```markdown
id="DD-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak danışmanı detay sayfası

3. Bu sayfada alınacak aksiyon: Numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = danisman-detay

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının gördüğü danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü danışmanın ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü danışman o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Görüntülenen danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen danışmanın mahalle bilgisi. Örn: \"abdi-ipekci\"
  - item_list_id: Görüntülenen danışmanın bulunduğu modülün id bilgisi
  - item_list_name = danisman-detay
  - location_id: Görüntülenen danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-detay
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DD-04

```markdown
id="DD-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak danışmanı detay sayfası

3. Bu sayfada alınacak aksiyon: 'Talep Gönder' formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen danışmanın ortalama satış fiyatı bilgisi
  - item_id: Kullanıcının gördüğü danışmanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü danışmanın ismi gönderilmelidir.
  - affiliation = form
  - discount = 0
  - index: Kullanıcının gördüğü danışman o modüldeki pozisyonu gönderilmelidir.
  - item_brand = danisman
  - item_category3: Görüntülenen danışmanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen danışmanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen danışmanın mahalle bilgisi. Örn: \"kazim-karabekir\"
  - item_list_id: Görüntülenen danışmanın bulunduğu modülün id bilgisi
  - item_list_name = danisman-detay
  - location_id: Görüntülenen danışmanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- content_group = danisman-detay
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DD-05

```markdown
id="DD-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak danışmanı detay sayfası

3. Bu sayfada alınacak aksiyon: 'Paylaş' butonuna tıkla, açılan seçeneklerden 'Linki kopyala'yı seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = paylas
- content_group = danisman-detay
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

2) share
- item_id: İlanın/projenin/danışmanın id bilgisi gönderilmelidir. id bilgisi olmadığı durumlarda bu bilgi string olmayacak şekilde null ya da undefined olarak gönderilmelidir.
- item_type = danisman
- method: Paylaşılan mecra bilgisi gönderilmelidir. Linki kopyalama için \"link-copy\" şeklinde atılsın.
- content_group = danisman-detay
- city: Görüntülenen danışmanın il bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"istanbul\" \"antalya\"
- town: Görüntülenen danışmanın ilçe bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"sariyer\" \"kepez\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- neighborhood: Görüntülenen danışmanın mahalle bilgisi gönderilmelidir. Tümü küçük harf olmalı Türkçe karakterler (ı,ğ,ü,ş,ç,ö) kullanılmamalı Boşluk yerine orta çizgi \"-\" kullanılmalı Örneğin: \"mimar-sinan-mah\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## EO-01

```markdown
id="EO-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak ofisi detay sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = emlak-ofisi-detay

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## EO-02

```markdown
id="EO-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak ofisi detay sayfası

3. Bu sayfada alınacak aksiyon: Ofisin ilan listesi bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = emlak-ofisi-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = emlak-ofisi-detay

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## EO-03

```markdown
id="EO-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak ofisi detay sayfası

3. Bu sayfada alınacak aksiyon: Ofisin ilan listesi bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = emlak-ofisi-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = emlak-ofisi-detay

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## EO-04

```markdown
id="EO-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak ofisi detay sayfası

3. Bu sayfada alınacak aksiyon: Bir ilan kartında 'Telefon Et' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = emlak-ofisi-detay

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = emlak-ofisi-detay
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = emlak-ofisi-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = emlak-ofisi-detay

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## EO-05

```markdown
id="EO-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak ofisi detay sayfası

3. Bu sayfada alınacak aksiyon: Bir ilan kartında numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = emlak-ofisi-detay

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = emlak-ofisi-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = emlak-ofisi-detay

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## EO-06

```markdown
id="EO-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak ofisi detay sayfası

3. Bu sayfada alınacak aksiyon: 'Bilgi Al' formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = form
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = emlak-ofisi-detay
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = emlak-ofisi-detay

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## EO-07

```markdown
id="EO-07";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir emlak ofisi detay sayfası

3. Bu sayfada alınacak aksiyon: 'Paylaş' butonuna tıkla, açılan seçeneklerden 'Linki kopyala'yı seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = paylas
- content_group = emlak-ofisi-detay

2) share
- item_id: İlanın/projenin/danışmanın id bilgisi gönderilmelidir. id bilgisi olmadığı durumlarda bu bilgi string olmayacak şekilde null ya da undefined olarak gönderilmelidir.
- item_type = ilan
- method: Paylaşılan mecra bilgisi gönderilmelidir. Linki kopyalama için \"link-copy\" şeklinde atılsın.
- content_group = emlak-ofisi-detay

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FP-01

```markdown
id="FP-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje firması profil sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = firma-profil

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FP-02

```markdown
id="FP-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje firması profil sayfası

3. Bu sayfada alınacak aksiyon: Firmanın proje listesi bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = firma-profil
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = firma-profil

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FP-03

```markdown
id="FP-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje firması profil sayfası

3. Bu sayfada alınacak aksiyon: Firmanın proje listesi bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = firma-profil
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = firma-profil

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FP-04

```markdown
id="FP-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje firması profil sayfası

3. Bu sayfada alınacak aksiyon: Bir proje kartında 'Telefonu Göster' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) view_phone
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = firma-profil

2) view_phone_all (yalnızca oturumdaki ilk tıklamada)
- content_group = firma-profil
- ilan_fiyat: İlanın fiyat bilgisi gönderilmelidir. Örn: \"12345\" şeklinde string gelmelidir.
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"

3) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = view_phone
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = firma-profil
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = firma-profil

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FP-05

```markdown
id="FP-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje firması profil sayfası

3. Bu sayfada alınacak aksiyon: Bir proje kartında numara görünür olduktan sonra 'Ara' butonuna tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) call
- item_id: İlanın ID bilgisi gönderilmelidir.
- item_type: İlan mı proje mi olduğu bilgisi gönderilmelidir. Örn: \"ilan\" ya da \"proje\"
- city: İlanın şehir bilgisi gönderilmelidir. Örn: \"kocaeli\"
- town: İlanın ilçe bilgisi gönderilmelidir. Örn: \"gebze\"
- neighborhood: İlanın mahalle bilgisi gönderilmelidir. Örn: \"kazim-karabekir\"
- district: Bulunduğu sayfanın varsa semt bilgisi yoksa undefined değeri gönderilmelidir. Örn: \"istasyon\"
- content_group = firma-profil

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = call
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = firma-profil
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = firma-profil

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FP-06

```markdown
id="FP-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje firması profil sayfası

3. Bu sayfada alınacak aksiyon: 'Bilgi Al' formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü projenin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen projenin fiyat bilgisi
  - item_id: Kullanıcının gördüğü projenin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü projenin ismi gönderilmelidir.
  - affiliation = form
  - discount = 0
  - index: Kullanıcının gördüğü projenin o modüldeki posizyonu gönderilmelidir.
  - item_brand = proje
  - item_category: Görüntülenen projenin konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen projenin için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen projenin il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen projenin ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen projenin mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen projenin bulunduğu modülün id bilgisi
  - item_list_name = firma-profil
  - item_variant: Görüntülenen projenin satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen projenin bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = firma-profil

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FP-07

```markdown
id="FP-07";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da bir proje firması profil sayfası

3. Bu sayfada alınacak aksiyon: 'Paylaş' butonuna tıkla, açılan seçeneklerden 'Linki kopyala'yı seç.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) click_button
- label = paylas
- content_group = firma-profil

2) share
- item_id: İlanın/projenin/danışmanın id bilgisi gönderilmelidir. id bilgisi olmadığı durumlarda bu bilgi string olmayacak şekilde null ya da undefined olarak gönderilmelidir.
- item_type = proje
- method: Paylaşılan mecra bilgisi gönderilmelidir. Linki kopyalama için \"link-copy\" şeklinde atılsın.
- content_group = firma-profil

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FL-01

```markdown
id="FL-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com favori listem sayfası

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = favori-listem
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FL-02

```markdown
id="FL-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com favori listem sayfası

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Yayındaki favori ilanlar bölümüne kaydır, kartların görünür olmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

view_item_list
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = favori-listesi
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = favori-listem
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## FL-03

```markdown
id="FL-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com favori listem sayfası

3. Bu sayfada alınacak aksiyon: Giriş yapılmış hesapla. Yayındaki favori ilanlar bölümündeki ilk karta tıkla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

select_item
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_price: Görüntülenen ilanın fiyat bilgisi
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_brand = ilan
  - item_category: Görüntülenen ilanın konut / işyeri / arsa gibi kategori bilgisi Örn: Konut için \"konut\" İşyeri için \"isyeri\"
  - item_category2: Görüntülenen ilan için daire / villa / köy evi gibi kategori bilgisi Örn: Daire için \"daire\" Villa için \"villa\" Köy Evi için \"koy-evi\"
  - item_category3: Görüntülenen ilanın il bilgisi. Örn: \"kocaeli\"
  - item_category4: Görüntülenen ilanın ilçe bilgisi. Örn: \"darıca\"
  - item_category5: Görüntülenen ilanın mahalle bilgisi. Örn: \"fevzi-cakmak\"
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = favori-listesi
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - location_id: Görüntülenen ilanın bulunduğu lokasyonun id bilgisi
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = favori-listem
- login_status = true (giriş yapılmış hesapta)
- member_type: Emlakçılar için customer, normal kullanıcılar için user.
- member_id: Her kullanıcıya özel atanan benzersiz ID. Örn: 2329000
- account_type: Kullanıcının tipine göre bireysel ya da kurumsal.
- account_id: Her üst hesaba özel atanan benzersiz ID. Örn: 19875085

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UG-01

```markdown
id="UG-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üye giriş sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = uye-giris

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UG-02

```markdown
id="UG-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üye giriş sayfası

3. Bu sayfada alınacak aksiyon: Giriş formunun görüntülenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

form
- label = view||login-form
- content_group = uye-giris

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UG-03

```markdown
id="UG-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üye giriş sayfası

3. Bu sayfada alınacak aksiyon: Test hesabıyla Test hesabıyla e-posta yöntemiyle giriş yap.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

login
- method: Kullanıcının hangi kayıt türüyle kayıt yaptığı bilgisi gönderilmelidir. Örn: \"email\" , \"google\" \"facebook\" , \"apple\" , \"telefon\"
- uid: Kullanıcının user_id bilgisi gönderilmelidir.
- content_group = uye-giris

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UG-04

```markdown
id="UG-04";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üye giriş sayfası

3. Bu sayfada alınacak aksiyon: Bireysel kayıt akışında e-posta gir ve kayıt formunun açılmasını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

form
- label = view||register-individual-form
- content_group = uye-giris

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UG-05

```markdown
id="UG-05";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üye giriş sayfası

3. Bu sayfada alınacak aksiyon: Yeni bir test e-postasıyla Bireysel kayıt formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

register_individual
- method: Kullanıcının hangi kayıt türüyle kayıt yaptığı bilgisi gönderilmelidir. Örn: \"email\" , \"google\" ,\"facebook\", \"apple\", \"telefon\"
- uid: Kullanıcının user_id bilgisi gönderilmelidir.
- content_group = uye-giris

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UG-06

```markdown
id="UG-06";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üye giriş sayfası

3. Bu sayfada alınacak aksiyon: Kayıt sonrası aktivasyon e-postası / SMS gönderildi ekranını bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

register_activation
- method: Kullanıcının hangi kayıt türüyle kayıt yaptığı bilgisi gönderilmelidir. Örn: \"email\" , \"google\" ,\"facebook\", \"apple\", \"telefon\"
- content_group = uye-giris

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## KK-01

```markdown
id="KK-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com kurumsal üye kayıt sayfası (/uye-ol/kurumsal)

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = kurumsal-kayit

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## KK-02

```markdown
id="KK-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com kurumsal üye kayıt sayfası (/uye-ol/kurumsal)

3. Bu sayfada alınacak aksiyon: Kurumsal kayıt formunun görüntülenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

form
- label = view||register-corporate-form
- content_group = kurumsal-kayit

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## KK-03

```markdown
id="KK-03";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com kurumsal üye kayıt sayfası (/uye-ol/kurumsal)

3. Bu sayfada alınacak aksiyon: Kurumsal kayıt formunu doldur ve gönder.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

register_corporate
- method: Kullanıcının hangi kayıt türüyle kayıt yaptığı bilgisi gönderilmelidir. Örn: \"email\" \"google\" \"facebook\", \"apple\"
- uid: Kullanıcının user_id bilgisi gönderilmelidir.
- content_group = kurumsal-kayit

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UP-01

```markdown
id="UP-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üyelik paketleri sayfası

3. Bu sayfada alınacak aksiyon: Sayfayı aç ve tam yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = uyelik-paketleri

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## UP-02

```markdown
id="UP-02";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com üyelik paketleri sayfası

3. Bu sayfada alınacak aksiyon: Satın almayı tamamla.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

1) purchase
- value: Satın alınan ürünün/ürünlerin toplam fiyat bilgisi gönderilmelidir. Vergi dahil edilmemelidir. Double formatında
- shipping = 0
- tax: Satın alınan ürünün/ürünlerin toplam vergi fıyatı bilgisi gönderilmelidir. Double formatında
- currency: Kullanıcının satın aldığı paketin para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- coupon: Satın alımda kullanılan kupon kodu bilgisi gönderilmelidir. Kupon kodu yoksa burada string olmayan null değeri gönderilmelidir.
- transaction_id: Satın alma işlemi için atanan benzersiz id değeri gönderilmelidir.
- items (görünen/işlem yapılan her öğe için bir item):
  - item_id: Kullanıcının satın aldığı paketin id bilgisi gönderilmelidir.
  - item_name: Kullanıcının satın aldığı paketin ismi gönderilmelidir.
  - coupon: Satın alımda kullanılan kupon kodu bilgisi gönderilmelidir. Kupon kodu yoksa burada string olmayan null değeri gönderilmelidir.
  - discount: Kullanıcının satın aldığı üründe varsa indirim tutarı gönderilmelidir. Örn: 20.0 Double formatında
  - index: Kullanıcının satın aldığı paketin o modüldeki pozisyonu gönderilmelidir.
  - item_list_id: Ürünün bulunduğu modülün id bilgisi
  - item_list_name = uyelik-paketleri
  - item_variant: Kullanıcının satın aldığı ürünün paket tipi gönderilmelidir. Örn: \"danisman-paketleri\", \"ofis-paketleri\", \"one-cikarma-ozellikleri\" ya da \"ek-ilan-paketleri\"
  - price: Kullanıcının satın aldığı ürünün fiyat bilgisi gönderilmelidir. Örn: 12.0 Double formatında
  - quantity: Kullanıcının satın aldığı ürünün adet bilgisi. Örn: 1 int formatında
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = uyelik-paketleri

2) add_to_wishlist
- value = 0
- currency: Kullanıcının gördüğü ilanın para birimi gönderilmelidir. Örn: \"TRY\" ya da \"USD\"
- items (görünen/işlem yapılan her öğe için bir item):
  - search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
  - item_id: Kullanıcının gördüğü ilanın id bilgisi gönderilmelidir.
  - item_name: Kullanıcının gördüğü ilanın ismi gönderilmelidir.
  - affiliation = purchase
  - discount = 0
  - index: Kullanıcının gördüğü ilanın o modüldeki posizyonu gönderilmelidir.
  - item_list_id: Görüntülenen ilanın bulunduğu modülün id bilgisi
  - item_list_name = uyelik-paketleri
  - item_variant: Görüntülenen ilanın satılık, kiralık gibi kategori bilgisi Örn: Satılık için \"satilik\" Kiralık için \"kiralik\"
  - price = 0
  - quantity = 1
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = uyelik-paketleri

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## DS-01

```markdown
id="DS-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da tanımlı gruplar dışında bir sayfa (ör. haberler)

3. Bu sayfada alınacak aksiyon: Tanımlı gruplar dışındaki bir sayfayı aç (ör. haberler, kayıtlı aramalarım).

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group: Sayfa bilgisi gönderilmelidir. Örn: \"haberler\", \"favori-listem\" ya da \"kayitli-aramalarim\"

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## S404-01

```markdown
id="S404-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da var olmayan bir URL

3. Bu sayfada alınacak aksiyon: Var olmayan bir URL aç ve 404 sayfasının yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = 404-sayfasi

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```

## S410-01

```markdown
id="S410-01";
prompt="Görev: emlakjet.com'da GA4 event doğrulaması yap.

1. Web sitesini Playwright MCP ile ziyaret et. Tüm adımları Playwright MCP araçlarıyla yap.

2. Ziyaret edilecek sayfa: https://www.emlakjet.com adresinden başla ve şu sayfaya git: emlakjet.com'da yayından kalkmış bir ilan URL'si

3. Bu sayfada alınacak aksiyon: Yayından kalkmış bir ilan URL'si aç ve 410 sayfasının yüklenmesini bekle.

4. Sayfayı ziyaret ederken ve aksiyonu gerçekleştirirken kullandığın her Playwright MCP komutunu, parametreleriyle birlikte kullanım sırasına göre not et.

5. Aksiyondan sonra network isteklerinde GA4 isteklerini (google-analytics.com/g/collect, tid=G-RQY35QJEY7) incele. Aşağıdaki event'lerin gönderilip gönderilmediğini, her event'te beklenen parametrelerin olup olmadığını ve değerlerinin beklenene uyup uymadığını not et. \"=\" net beklenen değeri, \":\" beklenen değerin açıklamasını gösterir.

Beklenen event ve parametreler:

page_view
- search_id: 32 karakterden oluşmalı Harf ve rakam içermeli Her sayfa görüntülemesi için oluşturulmalı (ilan bazlı değil)
- content_group = 410-sayfasi

6. Sonucu verilen output şemasına uygun bir JSON olarak hazırla.";
id="$id-$(uuidgen | cut -c1-8 | tr A-Z a-z)" && echo "id: $id" && claude -p "$prompt" -n "$id" --model opus --effort high --mcp-config '{"mcpServers":{"playwright":{"command":"npx","args":["@playwright/mcp@0.0.84","--isolated","--caps=network,devtools","--codegen=none"]}}}' --strict-mcp-config --allowedTools mcp__playwright --output-format json --json-schema "$(cat docs/recorder-output.schema.json)" | jq .structured_output > "recordings/$id.json" && cp "$(grep -l "\"customTitle\":\"$id\"" ~/.claude/projects/-Users-snncn-projects-sinancan34-argos-agent/*.jsonl)" "recordings/$id.session.jsonl"
```
