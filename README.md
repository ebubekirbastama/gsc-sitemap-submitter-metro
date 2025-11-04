# GSC Sitemap Submitter — Metro UI

Google Search Console'a (GSC) **toplu sitemap bildirme** işlemini tek tıkla yapan, modern Metro temalı bir masaüstü uygulaması.  
Python + Tkinter ile geliştirilmiştir. OAuth ile güvenli giriş yapar, `.txt` içindeki tüm sitemap URL’lerini otomatik olarak GSC’ye gönderir.

---

## 🖼️ Program Ekran Görüntüsü
![Uygulama Ekran Görüntüsü](s1.png)

---

## ✨ ÖZELLİKLER

- 🗂️ **Toplu yükleme:** `.txt` dosyasından sınırsız sitemap URL’i alır  
- 🧠 **Akıllı site tespiti:** `https://alanadiniz.com/sitemap.xml` içinden otomatik olarak `https://alanadiniz.com/` kök URL’sini çıkarır  
- 🔐 **Güvenli OAuth:** `credentials.json` ile Google hesabınızda yetkilendirme  
- 🪟 **Modern Metro UI:** Koyu tema, kart yapısı, responsive düzen  
- 🧾 **Anlık log:** Her adımı canlı olarak görürsünüz (başarılı / hata)  
- ✅ **GSC API v3:** Resmî webmasters API ile uyumlu  
- 💾 **Log kaydet:** Uygulama içindeki log’u tek tuşla `.txt` olarak dışa aktarabilirsiniz  
- 🧰 **Çapraz platform:** Windows ve Linux ile uyumlu  

---

## 🆕 Yeni Eklenen Araç (Tools) Özellikleri

### 📜 Mevcut Sitemap’leri Listele
- GSC’de doğrulanmış tüm siteleri çeker  
- Her site için GSC’de kayıtlı sitemap’leri listeler  
- Bulunan tüm sitemap URL’lerini **listeye otomatik ekler**  
- İşlem sonunda şu uyarı çıkar:  
  > “Toplam X sitemap bulundu ve listeye eklendi.”  
- Eğer path yalnızca `/sitemap.xml` şeklindeyse otomatik olarak tam URL’ye dönüştürür (`https://site.com/sitemap.xml`)

---

### 📤 Listelenenleri Submit Et
- GSC’den çekilen tüm sitemap’leri yeniden GSC’ye gönderir  
- Kaç sitemap gönderileceğini kullanıcıdan onay alır  
- Log’da her adımı gösterir (`✅ Gönderildi` / `❌ Hata`)  
- Tüm sitemap’lerin hızlı şekilde “refresh” edilmesini sağlar  

---

### 🔍 Durum Kontrolü
- Listedeki sitemap’lerin GSC üzerindeki durumunu kontrol eder  
- “pending” mi, “son indirildiği tarih” ne zaman, hata var mı — hepsini log’da gösterir  
- GSC paneline girmeden sitemap durumlarını görmenizi sağlar  

---

### 📊 Performans Verilerini Getir (Search Analytics Özeti)
- GSC’deki doğrulanmış tüm siteler için son **7 günlük performansı** getirir  
- Veriler:  
  - Tıklama  
  - Gösterim  
  - Ortalama CTR  
  - Ortalama Pozisyon  
- Sol listeye site URL’lerini yazar  
- Sağ tarafta “📊 Performans Özeti” panelinde detayları gösterir  

---

### 💾 Log Kaydet (.txt)
- Sağdaki log alanındaki tüm içeriği `.txt` dosyası olarak kaydeder  
- Özellikle çoklu domain yönetiminde hata analizi için kullanışlıdır  

---

## 🧭 KİMLER KULLANMALI?

- 📰 Haber siteleri ve çoklu domain yöneten yayıncılar  
- 🛍️ E-ticaret ve pazaryeri işletmeleri  
- 🧰 SEO ajansları ve uzmanları  
- 🧑‍💻 Web geliştiricileri (deployment sonrası sitemap süreçlerini hızlandırmak için)

---

## 🤔 NEDEN BU ARAÇ?

- ⏱️ Aynı işlemi GSC arayüzünde tek tek yapmak zaman alır  
- 🧩 Tüm sitelerinizi tek pencereden yönetirsiniz  
- 🛡️ OAuth sayesinde hesap güvenliği korunur  
- ✔️ Hata ve başarı log’larını anlık görürsünüz  
- 📊 Artık sitemap yönetimi + performans analizi aynı ekrandan yapılabilir  

---

## 🚀 HIZLI BAŞLANGIÇ

### 1️⃣ Gereksinimler
- Python 3.9+  
- Google Cloud Console erişimi (OAuth oluşturmak için)  
- GSC üzerinde doğrulanmış web siteler  

---

### 2️⃣ Kurulum
```bash
git clone https://github.com/ebubekirbastama/gsc-sitemap-submitter-metro.git
cd gsc-sitemap-submitter-metro

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

### 3️⃣ Google OAuth Hazırlığı
1. Google Cloud Console → APIs & Services → Credentials  
2. **Create Credentials → OAuth client ID**  
3. Application type: **Desktop app**  
4. İndirilen dosyayı proje köküne `credentials.json` adıyla koyun  
5. **Search Console API**’yi etkinleştirin  
6. İlk çalıştırmada tarayıcıdan izin verilir ve `token.json` kaydedilir  

---

### 4️⃣ Çalıştırma
```bash
python gsc_sitemap_submit_gui_metro.py
```

---

### 5️⃣ Kullanım Akışı
1. **🔐 Google ile Yetkilendir**  
2. **📂 .txt Yükle** veya **📜 Mevcut Sitemap’leri Listele**  
3. **🚀 Seçilenleri Submit Et** veya **📤 Listelenenleri Submit Et**  
4. **🔍 Durum Kontrolü** → sitemap durumlarını görüntüle  
5. **📊 Performans Verilerini Getir** → son 7 günün özetini al  
6. **💾 Log Kaydet (.txt)** → tüm işlemleri dışa aktar  

---

#### 📄 .txt Örnek:
```text
https://alanadiniz.com/sitemap.xml
https://site2.com/sitemap_index.xml
https://site3.com/sitemaps/news.xml
```

---

## 🧩 PROJE YAPISI
```text
gsc-sitemap-submitter-metro/
├─ gsc_sitemap_submit_gui_metro.py
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## ⚠️ SIK KARŞILAŞILAN HATALAR

- **HttpError 403** → site doğrulanmamış veya yanlış hesap  
- **credentials.json yok** → Cloud Console’dan oluşturun  
- **invalid_grant** → `token.json` silip yeniden yetkilendirin  
- **“Listede gönderilecek sitemap bulunamadı.”** → GSC’den listeleme yapmadıysanız bu normaldir  
- **.txt hatası** → her satır tam URL olmalı (`.xml` ile bitmeli)  

---

## 🔐 GÜVENLİK NOTLARI
- `credentials.json` ve `token.json` gizli dosyalardır  
- Versiyon kontrolüne dahil edilmemelidir  
- `.gitignore` bu dosyaları kapsar  

---

## 🧭 YOL HARİTASI
- [x] GSC’den mevcut sitemap’leri listeleme  
- [x] Listelenen sitemap’leri tekrar submit etme  
- [x] Durum kontrolü (sitemaps.get)  
- [x] Performans (Search Analytics) özet paneli  
- [x] Log dışa aktarma  
- [ ] Tema seçenekleri (açık / koyu)  
- [ ] Çoklu kullanıcı profili  
- [ ] CLI modu  

---

## 🤝 KATKIDA BULUNMA
Pull request’ler ve issue’lar memnuniyetle kabul edilir!

---

## 📄 LİSANS
MIT Lisansı – Dilediğiniz gibi kullanın, geliştirin, özelleştirin.

---
