import re

import sys
import os

gui_path = r"C:\Users\Cagat\.gemini\antigravity\scratch\MinecraftMacro\gui\app.py"

with open(gui_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Renk değişimi (Apple / Glass Tarzı)
old_colors = r"""BG            = "#07060d"
BG_PANEL      = "#0b0a14"
BG_SIDEBAR    = "#090815"
BG_CARD       = "#0f0e1c"
BG_INPUT      = "#0a0916"
BG_TAG        = "#131126"

BORDER        = "#1a1830"
BORDER_LITE   = "#28254a"
BORDER_ORANGE = "#3a2510"
BORDER_GREEN  = "#143020"

TXT           = "#edeaff"
TXT_MED       = "#7a7498"
TXT_MUTED     = "#3a3660"
TXT_ORANGE    = "#f5a623"
TXT_GREEN     = "#3ddc84"
TXT_RED       = "#ff5c5c"
TXT_CYAN      = "#56d4c8"
TXT_PURPLE    = "#c084fc"

ACC           = "#7c3aed"   # Ana vurgu — derin mor
ACC_HOT       = "#9f5cf7"   # Hover hali
ACC_DIM       = "#1e1040"
ACC_ORANGE    = "#f5a623"   # İkincil vurgu — turuncu
ACC_ORG_DIM   = "#2a1800"
ACC_GREEN_DIM = "#0b2018"
"""

new_colors = r"""BG            = "#1c1c1e"  # Apple dark arka plan
BG_PANEL      = "#2c2c2e"
BG_SIDEBAR    = "#1a1a1c"
BG_CARD       = "#2c2c2e"
BG_INPUT      = "#3a3a3c"
BG_TAG        = "#3a3a3c"

BORDER        = "#38383a"  # Şeffaf hissiyatı veren silik çizgi
BORDER_LITE   = "#48484a"
BORDER_ORANGE = "#4d2900"
BORDER_GREEN  = "#143020"

TXT           = "#f2f2f7"  # Göz yormayan Apple beyazı
TXT_MED       = "#8e8e93"
TXT_MUTED     = "#5c5c5f"
TXT_ORANGE    = "#ff9f0a"
TXT_GREEN     = "#32d74b"
TXT_RED       = "#ff453a"
TXT_CYAN      = "#64d2ff"
TXT_PURPLE    = "#0a84ff"  # Eskinin Mor mavisini Apple Mavi yaptık

ACC           = "#0a84ff"  # Ana vurgu - iOS Blue
ACC_HOT       = "#409cff"
ACC_DIM       = "#002a5c"  # Çok silik mavi vurgu glow efekti için
ACC_ORANGE    = "#ff9f0a"
ACC_ORG_DIM   = "#4d2900"
ACC_GREEN_DIM = "#103319"
"""

text = text.replace(old_colors.strip(), new_colors.strip())

# 2. Font Değişimi
text = re.sub(r'family="Courier New"', r'family="Segoe UI"', text)
text = re.sub(r'font=\("Courier New",\s*\d+\)', r'font=("Segoe UI", 12)', text)
text = re.sub(r'font=\("Arial",\s*\d+\)', r'font=("Segoe UI", 12)', text)

# 3. Main Window / Login Window / Splash opacity ayarları
init_pattern = r'(self\.configure\(fg_color=BG\))'
text = re.sub(init_pattern, r'\1\n        try:\n            self.attributes("-alpha", 0.98)\n        except:\n            pass', text)

splash_pattern = r'(sp\.attributes\("-topmost", True\))'
text = re.sub(splash_pattern, r'\1\n        try:\n            sp.attributes("-alpha", 0.96)\n        except:\n            pass', text)

login_pattern = r'(lw\.attributes\("-topmost", True\))'
text = re.sub(login_pattern, r'\1\n        try:\n            lw.attributes("-alpha", 0.96)\n        except:\n            pass', text)

# 4. Köşeleri tam yuvarlama ve gereksiz sınırları silme (Flat Modern/Apple Design)
text = re.sub(r'corner_radius=0', 'corner_radius=20', text)
text = re.sub(r'corner_radius=6', 'corner_radius=14', text)
text = re.sub(r'corner_radius=8', 'corner_radius=18', text)
text = re.sub(r'corner_radius=10', 'corner_radius=22', text)
text = re.sub(r'corner_radius=12', 'corner_radius=24', text)
text = re.sub(r'corner_radius=14', 'corner_radius=26', text)
text = re.sub(r'corner_radius=22', 'corner_radius=30', text)

text = re.sub(r'border_width=1', 'border_width=0', text)

# Küçük düzenlemeler
# Arkaplandan daha iyi ayırt edilsin diye action kartlarına border verebiliriz Apple misali (blur/border trick)
text = text.replace('fg_color=BG_CARD, corner_radius=18,\n                         border_width=0, border_color=border', 'fg_color=BG_CARD, corner_radius=18,\n                         border_width=1, border_color=BORDER')

# Save 
with open(gui_path, "w", encoding="utf-8") as f:
    f.write(text)

print("UI successfully patched.")
