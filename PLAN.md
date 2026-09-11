# Otomatik Güncellenen Global Futbol Gündemi Sitesi — Plan

## Context

Kullanıcı `C:\Users\User\Desktop\futbol` klasöründe (şu an boş) global futbol
gündemini takip eden bir web sitesi kurmak istiyor. Site kendi başına, periyodik
olarak internette popüler/gündemdeki futbol konularını araştırıp (Claude
aracılığıyla) bunları kısa özet + kaynak linki şeklinde siteye ekleyecek. Amaç:
elle içerik girmeden kendini güncelleyen bir futbol haber/gündem akışı.

Kullanıcının onayladığı kapsam:
- **İçerik**: Global futbol (Premier League, La Liga, Champions League vb.),
  Türkiye özel değil.
- **Otomasyon sıklığı**: Günde birkaç kez (önerilen: her 6 saatte bir → günde 4
  çalışma).
- **İçerik formatı**: Her konu için 2-3 cümlelik özet + orijinal kaynağa link
  (uzun makale değil — daha az maliyet, daha az telif riski).
- **Hosting**: `higgsfield-websites` altyapısı (React 19 + TanStack Start,
  Cloudflare Worker + D1).

## Önemli mimari not (skill dokümanlarından doğrulandı)

`higgsfield website deploy` **kullanıcının kendi Cloudflare hesabına değil**,
Higgsfield'in kendi platform CI'sine deploy eder ("sandbox'ın Cloudflare
token'ı yok, deploy'u güvenilir platform CI yapar"). Bu yüzden:
- `wrangler login` / kullanıcının kendi Cloudflare hesabı **bu proje için
  gerekmiyor** — önceki oturumdaki Cloudflare token/DNS notları burada
  geçerli değil, çünkü Cloudflare hesabına biz deploy etmiyoruz.
- Altyapı (D1/R2/KV) `app/app.manifest.json` içinde **opt-in** olarak
  tanımlanır; platform bunu deploy anında provision eder.
- Manifest'te native bir "cron trigger" opsiyonu **yok** (sadece db/r2/kv/
  durableObject/container var). Yani içerik toplama otomasyonunu Cloudflare'in
  kendi Cron Trigger'ı ile Worker içinde çalıştırmak bu platformda desteklenen
  bir yol değil.

## Otomasyon mekanizması — karar

**Seçilen yöntem: Claude Code `schedule` skill'i ile bulutta çalışan periyodik
bir cron agent.** Bu agent her tetiklendiğinde:
1. `WebSearch` ile güncel/popüler global futbol haberlerini arar,
2. Her konu için 2-3 cümlelik özet + kaynak linki + kaynak adı + varsa
   lig/kategori etiketi hazırlar,
3. Bunları sitenin deploy edilmiş Worker'ındaki korumalı bir API route'a
   (`POST /api/ingest-topics`) bir gizli token ile gönderir,
4. Route, D1'e "aynı `source_url` zaten varsa ekleme" mantığıyla (dedup) yazar.

Bunun tercih edilme nedeni: platform manifestinde native cron desteği
olmadığından, tek pratik yol otomasyonu Claude Code'un kendi cron
altyapısında (`/schedule`) çalıştırıp sonucu siteye bir API çağrısıyla
push etmek. Alternatif olarak ileride Higgsfield platformu native cron
desteği eklerse, aynı mantık (arama → özet → D1'e yaz) bir Worker cron
handler'ına taşınabilir — mimari bunu değiştirmeye izin verecek şekilde
(ayrı, saf bir "ingest" fonksiyonu) kurulacak.

## Veri modeli — D1 şeması

`app/migrations/0001_topics.sql`:
```sql
CREATE TABLE IF NOT EXISTS topics (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  source_url TEXT NOT NULL UNIQUE,
  source_name TEXT,
  competition TEXT,
  image_url TEXT,
  discovered_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_topics_discovered_at ON topics(discovered_at DESC);
```
- Dedup: `source_url` üzerinde `UNIQUE` — ingest route `INSERT OR IGNORE` kullanır.
- Retention: ingest route her çalıştığında `discovered_at`'i 30 günden eski
  satırları siler (akışın sınırsız büyümesini önler).

## Site yapısı

- **Ana sayfa** (`app/src/routes/index.tsx`): en yeni konular, tarihe göre
  azalan sırada, kart listesi (başlık, özet, kaynak adı + link, lig etiketi).
  `createServerFn` ile D1'den okur (`bindings().DB`).
- **Lig/kategori filtresi** (opsiyonel, basit): query param ile filtreleme.
- **`/api/ingest-topics`** (`app/src/routes/api/ingest-topics.ts`): `POST`,
  `Authorization` header'daki secret token'ı doğrular, gövdeyi validate eder,
  D1'e `INSERT OR IGNORE` yapar + eski kayıtları temizler.
- SEO altyapısı (`robots.txt`, `sitemap.xml`, canonical) skill'in zorunlu
  kıldığı standart route'larla eklenir.

## Adım adım kurulum

1. `higgsfield-websites` skill'i `--type website` ile başlatılır; skill'in
   kendi zorunlu intake sorularını (Animasyonlu/Animasyonsuz site, marka
   tercihleri) build sırasında bize soracak — bu plan onları önceden
   cevaplamıyor, build anında sorulacak.
2. `app/app.manifest.json` içinde `"db": true` ile D1 opt-in edilir.
3. `app/migrations/0001_topics.sql` yukarıdaki şema ile eklenir.
4. Ana sayfa + `/api/ingest-topics` route'u yukarıdaki mantıkla yazılır.
5. `higgsfield website secrets set <website_id> --name INGEST_TOKEN --value <rastgele-token>`
   ile ingest route'un secret'ı ayarlanır.
6. `higgsfield website deploy <website_id>` ile site canlıya alınır; canlı URL
   not edilir.
7. `/schedule` skill'i ile 6 saatte bir çalışan bir cloud cron agent kurulur;
   promptu: "Global futbolda şu an popüler/gündemde olan 5-10 haberi
   `WebSearch` ile bul, her biri için 2-3 cümlelik özet + kaynak linki hazırla,
   `<canlı-url>/api/ingest-topics`'e `INGEST_TOKEN` ile POST et."
8. Cron agent bir kez elle tetiklenir, D1'e yeni satırlar düştüğü ve ana
   sayfada göründüğü doğrulanır.

## Doğrulama

- Deploy sonrası ana sayfa açılıp boş/placeholder olmadığı görülür.
- Ingest route'a elle bir test POST'u yapılıp D1'e satır düştüğü, sayfada
  göründüğü kontrol edilir.
- Cron agent bir kez manuel tetiklenip aynı akışın uçtan uca çalıştığı
  (arama → özet → POST → D1 → sayfa) doğrulanır.
- Aynı haber tekrar bulunduğunda `source_url` dedup'unun ikinci kaydı
  eklemediği kontrol edilir.
- Site canlı URL'i bu makineden hemen açılmazsa (yeni domain DNS gecikmesi
  bilinen bir durum), başka bir ağdan/telefon üzerinden doğrulanır.
