GSC Sitemap Submitter — Metro UI
=================================

Google Search Console'a (GSC) toplu sitemap bildirme işlemini tek tıkla yapan, modern Metro temalı bir masaüstü uygulaması.
Python + Tkinter ile geliştirilmiştir. OAuth ile güvenli giriş yapar, .txt içindeki tüm sitemap URL’lerini otomatik olarak GSC’ye gönderir.

------------------------------------------------------------
✨ ÖZELLİKLER
------------------------------------------------------------
🗂️ Toplu yükleme: .txt dosyasından sınırsız sitemap URL’i alır <br>
🧠 Akıllı site tespiti: https://ebubekirbastama.com/ kök URL’sini otomatik çıkartır<br>
🔐 Güvenli OAuth: credentials.json ile Google hesabınızda yetkilendirme<br>
🪟 Modern Metro UI: Koyu tema, kart yapısı, responsive düzen<br>
🧾 Anlık log: Her adımı canlı olarak görürsünüz (başarılı / hata)<br>
✅ GSC API v3: Resmî webmasters API ile uyumlu<br>

------------------------------------------------------------
🧭 KİMLER KULLANMALI?
------------------------------------------------------------
📰 Haber siteleri ve çoklu domain yöneten yayıncılar  
🛍️ E-ticaret ve pazaryeri işletmeleri  
🧰 SEO ajansları / uzmanları (müşterilerin GSC gönderimlerini hızlandırmak için)  
🧑‍💻 Web geliştiricileri (deployment sonrası sitemap süreçlerini otomatikleştirmek için)

------------------------------------------------------------
🤔 NEDEN BU ARAÇ?
------------------------------------------------------------
⏱️ Aynı işlemi GSC arayüzünde tek tek yapmak zaman alır  
🧩 Tüm sitelerinizi tek pencereden yönetirsiniz  
🛡️ OAuth sayesinde hesap güvenliği korunur  
✔️ Hata durumlarını ve başarıları net log ile görürsünüz

------------------------------------------------------------
🚀 HIZLI BAŞLANGIÇ
------------------------------------------------------------

1) GEREKSİNİMLER
- Python 3.9+
- Google Cloud Console erişimi (OAuth oluşturmak için)
- İlgili sitelerin GSC’de doğrulanmış olması

2) KURULUM
--------------------------------
git clone https://github.com/ebubekirbastama/gsc-sitemap-submitter-metro.git<br>
cd gsc-sitemap-submitter-metro<br>

python -m venv .venv
.venv\Scripts\activate   (Windows)
source .venv/bin/activate  (macOS/Linux)

pip install -r requirements.txt

3) GOOGLE OAUTH HAZIRLIĞI
--------------------------------
1. Google Cloud Console → APIs & Services → Credentials
2. Create Credentials → OAuth client ID
3. Application type: Desktop app
4. İndirilen dosyayı proje köküne "credentials.json" adıyla koyun
5. Search Console API’yi etkinleştirin

İlk çalıştırmada tarayıcıda OAuth onayı alınır ve otomatik olarak "token.json" kaydedilir.

4) ÇALIŞTIRMA
--------------------------------
python gsc_sitemap_submit_gui_metro.py

5) KULLANIM
--------------------------------
1. 🔐 Google ile Yetkilendir (OAuth)
2. 📂 .txt Yükle → sitemap URL’lerinizi içeren dosyayı seçin
3. ➕ Elle Ekle → tek tek URL girişi
4. 🚀 Seçilenleri Submit Et → GSC’ye gönderin

.txt Örnek:
https://alanadiniz.com/sitemap.xml
https://site2.com/sitemap_index.xml
https://site3.com/sitemaps/news.xml

------------------------------------------------------------
🧩 PROJE YAPISI
------------------------------------------------------------
gsc-sitemap-submitter-metro/<br>
├─ assets/<br>
│  ├─ hero.png<br>
│  ├─ submit.png<br>
│  └─ oauth.png<br>
├─ gsc_sitemap_submit_gui_metro.py<br>
├─ requirements.txt<br>
├─ .gitignore<br>
└─ README.txt<br>

------------------------------------------------------------
⚠️ SIK KARŞILAŞILAN HATALAR
------------------------------------------------------------
HttpError 403 → site doğrulanmamış veya yanlış hesap<br>
credentials.json yok → Cloud Console’dan OAuth client oluşturmalısınız<br>
invalid_grant → token.json silip yeniden yetkilendirin<br>
.txt hatası → her satır tam URL olmalı (.xml ile bitmeli)<br>

------------------------------------------------------------
🔐 GÜVENLİK NOTLARI
------------------------------------------------------------
- credentials.json ve token.json gizli dosyalardır<br>
- Versiyon kontrolüne dahil edilmemelidir<br>
- .gitignore bu dosyaları korur<br>

------------------------------------------------------------
🧭 YOL HARİTASI
------------------------------------------------------------
[ ] GSC’den mevcut sitemap’leri listeleme  
[ ] Submit loglarını CSV/JSON dışa aktarma  
[ ] Tema seçenekleri (açık/kapalı tema)  

------------------------------------------------------------
🤝 KATKIDA BULUNMA
------------------------------------------------------------
Pull request’ler ve issue’lar memnuniyetle kabul edilir!

------------------------------------------------------------
📄 LİSANS
------------------------------------------------------------
MIT Lisansı – Dilediğiniz gibi kullanın, geliştirin, özelleştirin.

------------------------------------------------------------
💬 SSS
------------------------------------------------------------
Bu araç Google’a ping atar mı?
→ Hayır, Search Console API ile resmi submit işlemi yapar.

XML olmayan URL eklenebilir mi?
→ Evet fakat araç uyarır; GSC yalnızca geçerli sitemap’leri işler.

Birden fazla domain ekleyebilir miyim?
→ Evet, .txt dosyasına satır satır ekleyin.

Sitemap index dosyası desteklenir mi?
→ Evet, sitemap_index.xml dosyalarını normal sitemap gibi submit edebilirsiniz.
