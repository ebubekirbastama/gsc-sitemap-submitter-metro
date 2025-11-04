# gsc_sitemap_submit_gui_metro.py
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
        self.geometry("980x640")
        self.minsize(900, 560)

        self.service = None

        self._apply_metro_style()
        self._build_ui()
        self._make_responsive()

    # ---------- Metro Style ----------
    def _apply_metro_style(self):
        # Palette
        self.P_BG      = "#0f172a"  # slate-900
        self.P_CARD    = "#111827"  # gray-900
        self.P_SURFACE = "#1f2937"  # gray-800
        self.P_ACCENT  = "#22c55e"  # emerald-500
        self.P_ACCENT_D= "#16a34a"  # emerald-600
        self.P_TEXT    = "#e5e7eb"  # gray-200
        self.P_MUTED   = "#9ca3af"  # gray-400
        self.P_ERR     = "#ef4444"  # red-500
        self.P_INFO    = "#38bdf8"  # sky-400

        self.configure(bg=self.P_BG)
        base_font = "Segoe UI" if platform.system() == "Windows" else "Helvetica"
        self.option_add("*Font", (base_font, 10))
        self.option_add("*TNotebook.TabPadding", [16, 8])
        self.option_add("*TButton.Padding", 8)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Containers
        style.configure("Card.TFrame", background=self.P_SURFACE)
        style.configure("Subtle.TFrame", background=self.P_CARD)
        style.configure("TLabel", background=self.P_BG, foreground=self.P_TEXT)
        style.configure("Card.TLabel", background=self.P_SURFACE, foreground=self.P_TEXT)
        style.configure("Muted.TLabel", background=self.P_BG, foreground=self.P_MUTED)

        # Inputs
        style.configure("TEntry", fieldbackground="#0b1220", foreground=self.P_TEXT, insertcolor=self.P_TEXT)
        style.configure("TCombobox", fieldbackground="#0b1220", foreground=self.P_TEXT)
        style.map("TEntry", fieldbackground=[("focus", "#0d1526")])

        # Buttons
        style.configure("Accent.TButton", background=self.P_ACCENT, foreground="#0b0f1a", borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", self.P_ACCENT_D)],
                  foreground=[("active", "#ffffff")])
        style.configure("Ghost.TButton", background=self.P_SURFACE, foreground=self.P_TEXT, borderwidth=0)
        style.map("Ghost.TButton", background=[("active", "#2a3648")])

        # LabelFrame
        style.configure("TLabelframe", background=self.P_CARD, foreground=self.P_TEXT, borderwidth=0)
        style.configure("TLabelframe.Label", background=self.P_CARD, foreground=self.P_MUTED)

    # ---------- UI ----------
    def _build_ui(self):
        # Header
        header = ttk.Frame(self, style="Subtle.TFrame", padding=(18, 16))
        header.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 8))

        title = ttk.Label(header, text="🗺️ GSC Sitemap Submitter", style="Card.TLabel")
        title.configure(font=(self.option_get("Font","") or "Segoe UI", 16, "bold"))
        subtitle = ttk.Label(header, text="Sitemap URL’lerini .txt’den yükle • Google Search Console’a toplu submit",
                             style="Card.TLabel")
        subtitle.configure(foreground=self.P_MUTED)

        actbar = ttk.Frame(header, style="Subtle.TFrame")
        self.btn_auth = ttk.Button(actbar, text="🔐 Google ile Yetkilendir (OAuth)",
                                   style="Accent.TButton", command=self.on_auth)
        self.lbl_status = ttk.Label(actbar, text="Durum: Bağlı değil", style="Card.TLabel")

        title.grid(row=0, column=0, sticky="w", padx=(2, 12))
        actbar.grid(row=0, column=1, sticky="e")
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", padx=(2, 12), pady=(6,0))
        self.btn_auth.grid(row=0, column=0, sticky="e", padx=(0, 10))
        self.lbl_status.grid(row=0, column=1, sticky="e")

        # Body shell
        shell = ttk.Frame(self, style="Card.TFrame", padding=10)
        shell.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))

        # Left: list
        left = ttk.Frame(shell, style="Card.TFrame", padding=8)
        left.grid(row=0, column=0, sticky="nsew")

        ttk.Label(left, text="📄 Sitemap URL listesi (.txt):", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.listbox = tk.Listbox(left, selectmode="extended",
                                  bg="#0b1220", fg=self.P_TEXT, relief="flat",
                                  highlightthickness=0)
        self.listbox.grid(row=1, column=0, sticky="nsew", pady=(6, 4))

        # Scrollbar for listbox
        lb_scroll = ttk.Scrollbar(left, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=lb_scroll.set)
        lb_scroll.grid(row=1, column=1, sticky="ns")

        controls = ttk.Frame(left, style="Card.TFrame")
        controls.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4,0))
        ttk.Button(controls, text="📂 .txt Yükle", style="Ghost.TButton", command=self.on_load_txt).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="➕ Elle Ekle", style="Ghost.TButton", command=self.on_add_manual).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="🗑️ Seçileni Sil", style="Ghost.TButton", command=self.on_delete_selected).pack(side="left", padx=(0,6))
        ttk.Button(controls, text="🧹 Temizle", style="Ghost.TButton", command=self.on_clear_all).pack(side="left")

        # Right: log
        right = ttk.Frame(shell, style="Card.TFrame", padding=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(10,0))

        ttk.Label(right, text="📜 Log:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.txt_log = tk.Text(right, height=10, wrap="word",
                               bg="#0b1220", fg=self.P_TEXT, insertbackground=self.P_TEXT,
                               relief="flat", padx=10, pady=10)
        self.txt_log.grid(row=1, column=0, sticky="nsew", pady=(6,4))

        log_scroll = ttk.Scrollbar(right, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=log_scroll.set)
        log_scroll.grid(row=1, column=1, sticky="ns")

        # Footer
        footer = ttk.Frame(self, style="Subtle.TFrame", padding=(10, 8))
        footer.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0,12))
        self.btn_submit = ttk.Button(footer, text="🚀 Seçilenleri Submit Et", style="Accent.TButton",
                                     command=self.on_submit_selected)
        self.btn_submit.pack(side="right")

        # Intro log
        self._log("Uygulama hazır. Önce OAuth ile yetkilendirin, ardından .txt dosyasını yükleyin.")

        # Grid weights inside shell
        shell.grid_rowconfigure(0, weight=1)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_columnconfigure(1, weight=1)

        # Left panel weights
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Right panel weights
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

    def _make_responsive(self):
        # Root grid weights (header, body, footer)
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
                self._log(f"HATA (OAuth/Service): {e}")
                messagebox.showerror("Hata", str(e))
        threading.Thread(target=run, daemon=True).start()

    def on_load_txt(self):
        # Çapraz platform başlangıç dizini (script’in bulunduğu klasör)
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            # Bazı ortamlarda (__file__) tanımsız olabilir
            base_dir = os.getcwd()
    
        path = filedialog.askopenfilename(
            title="Sitemap URL listesi (.txt)",
            filetypes=[("Text", "*.txt"), ("All files", "*.*")],
            initialdir=base_dir  # Çapraz platform dizin
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            added = 0
            for ln in lines:
                if is_probably_sitemap(ln):
                    self.listbox.insert(tk.END, ln)
                    added += 1
            self._log(f"Yüklendi: {path} — {added} satır eklendi.")
            if added == 0:
                messagebox.showwarning("Uyarı", ".txt içinde geçerli sitemap URL bulunamadı ('.xml' beklenir).")
        except Exception as e:
            self._log(f"HATA (.txt okuma): {e}")
            messagebox.showerror("Hata", str(e))
    

    def on_add_manual(self):
        def add():
            url = ent.get().strip()
            if not url:
                return
            if not is_probably_sitemap(url):
                messagebox.showwarning("Uyarı", "Bu URL bir sitemap gibi görünmüyor (.xml). Yine de eklendi.")
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
            messagebox.showwarning("Uyarı", "Önce OAuth ile yetkilendirin.")
            return

        sel = self.listbox.curselection()
        indices = sel if sel else range(self.listbox.size())
        urls = [self.listbox.get(i) for i in indices]

        if not urls:
            messagebox.showinfo("Bilgi", "Gönderilecek URL yok.")
            return

        if not messagebox.askyesno("Onay", f"{len(urls)} sitemap URL submit edilecek. Devam?"):
            return

        def run():
            ok_count = 0
            for i, u in enumerate(urls, 1):
                u = u.strip()
                try:
                    prefix = base_prefix_from_sitemap(u)
                    self._log(f"[{i}/{len(urls)}] Submit → site: {prefix} | feed: {u}")
                    self.service.sitemaps().submit(siteUrl=prefix, feedpath=u).execute()
                    self._log(f" ✅ OK: {u}")
                    ok_count += 1
                except HttpError as e:
                    self._log(f" ❌ HttpError: {u} — {e}")
                except Exception as e:
                    self._log(f" ❌ Hata: {u} — {e}")
            self._log(f"Tamamlandı. Başarılı: {ok_count}/{len(urls)}")
            messagebox.showinfo("Bitti", f"Başarılı: {ok_count}/{len(urls)}")

        threading.Thread(target=run, daemon=True).start()

    # ---------- Utils ----------
    def _log(self, msg: str):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()
