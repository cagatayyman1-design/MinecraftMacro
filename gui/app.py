import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import StringVar
import tkinter as tk
from functools import partial
from utils.profile_manager import load_data, save_data
from core.macro_engine import AutoClicker

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ─── PORTABLE SCRIPT CONTENTS ───────────────────────────────────────────────
BAT_SEKMEME = r"""@echo off
color 0b
title Sekmeme ^& Ping Optimizer - SKY PROJECT
echo [!] SonOyuncu Sekmeme ^& Ping Optimizer Calistiriliyor...
echo.
echo [1/4] Winsock Katalogu Sifirlaniyor...
netsh winsock reset >nul
echo [2/4] IP Protokolleri Sifirlaniyor...
netsh int ip reset >nul
echo [3/4] DNS Onbellesi Temizleniyor...
ipconfig /flushdns >nul
echo [4/4] TCP Otomatik Ayarlama Devre Disi Birakiliyor (Stabil Ping)...
netsh int tcp set global autotuninglevel=disabled >nul
netsh int tcp set global rss=enabled >nul
echo.
echo [TAMAM] Optimizasyonlar Uygulandi! 
echo Not: Etkiyi gormek icin Minecraft'i yeniden baslatin.
echo.
pause"""

BAT_HITFIX = r"""@echo off
color 0d
title TCP Hit Registration Fix - SKY PROJECT
echo [!] Hit Iyilestirme ^& Paket Stabilizasyonu Baslatiliyor...
echo.
echo [1/3] Nagle Algoritmasi Optimizasyonu...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" /v TcpAckFrequency /t REG_DWORD /d 1 /f >nul 2>nul
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces" /v TcpNoDelay /t REG_DWORD /d 1 /f >nul 2>nul
echo [2/3] Netsh Arayuzu TCP Ayarlari...
netsh interface tcp set global sack=enabled >nul 2>nul
netsh interface tcp set global ecncapability=disabled >nul 2>nul
netsh interface tcp set global timestamps=disabled >nul 2>nul
echo [3/3] Winsock Katalogu Yenileniyor...
netsh winsock reset catalog >nul 2>nul
echo.
echo [TAMAM] Hit Kayitlari Iyilestirildi!
echo Not: Kayit defteri degisiklikleri icin bilgisayari baslatmaniz onerilir.
echo.
pause"""

# ─────────────────────────── APPLE VIBE RENK PALETİ (LIGHT) ──────────────────────────
BG            = "#fbfbfd"  # Apple Ultra Light Gray
BG_PANEL      = "#ffffff"  # White Card
BG_SIDEBAR    = "#f5f5f7"  # App System Gray 6
BG_CARD       = "#ffffff"  # Pure White
BG_INPUT      = "#f2f2f7"  # System Gray 5
BG_TAG        = "#e5e5ea"  # Pill background
BG_HOVER      = "#e5e5ea"  
BG_GLASS      = "#ffffff"  

BORDER        = "#d1d1d6"  # System border
BORDER_LITE   = "#e5e5ea"  
BORDER_ORANGE = "#ff9f0a"
BORDER_GREEN  = "#34c759"
BORDER_GLOW   = "#007aff"  

TXT           = "#1d1d1f"  # Apple extremely dark gray
TXT_MED       = "#86868b"  # Secondary label
TXT_MUTED     = "#a1a1a6"  # Tertiary label
TXT_ORANGE    = "#ff9f0a"
TXT_GREEN     = "#34c759"  
TXT_RED       = "#ff3b30"  
TXT_CYAN      = "#32ade6"  
TXT_PURPLE    = "#af52de"  

ACC           = "#007aff"  # Apple System Blue
ACC_HOT       = "#005bb5"  
ACC_DIM       = "#e6f2ff"  # Light blue glow
ACC_GLOW      = "#007aff"  
ACC_ORANGE    = "#fff5e6"  
ACC_ORG_DIM   = "#fff5e6"
ACC_GREEN_DIM = "#eaffed"

# ─────────────────────────── TETİK SEÇENEKLERİ ────────────────────────────────
TRIGGER_OPTS = {
    "Sol Tık"   : "left",
    "Sağ Tık"   : "right",
    "Orta Tık"  : "mid",
    "Mouse 4"   : "x1",
    "Mouse 5"   : "x2",
}
TRIGGER_LABELS = {v: k for k, v in TRIGGER_OPTS.items()}   # ters tablo

TRIGGER_ICONS = {
    "left":  "🖱L",
    "right": "🖱R",
    "mid":   "🖱M",
    "x1":    "M4",
    "x2":    "M5",
}


def resource_path(rel):
    try:    base = sys._MEIPASS
    except: base = os.path.abspath(".")
    return os.path.join(base, rel)


# ─────────────────────────── EYLEM SATIRI ─────────────────────────────────────
class ActionRow(ctk.CTkFrame):
    def __init__(self, master, index, icon, name, is_timer=False,
                 move_up=None, move_down=None, delete=None, **kw):
        accent = TXT_CYAN if is_timer else TXT_PURPLE
        glow   = "#e6f7ff" if is_timer else "#f4e6ff"  # Light glows
        super().__init__(master, fg_color=BG_CARD, corner_radius=16,
                         border_width=1, border_color=BORDER_LITE, **kw)
        self.grid_columnconfigure(2, weight=1)

        # index pill badge
        badge = ctk.CTkFrame(self, fg_color=glow, corner_radius=12, width=32, height=32)
        badge.grid(row=0, column=0, padx=(12, 6), pady=10)
        badge.grid_propagate(False)
        ctk.CTkLabel(badge, text=f"{index:02d}",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=accent).place(relx=.5, rely=.5, anchor="center")

        # icon pill
        i_f = ctk.CTkFrame(self, fg_color=glow, corner_radius=12,
                           border_width=0, width=32, height=32)
        i_f.grid(row=0, column=1, padx=(0, 8), pady=10)
        i_f.grid_propagate(False)
        ctk.CTkLabel(i_f, text=icon, font=("Segoe UI Emoji", 14),
                     text_color=accent).place(relx=.5, rely=.5, anchor="center")

        # name
        ctk.CTkLabel(self, text=name, text_color=TXT,
                     font=ctk.CTkFont(size=13), anchor="w").grid(
            row=0, column=2, sticky="ew", padx=(0, 8), pady=10)

        # controls - tam yuvarlak pill butonlar
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.grid(row=0, column=3, padx=(0, 12), pady=10)
        for sym, cmd, danger in [("↑", move_up, False), ("↓", move_down, False), ("✕", delete, True)]:
            fg  = "#ffe5e5" if danger else BG_HOVER
            tc  = TXT_RED  if danger else TXT_MED
            hov = "#ffcccc" if danger else "#d1d1d6"
            ctk.CTkButton(ctrl, text=sym, width=28, height=28, corner_radius=14,
                          fg_color=fg, hover_color=hov, text_color=tc,
                          border_width=0,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          command=cmd, cursor="hand2").pack(side="left", padx=2)


# ─────────────────────────── KART / BÖLÜM YARDIMCIları ───────────────────────
def make_card(parent, row=None, col=0, padx=14, pady=(0, 10)):
    f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=20,
                     border_width=1, border_color=BORDER)
    if row is not None:
        f.grid(row=row, column=col, sticky="ew", padx=padx, pady=pady)
    f.grid_columnconfigure(0, weight=1)
    return f


def section_label(parent, text, row):
    ctk.CTkLabel(parent, text=text,
                 font=ctk.CTkFont(size=10, weight="bold"),
                 text_color=TXT_MED).grid(
        row=row, column=0, sticky="w", padx=18, pady=(18, 8))


# ─────────────────────────── ANA UYGULAMA ─────────────────────────────────────
class SkyProjectApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("SKY PROJECT  ·  Macro Suite")
        self.geometry("1080x700")
        self.minsize(900, 580)
        self.configure(fg_color=BG)
        try:
            self.attributes("-alpha", 0.98)
        except:
            pass
        try: self.iconbitmap(resource_path("icon.ico"))
        except: pass

        self._active_tab       = StringVar(value="Bekleme")
        self._active_slot      = "left"   # "left" | "right"
        self._logged_user      = "Misafir"
        self._trigger_var      = ctk.StringVar(value="Sol Tık")

        self.LICENSE_KEYS = {
            "SKY-VIP-2026": "CagatayYaman",
            "SKY-VIP-2027": "buminakdag",
            "SKY-VIP-2028": "yasarsari",
        }

        self.macro_data = load_data()
        self.macro_data.pop("hud_enabled", None)
        self.macro_data.pop("hud_target_title", None)

        profiles = self.macro_data.get("profiles", {})
        self.active_prof_name = self.macro_data.get("active_profile", "")
        if not self.active_prof_name or self.active_prof_name not in profiles:
            self.active_prof_name = list(profiles.keys())[0] if profiles else "Varsayılan"

        # Yeni sayfa: .batlar verisini başlat
        self._bats = self.macro_data.get("bats", [])
        
        # Uygulama dizinine göre path oluştur (daha sağlam)
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        scripts_dir = os.path.join(base, "Scripts")
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir, exist_ok=True)

        s1 = os.path.join(scripts_dir, "sekmeme_optimizer.bat")
        s2 = os.path.join(scripts_dir, "hit_reg_fix.bat")

        # Dosyalar yoksa içeriden oluştur (Portabilite için en önemli adım)
        if not os.path.exists(s1):
            with open(s1, "w", encoding="cp1254", errors="replace") as f:
                f.write(BAT_SEKMEME)
        if not os.path.exists(s2):
            with open(s2, "w", encoding="cp1254", errors="replace") as f:
                f.write(BAT_HITFIX)

        # Eğer liste boşsa veya yollar bozuksa düzelt
        if not self._bats:
            self._bats = [
                {"name": "Sekmeme Optimizer (Ping)", "path": s1},
                {"name": "Hit Iyilestirme (TCP Fix)", "path": s2}
            ]
            self.macro_data["bats"] = self._bats
            save_data(self.macro_data)
        else:
            # Mevcut listeyi kontrol et, eğer yollar bozuksa ve default isimlerse düzelt
            changed = False
            for b in self._bats:
                if not os.path.exists(b["path"]):
                    if "Sekmeme" in b["name"]:
                        b["path"] = s1
                        changed = True
                    elif "Hit" in b["name"]:
                        b["path"] = s2
                        changed = True
            if changed:
                save_data(self.macro_data)

        self.engine = AutoClicker(update_callback=self.on_state_change)
        self._show_splash()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ─── PROFİL YARDIMCILARI ──────────────────────────────────────────────────
    def _get_active_profile(self):
        profs = self.macro_data.setdefault("profiles", {})
        if self.active_prof_name not in profs:
            profs[self.active_prof_name] = {
                "left":  {"hotkey": "f8", "sequence": [], "helper_key": "None", "trigger": "left"},
                "right": {"hotkey": "",   "sequence": [], "helper_key": "None", "trigger": "right"},
            }
        prof = profs[self.active_prof_name]
        for slot, default_trig in (("left", "left"), ("right", "right")):
            s = prof.setdefault(slot, {"hotkey": "", "sequence": [], "helper_key": "None", "trigger": default_trig})
            s.setdefault("helper_key", "None")
            s.setdefault("trigger", default_trig)
        return prof

    def _get_slot_cfg(self):
        return self._get_active_profile()[self._active_slot]

    # ─── SPLASH ───────────────────────────────────────────────────────────────
    def _show_splash(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        W, H = 480, 260
        sp = ctk.CTkToplevel(self)
        self.splash = sp
        sp.overrideredirect(True)
        sp.configure(fg_color=BG)
        sp.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        sp.attributes("-topmost", True)
        try: sp.attributes("-alpha", 0.95)
        except: pass

        # Frosted glass kart
        outer = ctk.CTkFrame(sp, fg_color=BG_CARD, corner_radius=28,
                             border_width=1, border_color=BORDER_GLOW)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        # Glow halkası efekti
        glow_ring = ctk.CTkFrame(outer, fg_color=ACC_DIM, corner_radius=24,
                                  border_width=1, border_color=BORDER_GLOW)
        glow_ring.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(glow_ring, text="SKY",
                     font=ctk.CTkFont(size=42, weight="bold"),
                     text_color=ACC).pack(pady=(36, 0))
        ctk.CTkLabel(glow_ring, text="PROJECT",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TXT_MED).pack(pady=(0, 4))
        ctk.CTkLabel(glow_ring, text="Macro Suite  ·  Başlatılıyor…",
                     font=ctk.CTkFont(size=11), text_color=TXT_MUTED).pack()

        pb = ctk.CTkProgressBar(glow_ring, width=280, height=2,
                                fg_color=BORDER, progress_color=ACC, corner_radius=1)
        pb.pack(pady=(18, 0))
        pb.set(0)

        def _anim(v=0.0):
            if v <= 1.0:
                pb.set(v)
                sp.after(12, lambda: _anim(v + 0.03))
            else:
                sp.after(100, self._destroy_splash)
        sp.after(100, _anim)

    def _destroy_splash(self):
        self.splash.destroy()
        self._show_login()

    # ─── GİRİŞ ────────────────────────────────────────────────────────────────
    def _show_login(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        W, H = 420, 320
        lw = ctk.CTkToplevel(self)
        self.login_win = lw
        lw.overrideredirect(True)
        lw.configure(fg_color=BG)
        lw.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        lw.attributes("-topmost", True)
        try: lw.attributes("-alpha", 0.95)
        except: pass

        # Frosted glass kart
        outer = ctk.CTkFrame(lw, fg_color=BG_CARD, corner_radius=28,
                             border_width=1, border_color=BORDER_GLOW)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        # İç glow katmanı
        inner = ctk.CTkFrame(outer, fg_color=BG_PANEL, corner_radius=22,
                             border_width=0)
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(inner, text="🔐",
                     font=ctk.CTkFont(size=28)).pack(pady=(28, 6))
        ctk.CTkLabel(inner, text="Lisans Girişi",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TXT).pack(pady=(0, 4))
        ctk.CTkLabel(inner, text="SKY PROJECT anahtarınızı girin",
                     font=ctk.CTkFont(size=11), text_color=TXT_MUTED).pack()

        self.key_entry = ctk.CTkEntry(
            inner, fg_color=BG_INPUT, border_color=BORDER_LITE,
            text_color=TXT, font=ctk.CTkFont(size=13), width=280, height=42,
            placeholder_text="SKY-VIP-XXXX", corner_radius=14)
        self.key_entry.pack(pady=(20, 4))
        if self.macro_data.get("saved_key"):
            self.key_entry.insert(0, self.macro_data["saved_key"])
        self.key_entry.bind("<Return>", lambda e: self._verify_login())

        self.login_err = ctk.CTkLabel(inner, text="", text_color=TXT_RED,
                                      font=ctk.CTkFont(size=11))
        self.login_err.pack()

        ctk.CTkButton(inner, text="Giriş Yap", width=280, height=44,
                      fg_color=ACC, hover_color=ACC_HOT,
                      text_color="white", corner_radius=14,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._verify_login, cursor="hand2").pack(pady=(8, 0))

    def _verify_login(self):
        key = self.key_entry.get().strip()
        if key in self.LICENSE_KEYS:
            self._logged_user = self.LICENSE_KEYS[key]
            self.macro_data["saved_key"] = key
            save_data(self.macro_data)
            self.login_win.destroy()
            if hasattr(self, "_user_lbl"):
                self._user_lbl.configure(text=f"◈  {self._logged_user}")
            self.deiconify()
            self.refresh_profile_list()
            self.load_slot_ui()
            self.engine.apply_profiles({self.active_prof_name: self._get_active_profile()})
        else:
            self.login_err.configure(text="✗  Geçersiz veya süresi dolmuş anahtar!")
            self.key_entry.configure(border_color=TXT_RED)
            self.after(1500, lambda: self.key_entry.configure(border_color=BORDER_LITE))

    # ─── GENEL YAPI ───────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ─── KENAR ÇUBUĞU ─────────────────────────────────────────────────────────
    def _build_sidebar(self):
        # Ana sidebar - frosted glass panel
        sb = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0,
                          border_width=0, width=260)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(4, weight=1)
        sb.grid_columnconfigure(0, weight=1)

        # Sağ kenar ince glow çizgisi
        glow_line = ctk.CTkFrame(sb, fg_color=BORDER_GLOW, width=1)
        glow_line.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        # ── Logo bölümü - daha geniş ve nefes alan
        top = ctk.CTkFrame(sb, fg_color="transparent", height=72)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)

        # Logo ikonu - gradient hissiyatı
        gem = ctk.CTkFrame(top, fg_color=ACC, corner_radius=12,
                           width=36, height=36)
        gem.grid(row=0, column=0, padx=(20, 10), pady=18)
        gem.grid_propagate(False)
        ctk.CTkLabel(gem, text="◆", font=("Segoe UI", 14), text_color="white").place(
            relx=.5, rely=.5, anchor="center")
        ctk.CTkLabel(top, text="SKY PROJECT",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TXT).grid(row=0, column=1, sticky="w")

        # ── Kullanıcı rozeti - cam pill
        usr_card = ctk.CTkFrame(sb, fg_color=ACC_DIM, corner_radius=16,
                                border_width=1, border_color=BORDER_GLOW)
        usr_card.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 12))
        self._user_lbl = ctk.CTkLabel(usr_card, text=f"◈  {self._logged_user}",
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      text_color=ACC)
        self._user_lbl.pack(pady=10, padx=16, anchor="w")

        # ── Navigasyon sekmeleri - Apple segmented control tarzı
        nav_frame = ctk.CTkFrame(sb, fg_color="transparent")
        nav_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 8))
        nav_frame.grid_columnconfigure(0, weight=1)

        self._nav_btns = {}
        nav_items = [
            ("macro",  "◧  Makrolar"),
            ("bats",   "⚡  Scriptler"),
        ]
        for i, (page_id, label) in enumerate(nav_items):
            is_first = (i == 0)
            b = ctk.CTkButton(
                nav_frame, text=label, height=40, corner_radius=12,
                fg_color=ACC_GLOW if is_first else "transparent",
                hover_color=BG_HOVER,
                text_color=ACC if is_first else TXT_MED,
                font=ctk.CTkFont(size=13, weight="bold"),
                border_width=0, cursor="hand2",
                command=lambda pid=page_id: self._switch_page(pid))
            b.grid(row=i, column=0, sticky="ew", pady=2)
            self._nav_btns[page_id] = b

        # ── Profil listesi başlığı
        ctk.CTkLabel(sb, text="PROFİLLER",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TXT_MUTED).grid(
            row=3, column=0, sticky="w", padx=20, pady=(12, 6))

        self._list_frame = ctk.CTkScrollableFrame(
            sb, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=BORDER_LITE)
        self._list_frame.grid(row=4, column=0, sticky="nsew", padx=8, pady=(0, 6))

        # ── Yeni profil butonu
        ftr = ctk.CTkFrame(sb, fg_color="transparent", height=68)
        ftr.grid(row=5, column=0, sticky="ew")
        ftr.grid_propagate(False)
        ctk.CTkButton(ftr, text="＋  Yeni Profil",
                      fg_color=ACC_GREEN_DIM, hover_color="#ccffda",
                      text_color=TXT_GREEN, border_width=1, border_color=BORDER_GREEN,
                      corner_radius=14, height=42, cursor="hand2",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._new_profile).place(
            relx=.5, rely=.5, anchor="center", relwidth=.85)

    def refresh_profile_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()
        for name in self.macro_data.get("profiles", {}):
            self._profile_row(name, name == self.active_prof_name)

    def _profile_row(self, name, active):
        bg  = ACC_DIM    if active else "transparent"
        brd = BORDER_LITE if active else BORDER
        tc  = TXT_PURPLE  if active else TXT_MED

        f = ctk.CTkFrame(self._list_frame, fg_color=bg, corner_radius=9,
                         border_width=0, border_color=brd, cursor="hand2")
        f.pack(fill="x", pady=2, padx=2)
        f.grid_columnconfigure(1, weight=1)

        dot = ctk.CTkLabel(f, text="◆" if active else "◇",
                           font=("Segoe UI", 12), text_color=ACC if active else TXT_MUTED)
        dot.grid(row=0, column=0, padx=(10, 6), pady=9)
        lbl = ctk.CTkLabel(f, text=name, text_color=tc,
                           font=ctk.CTkFont(size=12), anchor="w")
        lbl.grid(row=0, column=1, sticky="ew", pady=9)

        for w in (f, dot, lbl):
            w.bind("<Button-1>", lambda e, n=name: self.select_profile(n))

    def select_profile(self, name, save_current=True):
        if save_current:
            self._save_settings(apply=False)
        self.active_prof_name = name
        self.macro_data["active_profile"] = name
        self.refresh_profile_list()
        self._active_slot = "left"
        if hasattr(self, "slot_btn_left"):
            self._highlight_slot("left")
        self.load_slot_ui()
        self.after(10, lambda: self.engine.apply_profiles(
            {self.active_prof_name: self._get_active_profile()}))

    def _switch_page(self, page_id: str):
        """Sayfa göster/gizle ve nav butonlarını güncelle."""
        for pid, btn in self._nav_btns.items():
            active = pid == page_id
            btn.configure(
                fg_color=ACC_DIM if active else "transparent",
                text_color=TXT_PURPLE if active else TXT_MED)
        if page_id == "macro":
            self._page_macro.grid()
            if hasattr(self, '_page_bats'):
                self._page_bats.grid_remove()
        elif page_id == "bats":
            if hasattr(self, '_page_bats'):
                self._page_bats.grid()
            self._page_macro.grid_remove()

    # ─── ANA PANEL ────────────────────────────────────────────────────────────
    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color=BG, corner_radius=20)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # ── Makro Sayfası
        self._page_macro = ctk.CTkFrame(main, fg_color="transparent")
        self._page_macro.grid(row=0, column=0, sticky="nsew")
        self._page_macro.grid_columnconfigure(0, weight=1)
        self._page_macro.grid_rowconfigure(2, weight=1)
        self._build_topbar(self._page_macro)
        self._build_slot_tabs(self._page_macro)
        body = ctk.CTkFrame(self._page_macro, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        self._build_sequence_panel(body)
        self._build_config_panel(body)

        # ── .batlar Sayfası
        self._page_bats = ctk.CTkFrame(main, fg_color="transparent")
        self._page_bats.grid(row=0, column=0, sticky="nsew")
        self._page_bats.grid_columnconfigure(0, weight=1)
        self._page_bats.grid_rowconfigure(0, weight=1)
        self._build_bats_page(self._page_bats)
        self._page_bats.grid_remove()   # başlangıçta gizli

    # ─── ÜST BAR ──────────────────────────────────────────────────────────────
    def _build_topbar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                           border_width=0, border_color=BORDER, height=64)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=20, pady=16)

        self._prof_title_var = StringVar()
        self._title_entry = ctk.CTkEntry(
            left, textvariable=self._prof_title_var,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TXT, fg_color="transparent", border_width=0, width=230)
        self._title_entry.pack(side="left")
        self._title_entry.bind("<KeyRelease>", self._on_rename_profile)

        ctk.CTkButton(left, text="🗑", width=30, height=26,
                      fg_color="#ffe5e5", hover_color="#ffcccc",
                      text_color=TXT_RED, corner_radius=7,
                      font=ctk.CTkFont(size=12), cursor="hand2",
                      command=self._delete_profile).pack(side="left", padx=(10, 0))

        # Durum
        self._status_pill = ctk.CTkFrame(bar, fg_color=ACC_DIM,
                                         corner_radius=30, border_width=0,
                                         border_color=BORDER_LITE)
        self._status_pill.grid(row=0, column=2, sticky="e", padx=20, pady=20)

        self._status_dot = ctk.CTkLabel(self._status_pill, text="●",
                                        font=("Segoe UI", 12), text_color=ACC)
        self._status_dot.pack(side="left", padx=(14, 4), pady=7)
        self._status_label = ctk.CTkLabel(self._status_pill, text="UYKUDA",
                                          font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                                          text_color=ACC)
        self._status_label.pack(side="left", padx=(0, 16), pady=7)

    # ─── SLOT SEKME ÇUBUĞU ────────────────────────────────────────────────────
    def _build_slot_tabs(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                           border_width=0, border_color=BORDER, height=56)
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_propagate(False)

        # Arka plan konteyner
        pill = ctk.CTkFrame(bar, fg_color=BG_TAG, corner_radius=24,
                            border_width=0, border_color=BORDER)
        pill.place(x=20, rely=.5, anchor="w")

        def _slot_btn(text, slot, is_first=False):
            b = ctk.CTkButton(
                pill, text=text, width=158, height=34, corner_radius=30,
                fg_color=ACC_DIM if is_first else "transparent",
                hover_color=BORDER_LITE,
                text_color=TXT_PURPLE if is_first else TXT_MED,
                font=ctk.CTkFont(size=12, weight="bold"),
                border_width=0, cursor="hand2",
                command=lambda s=slot: self._set_slot(s))
            b.pack(side="left", padx=3, pady=3)
            return b

        self.slot_btn_left  = _slot_btn("◧  Makro Slotu 1", "left",  True)
        self.slot_btn_right = _slot_btn("◨  Makro Slotu 2", "right", False)

    def _highlight_slot(self, slot):
        if slot == "left":
            self.slot_btn_left.configure(fg_color=ACC_DIM, text_color=TXT_PURPLE)
            self.slot_btn_right.configure(fg_color="transparent", text_color=TXT_MED)
        else:
            self.slot_btn_right.configure(fg_color=ACC_DIM, text_color=TXT_PURPLE)
            self.slot_btn_left.configure(fg_color="transparent", text_color=TXT_MED)

    # ─── EYLEM DİZİSİ PANELİ ─────────────────────────────────────────────────
    def _build_sequence_panel(self, parent):
        p = ctk.CTkFrame(parent, fg_color=BG, corner_radius=20)
        p.grid(row=0, column=0, sticky="nsew")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=18, pady=(15, 6))
        ctk.CTkLabel(hdr, text="EYLEM DİZİSİ",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TXT_MUTED).pack(side="left")

        self._seq_scroll = ctk.CTkScrollableFrame(
            p, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=BORDER_LITE)
        self._seq_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._seq_scroll.grid_columnconfigure(0, weight=1)

    def _refresh_actions(self):
        for w in self._seq_scroll.winfo_children():
            w.destroy()

        seq = self._get_slot_cfg().get("sequence", [])
        if not seq:
            empty = ctk.CTkFrame(self._seq_scroll, fg_color=BG_CARD,
                                 corner_radius=26, border_width=0, border_color=BORDER)
            empty.pack(fill="x", padx=6, pady=50)
            ctk.CTkLabel(empty, text="— Henüz eylem eklenmedi —\n\nSağ panelden eylem ekleyebilirsiniz.",
                         text_color=TXT_MUTED, font=ctk.CTkFont(size=12),
                         justify="center").pack(pady=24)
            return

        for i, act in enumerate(seq):
            icon = name = ""
            is_t = False
            t = act.get("type")
            if t == "delay":
                icon, name, is_t = "⏱", f"{act['ms']} ms  bekleme", True
            elif t == "mouse":
                bm = {"left": "Sol", "right": "Sağ", "middle": "Orta"}
                am = {"click": "tıkla", "down": "bas", "up": "bırak"}
                icon = "🖱"
                name = f"Fare · {bm.get(act.get('target','left'))} · {am.get(act.get('action',''))}"
            elif t == "keyboard":
                am = {"press": "bas", "down": "aşağı", "up": "bırak"}
                icon = "⌨"
                name = f"Klavye · [{act.get('target','?').upper()}] · {am.get(act.get('action',''))}"

            ActionRow(self._seq_scroll, index=i+1, icon=icon, name=name, is_timer=is_t,
                      move_up=partial(self._move_action, i, -1),
                      move_down=partial(self._move_action, i, 1),
                      delete=partial(self._delete_action, i)).pack(fill="x", pady=2, padx=4)

    # ─── KONFİGÜRASYON PANELİ ────────────────────────────────────────────────
    def _build_config_panel(self, parent):
        p = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                         border_width=0, border_color=BORDER, width=300)
        p.grid(row=0, column=1, sticky="nsew")
        p.grid_propagate(False)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        sc = ctk.CTkScrollableFrame(p, fg_color="transparent",
                                    scrollbar_button_color=BORDER,
                                    scrollbar_button_hover_color=BORDER_LITE)
        sc.grid(row=0, column=0, sticky="nsew")
        sc.grid_columnconfigure(0, weight=1)

        # ─── Tetik & Hotkey kartı
        section_label(sc, "⚡  SLOT AYARLARI", 0)
        c1 = make_card(sc, row=1)
        c1.grid_columnconfigure(1, weight=1)

        # Tetik tuşu (YENİ)
        ctk.CTkLabel(c1, text="Tetik Tuşu", text_color=TXT_MED,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w",
                                                     padx=14, pady=(14, 10))
        trig_lbl = ctk.CTkLabel(c1, text="Basılı tutulacak\nmouse tuşu",
                                text_color=TXT_MUTED, font=ctk.CTkFont(size=9),
                                justify="left")
        trig_lbl.grid(row=0, column=0, sticky="sw", padx=14, pady=(0, 4))

        self._trigger_var = ctk.StringVar(value="Sol Tık")
        trig_menu = ctk.CTkOptionMenu(
            c1, variable=self._trigger_var,
            values=list(TRIGGER_OPTS.keys()),
            width=110, height=30, corner_radius=18,
            fg_color=BG_INPUT, button_color=ACC, button_hover_color=ACC_HOT,
            text_color=TXT_ORANGE, font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda _: self._on_trigger_change())
        trig_menu.grid(row=0, column=1, sticky="e", padx=14, pady=(14, 10))

        # ayraç
        ctk.CTkFrame(c1, fg_color=BORDER, height=1).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10)

        # Aç/Kapa tuşu
        ctk.CTkLabel(c1, text="Aç / Kapa Tuşu", text_color=TXT_MED,
                     font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w",
                                                     padx=14, pady=(10, 10))
        hk_row = ctk.CTkFrame(c1, fg_color="transparent")
        hk_row.grid(row=2, column=1, sticky="e", padx=10, pady=(10, 10))

        self._hk_btn = ctk.CTkButton(
            hk_row, text="F8", width=56, height=28,
            fg_color=ACC_DIM, corner_radius=18,
            text_color=TXT_PURPLE,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            border_width=0, cursor="hand2",
            command=self._start_hotkey_bind)
        self._hk_btn.pack(side="left")
        ctk.CTkButton(hk_row, text="✕", width=28, height=28,
                      fg_color="#ffe5e5", hover_color="#ffcccc",
                      text_color=TXT_RED, corner_radius=18,
                      font=ctk.CTkFont(size=11), cursor="hand2",
                      command=self._clear_hotkey).pack(side="left", padx=(6, 0))

        # ayraç
        ctk.CTkFrame(c1, fg_color=BORDER, height=1).grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=10)

        # Yardımcı tuş
        ctk.CTkLabel(c1, text="Bypass Tuşu", text_color=TXT_MED,
                     font=ctk.CTkFont(size=12)).grid(row=4, column=0, sticky="w",
                                                     padx=14, pady=(10, 14))
        self._helper_key_var = ctk.StringVar(value="None")
        ctk.CTkOptionMenu(c1, variable=self._helper_key_var,
                          values=["None", "Shift", "Ctrl", "Alt"],
                          width=90, height=28, corner_radius=18,
                          fg_color=BG_INPUT, button_color=ACC, button_hover_color=ACC_HOT,
                          text_color=TXT, font=ctk.CTkFont(size=11)).grid(
            row=4, column=1, sticky="e", padx=14, pady=(10, 14))

        # ─── Eylem ekle kartı
        section_label(sc, "＋  YENİ EYLEM", 2)
        c2 = make_card(sc, row=3)
        c2.grid_columnconfigure(0, weight=1)

        # Tür seçici
        tab_pill = ctk.CTkFrame(c2, fg_color=BG_TAG, corner_radius=30,
                                border_width=0, border_color=BORDER)
        tab_pill.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self._tab_buttons = {}
        for i, label in enumerate(["Bekleme", "Fare", "Klavye"]):
            b = ctk.CTkButton(tab_pill, text=label, height=30, corner_radius=18,
                              fg_color=ACC_ORG_DIM if i == 0 else "transparent",
                              hover_color=BORDER_LITE,
                              text_color=TXT_ORANGE if i == 0 else TXT_MED,
                              border_width=0, cursor="hand2",
                              font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda l=label: self._set_tab(l))
            b.pack(side="left", padx=3, pady=3, expand=True, fill="x")
            self._tab_buttons[label] = b

        self._add_con = ctk.CTkFrame(c2, fg_color="transparent")
        self._add_con.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        self._add_con.grid_columnconfigure(0, weight=1)

        def entry(parent, placeholder=""):
            e = ctk.CTkEntry(parent, fg_color=BG_INPUT, border_color=BORDER_LITE,
                             text_color=TXT, font=ctk.CTkFont(size=12),
                             corner_radius=18, placeholder_text=placeholder)
            return e

        def opt_menu(parent, var, values):
            return ctk.CTkOptionMenu(parent, variable=var, values=values,
                                     fg_color=BG_INPUT, button_color=ACC,
                                     button_hover_color=ACC_HOT,
                                     text_color=TXT, corner_radius=18,
                                     font=ctk.CTkFont(size=11))

        def lbl(parent, text):
            return ctk.CTkLabel(parent, text=text, text_color=TXT_MED,
                                font=ctk.CTkFont(size=11))

        # Bekleme
        self._f_delay = ctk.CTkFrame(self._add_con, fg_color="transparent")
        lbl(self._f_delay, "Gecikme (ms)").pack(anchor="w", pady=(0, 4))
        self._delay_entry = entry(self._f_delay, "50")
        self._delay_entry.insert(0, "50")
        self._delay_entry.pack(fill="x")

        # Fare
        self._f_mouse = ctk.CTkFrame(self._add_con, fg_color="transparent")
        lbl(self._f_mouse, "Fare Tuşu").pack(anchor="w", pady=(0, 4))
        self._m_btn_var = ctk.StringVar(value="Sol Tık")
        opt_menu(self._f_mouse, self._m_btn_var,
                 ["Sol Tık", "Sağ Tık", "Orta Tık"]).pack(fill="x", pady=(0, 8))
        lbl(self._f_mouse, "Eylem").pack(anchor="w", pady=(0, 4))
        self._m_act_var = ctk.StringVar(value="Aşağı Bas (Down)")
        opt_menu(self._f_mouse, self._m_act_var,
                 ["Aşağı Bas (Down)", "Yukarı Bırak (Up)", "Normal Tıkla"]).pack(fill="x")

        # Klavye
        self._f_key = ctk.CTkFrame(self._add_con, fg_color="transparent")
        lbl(self._f_key, "Tuş (örn: w, f5, space…)").pack(anchor="w", pady=(0, 4))
        self._k_entry = entry(self._f_key, "w")
        self._k_entry.insert(0, "w")
        self._k_entry.pack(fill="x", pady=(0, 8))
        lbl(self._f_key, "Eylem").pack(anchor="w", pady=(0, 4))
        self._k_act_var = ctk.StringVar(value="Aşağı Bas (Down)")
        opt_menu(self._f_key, self._k_act_var,
                 ["Aşağı Bas (Down)", "Yukarı Bırak (Up)", "Tuşa Bas"]).pack(fill="x")

        self._f_delay.pack(fill="x")

        # Ekle butonu
        ctk.CTkButton(sc, text="＋  DİZİYE EKLE",
                      fg_color=ACC_ORG_DIM, hover_color="#ffe6cc",
                      text_color=TXT_ORANGE, border_width=0, border_color=BORDER_ORANGE,
                      corner_radius=30, height=42, cursor="hand2",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._add_to_sequence).grid(
            row=4, column=0, sticky="ew", padx=12, pady=(4, 6))

        self._save_btn = ctk.CTkButton(
            sc, text="✓  KAYDET VE UYGULA",
            fg_color=ACC_GREEN_DIM, hover_color="#ccffda",
            text_color=TXT_GREEN, border_width=0, border_color=BORDER_GREEN,
            corner_radius=30, height=42, cursor="hand2",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._save_settings)
        self._save_btn.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 18))

    # ─── .BATLAR SAYFASI ─────────────────────────────────────────────────────────
    def _build_bats_page(self, parent):
        import subprocess

        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # ── Başlık bantı
        hdr = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                           border_width=0, border_color=BORDER, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(hdr, text="⚡  .BATLAR",
                     font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                     text_color=TXT_ORANGE).grid(row=0, column=0, padx=22, pady=18, sticky="w")
        ctk.CTkLabel(hdr, text="Bat dosyalarını yönet ve çalıştır",
                     font=ctk.CTkFont(size=11),
                     text_color=TXT_MUTED).grid(row=0, column=1, padx=6, sticky="w")

        # ── Gövde: sol liste + sağ detay
        body = ctk.CTkFrame(parent, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # ── Sol: bat listesi
        left = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=26,
                            border_width=0, border_color=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left, text="BAT DOSYALARI",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TXT_MUTED).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        self._bat_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=BORDER_LITE)
        self._bat_scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self._bat_scroll.grid_columnconfigure(0, weight=1)

        # Ekle butonu
        ctk.CTkButton(left, text="＋  Bat Ekle",
                      fg_color=ACC_ORG_DIM, hover_color="#ffe6cc",
                      text_color=TXT_ORANGE, border_width=0, border_color=BORDER_ORANGE,
                      corner_radius=30, height=38, cursor="hand2",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._bat_add_file).grid(
            row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        # ── Sağ: detay + terminallçıkış bölgesi
        right = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=26,
                             border_width=0, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # Üst bar — seçili bat bilgisi
        info_bar = ctk.CTkFrame(right, fg_color="transparent")
        info_bar.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        info_bar.grid_columnconfigure(0, weight=1)

        self._bat_name_lbl = ctk.CTkLabel(
            info_bar, text="Bat dosyası seçin…",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TXT_MED, anchor="w")
        self._bat_name_lbl.grid(row=0, column=0, sticky="ew")

        self._bat_path_lbl = ctk.CTkLabel(
            info_bar, text="",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=TXT_MUTED, anchor="w")
        self._bat_path_lbl.grid(row=1, column=0, sticky="ew")

        # Buton grubu
        btn_row = ctk.CTkFrame(info_bar, fg_color="transparent")
        btn_row.grid(row=0, column=1, rowspan=2, sticky="e")

        self._bat_run_btn = ctk.CTkButton(
            btn_row, text="▶  Çalıştır", width=100, height=34,
            fg_color=ACC_GREEN_DIM, hover_color="#ccffda",
            text_color=TXT_GREEN, border_width=0, border_color=BORDER_GREEN,
            corner_radius=30, cursor="hand2",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._bat_run, state="disabled")
        self._bat_run_btn.pack(side="left", padx=(0, 6))

        self._bat_del_btn = ctk.CTkButton(
            btn_row, text="🗑", width=34, height=34,
            fg_color="#ffe5e5", hover_color="#ffcccc",
            text_color=TXT_RED, corner_radius=30, cursor="hand2",
            font=ctk.CTkFont(size=12),
            command=self._bat_delete, state="disabled")
        self._bat_del_btn.pack(side="left")

        # Ayıraç
        ctk.CTkFrame(right, fg_color=BORDER, height=1).grid(
            row=0, column=0, sticky="sew", padx=14, pady=(64, 0))

        # Terminale benzeri çıktı alanı
        ctk.CTkLabel(right, text="KOMUT ÇIKTISI",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TXT_MUTED).grid(row=0, column=0, sticky="sw", padx=14, pady=(80, 0))

        self._bat_output = ctk.CTkTextbox(
            right, fg_color="#1e1e1e", text_color="#30d158",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            corner_radius=20, border_width=0, border_color=BORDER,
            state="disabled", wrap="word")
        self._bat_output.grid(row=1, column=0, sticky="nsew", padx=14, pady=(4, 14))

        # İç durum
        self._bat_selected_path = None
        self._bat_selected_name = None
        self._bat_procs: list = []

        # Kaydedilmiş bat listesini yükle
        self._bats: list = self.macro_data.get("bats", [])
        self._refresh_bat_list()

    def _refresh_bat_list(self):
        for w in self._bat_scroll.winfo_children():
            w.destroy()
        if not self._bats:
            ctk.CTkLabel(self._bat_scroll,
                         text="Henüz bat eklenmedi.\n\nAltındaki „＋ Bat Ekle“\nbutonu ile dosya ekle.",
                         text_color=TXT_MUTED, font=ctk.CTkFont(size=11),
                         justify="center").pack(pady=40)
            return
        for entry in self._bats:
            self._bat_row(entry)

    def _bat_row(self, entry: dict):
        name = entry.get("name", "")
        path = entry.get("path", "")
        is_sel = (path == self._bat_selected_path)

        row = ctk.CTkFrame(
            self._bat_scroll,
            fg_color=ACC_ORG_DIM if is_sel else BG_CARD,
            corner_radius=30, border_width=0,
            border_color=BORDER_ORANGE if is_sel else BORDER,
            cursor="hand2")
        row.pack(fill="x", pady=3, padx=2)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="⚡",
                     font=("Segoe UI", 12), text_color=TXT_ORANGE).grid(
            row=0, column=0, padx=(12, 6), pady=10)
        ctk.CTkLabel(row, text=name, text_color=TXT if is_sel else TXT_MED,
                     font=ctk.CTkFont(size=12, weight="bold"), anchor="w").grid(
            row=0, column=1, sticky="ew", pady=10)

        row.bind("<Button-1>", lambda e, p=path, n=name: self._bat_select(n, p))
        for child in row.winfo_children():
            child.bind("<Button-1>", lambda e, p=path, n=name: self._bat_select(n, p))

    def _bat_select(self, name: str, path: str):
        self._bat_selected_name = name
        self._bat_selected_path = path
        self._bat_name_lbl.configure(text=f"⚡  {name}", text_color=TXT_ORANGE)
        self._bat_path_lbl.configure(text=path)
        self._bat_run_btn.configure(state="normal")
        self._bat_del_btn.configure(state="normal")
        self._refresh_bat_list()

    def _bat_add_file(self):
        from tkinter import filedialog, simpledialog
        path = filedialog.askopenfilename(
            title="Bat Dosyası Seç",
            filetypes=[("Bat Dosyaları", "*.bat *.cmd"), ("Tüm Dosyalar", "*.*")])
        if not path:
            return
        name = simpledialog.askstring(
            "Bat Adı", "Bu bat için kısa bir ad girin:",
            initialvalue=os.path.splitext(os.path.basename(path))[0])
        if not name:
            name = os.path.basename(path)
        self._bats.append({"name": name, "path": path})
        self.macro_data["bats"] = self._bats
        save_data(self.macro_data)
        self._refresh_bat_list()

    def _bat_delete(self):
        if not self._bat_selected_path:
            return
        self._bats = [b for b in self._bats if b["path"] != self._bat_selected_path]
        self.macro_data["bats"] = self._bats
        save_data(self.macro_data)
        self._bat_selected_path = None
        self._bat_selected_name = None
        self._bat_name_lbl.configure(text="Bat dosyası seçin…", text_color=TXT_MED)
        self._bat_path_lbl.configure(text="")
        self._bat_run_btn.configure(state="disabled")
        self._bat_del_btn.configure(state="disabled")
        self._refresh_bat_list()

    def _bat_run(self):
        import subprocess, threading
        path = self._bat_selected_path
        if not path or not os.path.exists(path):
            self._bat_write_output("[HATA] Dosya bulunamadı: " + str(path) + "\n")
            return
        self._bat_write_output(f"[BAŞLATILIYOR] {path}\n" + "-" * 48 + "\n")
        self._bat_run_btn.configure(text="⏳ Çalışıyor…", state="disabled",
                                    text_color=TXT_MUTED)
        def _run():
            try:
                proc = subprocess.Popen(
                    [path], stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=os.path.dirname(path),
                    shell=True, text=True, encoding="cp1254", errors="replace")
                for line in proc.stdout:
                    self.after(0, self._bat_write_output, line)
                proc.wait()
                rc = proc.returncode
                self.after(0, self._bat_write_output,
                           f"\n" + "-" * 48 + f"\n[TAMAM] Çıkış kodu: {rc}\n")
            except Exception as ex:
                self.after(0, self._bat_write_output, f"[HATA] {ex}\n")
            finally:
                self.after(0, lambda: self._bat_run_btn.configure(
                    text="▶  Çalıştır", state="normal", text_color=TXT_GREEN))
        threading.Thread(target=_run, daemon=True).start()

    def _bat_write_output(self, text: str):
        self._bat_output.configure(state="normal")
        self._bat_output.insert("end", text)
        self._bat_output.see("end")
        self._bat_output.configure(state="disabled")




    # ─── TETIK DEĞİŞİKLİĞİ ────────────────────────────────────────────────────
    def _on_trigger_change(self):
        """Dropdown'dan tetik değiştirilince anında kaydeder."""
        cfg = self._get_slot_cfg()
        cfg["trigger"] = TRIGGER_OPTS.get(self._trigger_var.get(), "left")
        self._save_settings(apply=False)
        self.after(20, lambda: self.engine.apply_profiles(
            {self.active_prof_name: self._get_active_profile()}))

    # ─── TUŞA ATAMA ───────────────────────────────────────────────────────────
    def _start_hotkey_bind(self):
        self._hk_btn.configure(text="···", fg_color=BG_INPUT, text_color=TXT_MED)
        self.bind("<Key>", self._on_hotkey_press)
        self.focus_set()

    def _on_hotkey_press(self, event):
        self.unbind("<Key>")
        key = event.keysym.lower()
        if key in ("escape", "space", "return", "backspace"):
            cfg = self._get_slot_cfg()
            hk = cfg.get("hotkey", "")
            self._hk_btn.configure(
                text=hk.upper() if hk else "Tuşa Bas",
                fg_color=ACC_DIM if hk else BG_INPUT,
                text_color=TXT_PURPLE if hk else TXT_MED)
            return
        self._hk_btn.configure(text=key.upper(), fg_color=ACC_DIM, text_color=TXT_PURPLE)
        self._save_settings(apply=True)

    def _clear_hotkey(self):
        self._hk_btn.configure(text="Tuşa Bas", fg_color=BG_INPUT, text_color=TXT_MED)
        self._save_settings(apply=True)

    # ─── SIRA / SİL ───────────────────────────────────────────────────────────
    def _move_action(self, idx, direction):
        seq = self._get_slot_cfg()["sequence"]
        ni = idx + direction
        if 0 <= ni < len(seq):
            seq[idx], seq[ni] = seq[ni], seq[idx]
            self._save_settings()
            self._refresh_actions()

    def _delete_action(self, idx):
        seq = self._get_slot_cfg()["sequence"]
        if 0 <= idx < len(seq):
            seq.pop(idx)
            self._save_settings()
            self._refresh_actions()

    # ─── SLOT / TAB DEĞİŞTİRME ────────────────────────────────────────────────
    def _set_slot(self, slot):
        if self._active_slot == slot:
            return
        self._save_settings(apply=False)
        self._active_slot = slot
        self._highlight_slot(slot)
        self.load_slot_ui()
        self.after(10, lambda: self.engine.apply_profiles(
            {self.active_prof_name: self._get_active_profile()}))

    def _set_tab(self, label):
        self._active_tab.set(label)
        for lbl, btn in self._tab_buttons.items():
            btn.configure(fg_color=ACC_ORG_DIM if lbl == label else "transparent",
                          text_color=TXT_ORANGE if lbl == label else TXT_MED)
        self._f_delay.pack_forget()
        self._f_mouse.pack_forget()
        self._f_key.pack_forget()
        {"Bekleme": self._f_delay, "Fare": self._f_mouse, "Klavye": self._f_key}[label].pack(fill="x")

    # ─── EYLEM EKLE ───────────────────────────────────────────────────────────
    def _add_to_sequence(self):
        tab = self._active_tab.get()
        action = {}
        if tab == "Bekleme":
            try:    ms = int(self._delay_entry.get())
            except: ms = 50
            action = {"type": "delay", "ms": ms}
        elif tab == "Fare":
            bm = {"Sol Tık": "left", "Sağ Tık": "right", "Orta Tık": "middle"}
            am = {"Normal Tıkla": "click", "Aşağı Bas (Down)": "down", "Yukarı Bırak (Up)": "up"}
            action = {"type": "mouse",
                      "target": bm[self._m_btn_var.get()],
                      "action": am[self._m_act_var.get()]}
        elif tab == "Klavye":
            key = self._k_entry.get().strip() or "a"
            am = {"Tuşa Bas": "press", "Aşağı Bas (Down)": "down", "Yukarı Bırak (Up)": "up"}
            action = {"type": "keyboard", "target": key.lower(),
                      "action": am[self._k_act_var.get()]}
        if action:
            self._get_slot_cfg()["sequence"].append(action)
            self._refresh_actions()
            self._save_settings()

    # ─── UI YÜKLEMESİ ─────────────────────────────────────────────────────────
    def load_slot_ui(self):
        self._prof_title_var.set(self.active_prof_name)
        cfg = self._get_slot_cfg()
        hk = cfg.get("hotkey", "")
        if hk:
            self._hk_btn.configure(text=hk.upper(), fg_color=ACC_DIM, text_color=TXT_PURPLE)
        else:
            self._hk_btn.configure(text="Tuşa Bas", fg_color=BG_INPUT, text_color=TXT_MED)
        self._helper_key_var.set(cfg.get("helper_key", "None"))
        # Tetik tuşu dropdown'u güncelle
        trigger_raw = cfg.get("trigger", "left")
        self._trigger_var.set(TRIGGER_LABELS.get(trigger_raw, "Sol Tık"))
        self._refresh_actions()

    # ─── KAYDET ───────────────────────────────────────────────────────────────
    def _save_settings(self, apply=True):
        self._on_rename_profile()
        cfg = self._get_slot_cfg()
        txt = self._hk_btn.cget("text").lower()
        cfg["hotkey"]     = "" if txt in ("tuşa bas", "···", "") else txt
        cfg["helper_key"] = self._helper_key_var.get()
        cfg["trigger"]    = TRIGGER_OPTS.get(self._trigger_var.get(), "left")
        self.macro_data["active_profile"] = self.active_prof_name
        save_data(self.macro_data)
        if apply:
            self.engine.apply_profiles({self.active_prof_name: self._get_active_profile()})
            self._save_btn.configure(text="✔  KAYDEDİLDİ")
            self.after(2000, lambda: self._save_btn.configure(text="✓  KAYDET VE UYGULA"))

    # ─── DURUM ────────────────────────────────────────────────────────────────
    def on_state_change(self, worker_id, is_enabled):
        self.after(0, self._update_status, worker_id, is_enabled)

    def _update_status(self, worker_id, is_enabled):
        if is_enabled:
            self._status_dot.configure(text_color=TXT_GREEN)
            self._status_pill.configure(border_color=BORDER_GREEN)
            self._status_label.configure(text="MAKRO AKTİF", text_color=TXT_GREEN)
        else:
            self._status_dot.configure(text_color="#2a2850")
            self._status_pill.configure(border_color=BORDER_LITE)
            self._status_label.configure(text="UYKUDA", text_color="#38356a")

    # ─── PROFİL İŞLEMLERİ ────────────────────────────────────────────────────
    def _delete_profile(self):
        if len(self.macro_data.get("profiles", {})) <= 1:
            return
        del self.macro_data["profiles"][self.active_prof_name]
        self.select_profile(list(self.macro_data["profiles"].keys())[0], save_current=False)

    def _on_rename_profile(self, event=None):
        new = self._prof_title_var.get().strip()
        if not new or new == self.active_prof_name:
            return
        if new in self.macro_data.get("profiles", {}):
            return
        data = self.macro_data["profiles"].pop(self.active_prof_name)
        self.macro_data["profiles"][new] = data
        self.active_prof_name = new
        self.macro_data["active_profile"] = new
        save_data(self.macro_data)
        self.refresh_profile_list()

    def _new_profile(self):
        self._save_settings(apply=False)
        num = len(self.macro_data.get("profiles", {})) + 1
        name = f"SKY Profil {num}"
        while name in self.macro_data.get("profiles", {}):
            num += 1
            name = f"SKY Profil {num}"
        self.macro_data.setdefault("profiles", {})[name] = {
            "left":  {"hotkey": "f8", "sequence": [], "helper_key": "None", "trigger": "left"},
            "right": {"hotkey": "",   "sequence": [], "helper_key": "None", "trigger": "right"},
        }
        save_data(self.macro_data)
        self.select_profile(name)

    def on_closing(self):
        self._save_settings(apply=False)
        self.engine.on_closing()
        self.destroy()


if __name__ == "__main__":
    app = SkyProjectApp()
    app.mainloop()
