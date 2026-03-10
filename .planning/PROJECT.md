# Argos — GA4 Audit Tool

## What This Is

GA4 (Google Analytics 4) implementasyonlarını denetleyen bir araç. Backend API üzerinden senaryolar tanımlanır, Chrome extension tarayıcıda senaryoları çalıştırır (sayfa aç, buton tıkla vb.), network isteklerini dinler, başarı kriterlerini kontrol eder ve sonuçları API'ye raporlar. Senaryo oluşturma, çalıştırma ve raporlama arayüzü sunar.

## Core Value

Bir web sitesindeki GA4 event'lerinin doğru tetiklendiğini otomatik olarak doğrulayabilmek — senaryoya dayalı, tekrarlanabilir audit.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Backend API (FastAPI) ile senaryo CRUD
- [ ] SQLite veritabanı, yolu .env ile konfigüre edilebilir
- [ ] Veritabanı install ve seed için API endpoint'leri
- [ ] Adım tabanlı senaryo modeli (URL aç, tıkla, form doldur vb.)
- [ ] Başarı kriteri: URL pattern + parametre kontrolü (network isteklerinde)
- [ ] Chrome extension senaryoyu API'den alır, tarayıcıda çalıştırır
- [ ] Chrome extension network isteklerini dinler, başarı kriterlerini kontrol eder
- [ ] Sonuçlar API'ye gönderilir (senaryo bazlı özet: pass/fail)
- [ ] Arayüz: senaryo oluşturma, çalıştırma, rapor görüntüleme
- [ ] API dokümantasyonu (Swagger/ReDoc)

### Out of Scope

- Authentication/authorization — şimdilik gerekli değil
- Çoklu kullanıcı/workspace desteği — tek kullanıcılı
- Chrome extension geliştirme — backend öncelikli

## Context

- Proje iki ana katmandan oluşacak: `backend/` (API + DB) ve `extension/` (Chrome extension)
- İlk aşamada sadece backend iskeleti kurulacak
- Senaryo detayları (aksiyon tipleri, başarı kriteri yapısı) ilerleyen aşamalarda tanımlanacak

## Constraints

- **Tech stack**: FastAPI, SQLite + SQLAlchemy, Alembic, Pydantic-settings — sabit, değişmeyecek
- **Auth**: Yok, eklenmeyecek (şimdilik)
- **Kullanıcı modeli**: Tek kullanıcılı

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| backend/ + extension/ dizin yapısı | Her katman bağımsız, temiz ayrım | — Pending |
| FastAPI + SQLite + SQLAlchemy + Alembic | Kullanıcının tercihi, hafif ve yeterli | — Pending |
| Senaryo bazlı özet sonuçlar (pass/fail) | Adım bazlı detay yerine basit özet, ilk versiyon için yeterli | — Pending |

---
*Last updated: 2026-03-10 after initialization*
