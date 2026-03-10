# Argos - Kurulum Rehberi

## Gereksinimler

- Python 3.12+
- pip
- git

## 1. Projeyi Klonla

```bash
git clone <repo-url>
cd argos
```

## 2. Virtual Environment Oluştur

```bash
cd backend
python3 -m venv env
source env/bin/activate
```

## 3. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

## 4. Ortam Değişkenlerini Ayarla

`.env.example` dosyasını kopyalayıp `.env` oluştur:

```bash
cp .env.example .env
```

Varsayılan olarak SQLite kullanılır. PostgreSQL kullanmak istersen `.env` dosyasındaki `DATABASE_URL` değerini güncelle:

```
DATABASE_URL=sqlite:///./argos.db
```

## 5. Veritabanını Oluştur

İlk migration'ı oluştur ve uygula:

```bash
alembic revision --autogenerate -m "initial tables"
alembic upgrade head
```

> **Not:** Veritabanı dosyasını (`argos.db`) sildiysen, aynı `alembic upgrade head` komutunu çalıştırarak tekrar oluşturabilirsin. Eğer `alembic/versions/` klasöründe henüz migration dosyası yoksa, önce `alembic revision --autogenerate -m "initial tables"` komutunu çalıştırman gerekir.

## 6. Geliştirme Sunucusunu Başlat

```bash
python -m uvicorn app.main:app --reload
```

Sunucu varsayılan olarak `http://127.0.0.1:8000` adresinde çalışır.

API dokümantasyonu: `http://127.0.0.1:8000/docs`
