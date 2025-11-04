import os
import platform
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.parse import urlparse

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

APP_TITLE = "GSC Sitemap Submitter — Metro UI"
SCOPES = ["https://www.googleapis.com/auth/webmasters"]

# -------------------- OAuth --------------------
def get_credentials(log_fn):
    if os.path.exists("token.json"):
        log_fn("Mevcut token.json bulundu, kimlik doğrulanıyor…")
        return Credentials.from_authorized_user_file("token.json", SCOPES)
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("credentials.json yok! Google Cloud → OAuth 'Desktop app' oluşturup bu klasöre koyun.")
    log_fn("Tarayıcı ile OAuth akışı başlatılıyor…")
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    log_fn("OAuth tamamlandı, token.json kaydedildi.")
    return creds

# -------------------- Helpers --------------------
def base_prefix_from_sitemap(sitemap_url: str) -> str:
    p = urlparse(sitemap_url.strip())
    if not p.scheme or not p.netloc:
        raise ValueError("Geçersiz URL (şema/host yok)")
    return f"{p.scheme}://{p.netloc}/"

def is_probably_sitemap(u: str) -> bool:
    u = u.strip().lower()
    return u.endswith(".xml") or "sitemap" in u

# -------------------- Metro App --------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x680")
        self.minsize(900, 560)

        self.service = None
        self._apply_metro_style()
        self._build_ui()
        self._make_responsive()

    # ---------- Metro Style ----------
    def _apply_metro_style(self):
        self.P_BG      = "#0f172a"
        self.P_CARD    = "#111827"
        self.P_SURFACE = "#1f2937"
        self.P_ACCENT  = "#22c55e"
        self.P_ACCENT_D= "#16a34a"
        self.P_TEXT    = "#e5e7eb"
        self.P_MUTED   = "#9ca3af"
        self.P_ERR     = "#ef4444"
        self.P_INFO    = "#38bdf8"

        self.configure(bg=self.P_BG)
        base_font = "Segoe UI" if platform.system() == "Windows" else "Helvetica"
        self.option_add("*Font", (base_font, 10))

        style = ttk.Style(self)
        try: style.theme_use("clam")
        except Exception: pass

        style.configure("Card.TFrame", background=self.P_SURFACE)
        style.configure("Subtle.TFrame", background=self.P_CARD)
        style.configure("TLabel", background=self.P_BG, foreground=self.P_TEXT)
        style.configure("Card.TLabel", background=self.P_SURFACE, foreground=self.P_TEXT)
        style.configure("Muted.TLabel", background=self.P_BG, foreground=self.P_MUTED)
        style.configure("TEntry", fieldbackground="#0b1220", foreground=self.P_TEXT, insertcolor=self.P_TEXT)
        style.configure("Accent.TButton", background=self.P_ACCENT, foreground="#0b0f1a", borderwidth=0)
        style.map("Accent.TButton", background=[("active", self.P_ACCENT_D)])
        style.configure("Ghost.TButton", background=self.P_SURFACE, foreground=self.P_TEXT, borderwidth=0)
        style.map("Ghost.TButton", background=[("active", "#2a3648")])

    # ---------- UI ----------
    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Subtle.TFrame", padding=(18, 16))
        header.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 8))
        title = ttk.Label(header, text="🗺️ GSC Sitemap Submitter", style="Card.TLabel")
        title.configure(font=("Segoe UI", 16, "bold"))
        subtitle = ttk.Label(header, text="Sitemap URL’lerini yükle, GSC’ye gönder, listele, durum kontrolü yap.",
                             style="Card.TLabel")
        subtitle.configure(foreground=self.P_MUTED)
        actbar = ttk.Frame(header, style="Subtle.TFrame")
        self.btn_auth = ttk.Button(actbar, text="🔐 Google ile Yetkilendir", style="Accent.TButton", command=self.on_auth)
        self.lbl_status = ttk.Label(actbar, text="Durum: Bağlı değil", style="Card.TLabel")
        title.grid(row=0, column=0, sticky="w")
        actbar.grid(row=0, column=1, sticky="e")
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6,0))
        self.btn_auth.grid(row=0, column=0, padx=(0,10))
        self.lbl_status.grid(row=0, column=1)

        # Body shell
        shell = ttk.Frame(self, style="Card.TFrame", padding=10)
        shell.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))

        # Left: list
        left = ttk.Frame(shell, style="Card.TFrame", padding=8)
        left.grid(row=0, column=0, sticky="nsew")
        ttk.Label(left, text="📄 Sitemap URL listesi:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.listbox = tk.Listbox(left, selectmode="extended", bg="#0b1220", fg=self.P_TEXT, relief="flat")
        self.listbox.grid(row=1, column=0, sticky="nsew", pady=(6,4))
        lb_scroll = ttk.Scrollbar(left, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=lb_scroll.set)
        lb_scroll.grid(row=1, column=1, sticky="ns")

        controls = ttk.Frame(left, style="Card.TFrame")
        controls.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4,0))
        ttk.Button(controls, text="📂 .txt Yükle", style="Ghost.TButton", command=self.on_load_txt).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="➕ Elle Ekle", style="Ghost.TButton", command=self.on_add_manual).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="🗑️ Seçileni Sil", style="Ghost.TButton", command=self.on_delete_selected).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="🧹 Temizle", style="Ghost.TButton", command=self.on_clear_all).pack(side="left", padx=(0,6))

        # NEW buttons
        ttk.Button(controls, text="📜 Mevcut Sitemap’leri Listele", style="Ghost.TButton", command=self.on_list_existing).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="🔍 Durum Kontrolü", style="Ghost.TButton", command=self.on_check_status).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="📊 Performans Verilerini Getir", style="Ghost.TButton", command=self.on_fetch_performance).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="📤 Listelenenleri Submit Et", style="Ghost.TButton", command=self.on_resubmit_listed).pack(side="left", padx=(0,6))

        # Right: log
        right = ttk.Frame(shell, style="Card.TFrame", padding=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(10,0))
        ttk.Label(right, text="📜 Log:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.txt_log = tk.Text(right, height=10, wrap="word", bg="#0b1220", fg=self.P_TEXT, relief="flat", padx=10, pady=10)
        self.txt_log.grid(row=1, column=0, sticky="nsew", pady=(6,4))
        log_scroll = ttk.Scrollbar(right, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=log_scroll.set)
        log_scroll.grid(row=1, column=1, sticky="ns")
        
        ttk.Label(right, text="📊 Performans Özeti:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=(10,2))
        self.txt_perf = tk.Text(right, height=8, wrap="word", bg="#0b1220", fg=self.P_INFO, relief="flat", padx=10, pady=10)
        self.txt_perf.grid(row=3, column=0, sticky="nsew", pady=(4,4))
        perf_scroll = ttk.Scrollbar(right, orient="vertical", command=self.txt_perf.yview)
        self.txt_perf.configure(yscrollcommand=perf_scroll.set)
        perf_scroll.grid(row=3, column=1, sticky="ns")


        # Footer
        footer = ttk.Frame(self, style="Subtle.TFrame", padding=(10, 8))
        footer.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0,12))
        ttk.Button(footer, text="💾 Log Kaydet (.txt)", style="Ghost.TButton", command=self.on_save_log).pack(side="left")
        self.btn_submit = ttk.Button(footer, text="🚀 Seçilenleri Submit Et", style="Accent.TButton", command=self.on_submit_selected)
        self.btn_submit.pack(side="right")

        self._log("Uygulama hazır. OAuth yap, sitemap’leri yükle veya listele.")

        # Grid configs
        shell.grid_rowconfigure(0, weight=1)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_columnconfigure(1, weight=1)
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)
        
      
    def on_list_existing(self):
        if self.service is None:
            return messagebox.showwarning("Uyarı", "Önce OAuth yapın.")
        self.listbox.delete(0, tk.END)
        self._log("Sitemap listesi alınıyor, lütfen bekleyin...")
    
        def run():
            try:
                total_sitemaps = 0
                site_urls = self.service.sites().list().execute().get("siteEntry", [])
                for site in site_urls:
                    site_url = site.get("siteUrl")
                    self._log(f"🌐 Site: {site_url}")
                    try:
                        sitemaps = self.service.sitemaps().list(siteUrl=site_url).execute().get("sitemap", [])
                        for sm in sitemaps:
                            sm_path = sm.get("path")
                            # 🧩 path göreliyse site_url ile birleştir
                            if sm_path.startswith("/"):
                                sm_url = site_url.rstrip("/") + sm_path
                            else:
                                sm_url = sm_path
                            # Listeye ve log’a ekle
                            self.listbox.insert(tk.END, sm_url)
                            self._log(f"   • {sm_url} (Last submitted: {sm.get('lastSubmitted')})")
                            total_sitemaps += 1
                    except HttpError as e:
                        self._log(f"   ⚠️ Sitemap bilgisi alınamadı: {e}")
    
                # 🧾 Özet log ve kullanıcıya bilgi kutusu
                self._log(f"Toplam {total_sitemaps} sitemap bulundu ve listeye eklendi.")
                messagebox.showinfo("Listeleme Tamamlandı", f"Toplam {total_sitemaps} sitemap bulundu ve listeye eklendi.")
                
            except Exception as e:
                self._log(f"HATA (listeleme): {e}")
    
        threading.Thread(target=run, daemon=True).start()
    
    
    def on_resubmit_listed(self):
        if self.service is None:
            return messagebox.showwarning("Uyarı", "Önce OAuth yapın.")
    
        # Liste içeriğinde sitemap URL'leri var mı kontrol et
        all_items = [self.listbox.get(i) for i in range(self.listbox.size())]
        sitemaps = [u.strip() for u in all_items if u.strip().endswith(".xml")]
    
        if not sitemaps:
            return messagebox.showinfo("Bilgi", "Listede gönderilecek sitemap bulunamadı.")
    
        if not messagebox.askyesno("Onay", f"{len(sitemaps)} sitemap yeniden submit edilecek. Devam edilsin mi?"):
            return
    
        def run():
            ok = 0
            for i, sm_url in enumerate(sitemaps, 1):
                try:
                    prefix = base_prefix_from_sitemap(sm_url)
                    self._log(f"[{i}/{len(sitemaps)}] Yeniden Submit → {sm_url}")
                    self.service.sitemaps().submit(siteUrl=prefix, feedpath=sm_url).execute()
                    self._log(f"✅ Gönderildi: {sm_url}")
                    ok += 1
                except Exception as e:
                    self._log(f"❌ Hata: {sm_url} — {e}")
            self._log(f"Tamamlandı. Başarılı: {ok}/{len(sitemaps)}")
            messagebox.showinfo("Tamamlandı", f"Başarılı: {ok}/{len(sitemaps)}")
        threading.Thread(target=run, daemon=True).start()
          
    def on_fetch_performance(self):
        if self.service is None:
            return messagebox.showwarning("Uyarı", "Önce OAuth yapın.")
    
        self.listbox.delete(0, tk.END)
        self.txt_perf.delete("1.0", tk.END)
    
        def run():
            try:
                sites = self.service.sites().list().execute().get("siteEntry", [])
                if not sites:
                    return self._log("Hiç doğrulanmış site bulunamadı.")
                self._log(f"{len(sites)} site bulundu. Performans verileri alınıyor…")
    
                import datetime
                end_date = datetime.date.today()
                start_date = end_date - datetime.timedelta(days=7)
    
                self.site_performance = {}
    
                for site in sites:
                    site_url = site.get("siteUrl")
                    try:
                        result = self.service.searchanalytics().query(
                            siteUrl=site_url,
                            body={
                                "startDate": start_date.isoformat(),
                                "endDate": end_date.isoformat(),
                                "dimensions": []
                            }
                        ).execute()
    
                        rows = result.get("rows", [])
                        clicks = impressions = ctr = position = 0.0
                        if rows:
                            for row in rows:
                                clicks += row.get("clicks", 0)
                                impressions += row.get("impressions", 0)
                                ctr += row.get("ctr", 0)
                                position += row.get("position", 0)
                            ctr = (ctr / len(rows)) * 100
                            position = position / len(rows)
    
                        info = {
                            "clicks": clicks,
                            "impressions": impressions,
                            "ctr": round(ctr, 2),
                            "position": round(position, 2)
                        }
                        self.site_performance[site_url] = info
                        self.listbox.insert(tk.END, site_url)
                        self._log(f"📊 {site_url} — {clicks:.0f} tıklama, {impressions:.0f} gösterim")
                    except Exception as e:
                        self._log(f"⚠️ {site_url} performans alınamadı: {e}")
    
                self._log("Performans verileri alındı. Sol listeden bir site seçin.")
                self.listbox.bind("<<ListboxSelect>>", self._show_site_performance)
    
            except Exception as e:
                self._log(f"HATA (performans): {e}")
    
        threading.Thread(target=run, daemon=True).start()
    
    
    def _show_site_performance(self, event=None):
        if not hasattr(self, "site_performance"):
            return
        sel = self.listbox.curselection()
        if not sel:
            return
        site_url = self.listbox.get(sel[0])
        perf = self.site_performance.get(site_url)
        if not perf:
            return
        self.txt_perf.delete("1.0", tk.END)
        self.txt_perf.insert(tk.END,
            f"📍 Site: {site_url}\n\n"
            f"Son 7 Gün:\n"
            f"• Tıklama: {perf['clicks']:.0f}\n"
            f"• Gösterim: {perf['impressions']:.0f}\n"
            f"• CTR: {perf['ctr']}%\n"
            f"• Ortalama Pozisyon: {perf['position']}\n"
        )
    
    def _make_responsive(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # ---------- Events ----------
    def on_auth(self):
        def run():
            try:
                self._log("OAuth başlatılıyor…")
                creds = get_credentials(self._log)
                self.service = build("webmasters", "v3", credentials=creds)
                self.lbl_status.config(text="Durum: Bağlı")
                self._log("Google Search Console servisi hazır.")
            except Exception as e:
                self._log(f"HATA (OAuth): {e}")
                messagebox.showerror("Hata", str(e))
        threading.Thread(target=run, daemon=True).start()

    def on_load_txt(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()
        path = filedialog.askopenfilename(
            title="Sitemap URL listesi (.txt)",
            filetypes=[("Text", "*.txt"), ("All files", "*.*")],
            initialdir=base_dir
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            for ln in lines:
                if is_probably_sitemap(ln):
                    self.listbox.insert(tk.END, ln)
            self._log(f"{len(lines)} satır yüklendi: {os.path.basename(path)}")
        except Exception as e:
            self._log(f"HATA (.txt): {e}")
            messagebox.showerror("Hata", str(e))

    def on_add_manual(self):
        def add():
            url = ent.get().strip()
            if not url:
                return
            self.listbox.insert(tk.END, url)
            win.destroy()
        win = tk.Toplevel(self)
        win.title("Sitemap URL ekle")
        win.configure(bg=self.P_BG)
        ttk.Label(win, text="Sitemap URL:", style="TLabel").pack(anchor="w", padx=10, pady=(10,2))
        ent = ttk.Entry(win, width=60)
        ent.pack(padx=10, pady=4)
        ent.focus_set()
        ttk.Button(win, text="Ekle", style="Accent.TButton", command=add).pack(pady=(0,10))

    def on_delete_selected(self):
        sel = list(self.listbox.curselection())
        sel.reverse()
        for idx in sel:
            self.listbox.delete(idx)

    def on_clear_all(self):
        self.listbox.delete(0, tk.END)

    def on_submit_selected(self):
        if self.service is None:
            return messagebox.showwarning("Uyarı", "Önce OAuth ile yetkilendirin.")
        sel = self.listbox.curselection()
        indices = sel if sel else range(self.listbox.size())
        urls = [self.listbox.get(i) for i in indices]
        if not urls:
            return messagebox.showinfo("Bilgi", "Gönderilecek URL yok.")
        if not messagebox.askyesno("Onay", f"{len(urls)} sitemap gönderilecek, devam edilsin mi?"):
            return

        def run():
            ok = 0
            for i, u in enumerate(urls, 1):
                try:
                    prefix = base_prefix_from_sitemap(u)
                    self._log(f"[{i}/{len(urls)}] Submit → {u}")
                    self.service.sitemaps().submit(siteUrl=prefix, feedpath=u).execute()
                    self._log(f"✅ OK: {u}")
                    ok += 1
                except Exception as e:
                    self._log(f"❌ Hata: {u} — {e}")
            self._log(f"Tamamlandı. Başarılı: {ok}/{len(urls)}")
        threading.Thread(target=run, daemon=True).start()


    def on_check_status(self):
        if self.service is None:
            return messagebox.showwarning("Uyarı", "Önce OAuth yapın.")
        sel = self.listbox.curselection()
        urls = [self.listbox.get(i) for i in sel] if sel else [self.listbox.get(i) for i in range(self.listbox.size())]
        if not urls:
            return messagebox.showinfo("Bilgi", "Kontrol edilecek sitemap yok.")
        def run():
            for u in urls:
                try:
                    prefix = base_prefix_from_sitemap(u)
                    resp = self.service.sitemaps().get(siteUrl=prefix, feedpath=u).execute()
                    self._log(f"🔍 {u} → Status: {resp.get('isPending', False)}, LastDownload: {resp.get('lastDownloaded')}")
                except Exception as e:
                    self._log(f"❌ {u} — {e}")
        threading.Thread(target=run, daemon=True).start()

    def on_save_log(self):
        path = filedialog.asksaveasfilename(
            title="Log dosyasını kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialdir=os.getcwd()
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.txt_log.get("1.0", tk.END))
            self._log(f"💾 Log kaydedildi: {path}")
            messagebox.showinfo("Bilgi", f"Log kaydedildi:\n{path}")
        except Exception as e:
            self._log(f"HATA (log kaydetme): {e}")

    # ---------- Utils ----------
    def _log(self, msg: str):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()
