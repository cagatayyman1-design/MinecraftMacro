import os
import sys
import threading
import subprocess
import eel
import json
import urllib.request
from datetime import datetime, timedelta
import datetime as dt_mod

CURRENT_VERSION = "1.0.0"
# Önemli: Bu URL'yi kendi GitHub Gist veya sunucu linkinle değiştirmelisin
UPDATE_URL = "https://raw.githubusercontent.com/cagatayyman1-design/MinecraftMacro/main/version.json"

# Modül yollarını ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.profile_manager import load_data, save_data
from core.macro_engine import AutoClicker
from core.discord_rpc import DiscordRPCManager

def resource_path(rel):
    try:    base = sys._MEIPASS
    except: base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

HWID_DB_URL = "https://skyproject-db-default-rtdb.europe-west1.firebasedatabase.app/.json"

def get_hwid():
    try:
        import winreg
        registry = winreg.HKEY_LOCAL_MACHINE
        address = r"SOFTWARE\Microsoft\Cryptography"
        key = winreg.OpenKey(registry, address, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        hwid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return hwid
    except:
        return "UNKNOWN-HWID"

class AppState:
    def __init__(self):
        self.macro_data = load_data()
        
        # Her girişte key istesin: saved_key'i temizle
        self.macro_data.pop("saved_key", None)
        save_data(self.macro_data)
        
        self.active_prof_name = self.macro_data.get("active_profile", "")
        profs = self.macro_data.get("profiles", {})
        if not self.active_prof_name or self.active_prof_name not in profs:
            self.active_prof_name = list(profs.keys())[0] if profs else "Varsayılan"
            
        self._bats = self.macro_data.setdefault("bats", [])
        self._sync_local_scripts() # Yerel scriptleri senkronize et
        self.engine = None
        self.discord_rpc = DiscordRPCManager(client_id="1488472058395361352")
        self.discord_rpc.update_profile(self.active_prof_name)
        self.discord_rpc.start()

    def _sync_local_scripts(self):
        """Scripts klasöründeki bat dosyalarını otomatik olarak listeye ekler."""
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Scripts")
        if os.path.exists(scripts_dir):
            existing_paths = [b.get("path") for b in self._bats]
            for file in os.listdir(scripts_dir):
                if file.endswith(".bat") or file.endswith(".cmd"):
                    # Path normalization for comparison
                    full_path = os.path.abspath(os.path.join(scripts_dir, file))
                    if full_path not in existing_paths:
                        name = file.replace(".bat", "").replace(".cmd", "").replace("_", " ").title()
                        self._bats.append({"name": name, "path": full_path})
            save_data(self.macro_data)
        
    def get_active_profile(self):
        profs = self.macro_data.setdefault("profiles", {})
        if self.active_prof_name not in profs:
            profs[self.active_prof_name] = {
                "left":  {"hotkey": "f8", "sequence": [], "helper_key": "None", "trigger": "left"},
                "right": {"hotkey": "",   "sequence": [], "helper_key": "None", "trigger": "right"},
            }
        prof = profs[self.active_prof_name]
        for slot in ("left", "right"):
            s = prof.setdefault(slot, {})
            s.setdefault("hotkey", "")
            s.setdefault("sequence", [])
            s.setdefault("helper_key", "None")
            s.setdefault("trigger", slot)
        return prof
        
    def init_engine(self):
        self.engine = AutoClicker(update_callback=self.on_state_change)
        self.engine.apply_profiles({self.active_prof_name: self.get_active_profile()})
        
    def on_state_change(self, worker_id, is_enabled):
        try:
            eel.updateStatus(worker_id, is_enabled)()
        except:
            pass
            
state = AppState()

# -- API Metodları --

@eel.expose
def get_system_hwid():
    return get_hwid()

@eel.expose
def copy_to_clipboard(text):
    try:
        subprocess.run("clip", input=text.encode("utf-16le"), check=True)
        return True
    except Exception as e:
        print("Clipboard error:", e)
        return False

@eel.expose
def verify_hwid_login():
    current_hwid = get_hwid()
    try:
        req = urllib.request.Request(HWID_DB_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            licenses = data.get("licenses", {})
            
            if current_hwid in licenses:
                lic = licenses[current_hwid]
                expiry = lic.get("expiry", "unlimited")
                user_name = lic.get("name", "VIP Üye")
                
                if expiry == "unlimited":
                    return {"success": True, "user": user_name, "expiry": "Sınırsız"}
                
                # Tarih kontrolü
                try:
                    expiry_dt = dt_mod.datetime.strptime(expiry, '%Y-%m-%d')
                    if dt_mod.datetime.now() <= expiry_dt:
                        return {"success": True, "user": user_name, "expiry": expiry}
                    else:
                        return {"success": False, "msg": "Lisans süreniz dolmuş! Lütfen Discord'dan yenileyin."}
                except:
                    return {"success": False, "msg": "Lisans verisi hatalı. Lütfen destekle iletişime geçin."}
            else:
                return {"success": False, "msg": "HWID Onaylı Değil! Lütfen Discord'dan onaylatın."}
    except Exception as e:
        return {"success": False, "msg": "Veritabanıyla bağlantı kurulamadı!"}

@eel.expose
def check_saved_login():
    current_hwid = get_hwid()
    try:
        req = urllib.request.Request(HWID_DB_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            licenses = data.get("licenses", {})
            if current_hwid in licenses:
                lic = licenses[current_hwid]
                expiry = lic.get("expiry", "unlimited")
                if expiry == "unlimited":
                    return {"success": True, "user": lic.get("name", "VIP"), "expiry": "Sınırsız"}
                
                expiry_dt = dt_mod.datetime.strptime(expiry, '%Y-%m-%d')
                if dt_mod.datetime.now() <= expiry_dt:
                    return {"success": True, "user": lic.get("name", "VIP"), "expiry": expiry}
    except:
        pass
    return {"success": False}

@eel.expose
def logout():
    return True

@eel.expose
def get_initial_data():
    return {
        "profiles": state.macro_data.get("profiles", {}),
        "active_profile": state.active_prof_name,
        "bats": state.macro_data.get("bats", []),
        "theme": state.macro_data.get("theme", "light"),
        "current_profile_data": state.get_active_profile()
    }

@eel.expose
def check_update():
    """Uzak sunucudan güncel versiyon bilgisini kontrol eder."""
    try:
        # User-agent ekleyerek bazı sunucuların (GitHub gibi) isteği reddetmesini önlüyoruz
        req = urllib.request.Request(UPDATE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest = data.get("version", "1.0.0")
            
            # Versiyon karşılaştırma (Basit string karşılaştırma yerine split edip bakıyoruz)
            v_local = [int(x) for x in CURRENT_VERSION.split('.')]
            v_remote = [int(x) for x in latest.split('.')]
            
            if v_remote > v_local:
                return {
                    "update_available": True,
                    "latest_version": latest,
                    "url": data.get("url", "#"),
                    "changelog": data.get("changelog", "Yeni iyileştirmeler yapıldı.")
                }
    except Exception as e:
        print(f"Update check failed: {e}")
    
    return {"update_available": False}

@eel.expose
def start_download(url):
    """Dosyayı masaüstüne indirir ve ilerlemeyi bildirir."""
    def _dl():
        try:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            filename = "SKY_PROJECT_UPDATE.exe"
            save_path = os.path.join(desktop, filename)
            
            # User-agent ile istek
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                total_size = int(response.info().get('Content-Length', 0))
                downloaded = 0
                block_size = 8192
                
                with open(save_path, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        f.write(buffer)
                        
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            eel.updateDownloadProgress(percent)()
                
                eel.updateDownloadProgress(100, True)() # Bitti sinyali
        except Exception as e:
            print(f"Download failed: {e}")
            eel.updateDownloadProgress(-1)() # Hata sinyali
            
    threading.Thread(target=_dl, daemon=True).start()
    return True

@eel.expose
def save_theme(theme_name):
    state.macro_data["theme"] = theme_name
    save_data(state.macro_data)
    return True

@eel.expose
def save_slot_data(slot_id, trigger, hotkey, helper, sequence, repeat_mode="while_pressed", repeat_delay=13):
    prof = state.get_active_profile()
    prof[slot_id] = {
        "hotkey": hotkey,
        "sequence": sequence,
        "helper_key": helper,
        "trigger": trigger,
        "repeat_mode": repeat_mode,
        "repeat_delay": repeat_delay
    }
    state.macro_data["active_profile"] = state.active_prof_name
    save_data(state.macro_data)
    if state.engine:
        state.engine.apply_profiles({state.active_prof_name: prof})
    return True

@eel.expose
def set_active_profile(name):
    if name in state.macro_data.get("profiles", {}):
        state.active_prof_name = name
        state.macro_data["active_profile"] = name
        save_data(state.macro_data)
        state.discord_rpc.update_profile(name)
        if state.engine:
            state.engine.apply_profiles({state.active_prof_name: state.get_active_profile()})
        return {"success": True, "data": state.get_active_profile()}
    return {"success": False}

@eel.expose
def new_profile():
    num = len(state.macro_data.get("profiles", {})) + 1
    name = f"SKY Profil {num}"
    while name in state.macro_data.get("profiles", {}):
        num += 1
        name = f"SKY Profil {num}"
        
    state.macro_data.setdefault("profiles", {})[name] = {
        "left":  {"hotkey": "", "sequence": [], "helper_key": "None", "trigger": "left", "repeat_mode": "while_pressed", "repeat_delay": 13},
        "right": {"hotkey": "", "sequence": [], "helper_key": "None", "trigger": "right", "repeat_mode": "while_pressed", "repeat_delay": 13},
    }
    state.active_prof_name = name
    state.macro_data["active_profile"] = name
    save_data(state.macro_data)
    state.discord_rpc.update_profile(name)
    if state.engine:
        state.engine.apply_profiles({state.active_prof_name: state.get_active_profile()})
    return {"success": True, "name": name, "data": state.get_active_profile()}

@eel.expose
def rename_profile(new_name):
    new_name = str(new_name).strip()
    if not new_name or new_name == state.active_prof_name: return False
    if new_name in state.macro_data.get("profiles", {}): return False
    
    data = state.macro_data["profiles"].pop(state.active_prof_name)
    state.macro_data["profiles"][new_name] = data
    state.active_prof_name = new_name
    state.macro_data["active_profile"] = new_name
    save_data(state.macro_data)
    state.discord_rpc.update_profile(new_name)
    return True

@eel.expose
def delete_profile():
    if len(state.macro_data.get("profiles", {})) <= 1: return False
    del state.macro_data["profiles"][state.active_prof_name]
    state.active_prof_name = list(state.macro_data["profiles"].keys())[0]
    state.macro_data["active_profile"] = state.active_prof_name
    save_data(state.macro_data)
    state.discord_rpc.update_profile(state.active_prof_name)
    if state.engine:
        state.engine.apply_profiles({state.active_prof_name: state.get_active_profile()})
    return {"success": True, "name": state.active_prof_name, "data": state.get_active_profile()}

@eel.expose
def create_dialog_bat():
    try:
        import tkinter as tk
        from tkinter import filedialog, simpledialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title="Bat Dosyası Seç", filetypes=[("Bat Dosyaları", "*.bat *.cmd")])
        if not path: return {"success": False}
        name = simpledialog.askstring("Bat Adı", "Kısa Ad Girin:", initialvalue=os.path.basename(path).replace('.bat',''))
        name = name if name else os.path.basename(path)
        state._bats.append({"name": name, "path": path})
        save_data(state.macro_data)
        return {"success": True, "bats": state._bats}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def delete_bat(path):
    state._bats = [b for b in state._bats if b.get('path') != path]
    state.macro_data["bats"] = state._bats
    save_data(state.macro_data)
    return {"success": True, "bats": state._bats}

@eel.expose
def run_bat(path):
    if not path or not os.path.exists(path): return {"success": False, "error": "Dosya bulunamadı"}
    def _run():
        try:
            proc = subprocess.Popen([path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW, shell=True, text=True, encoding="cp1254", errors="replace")
            for line in proc.stdout:
                eel.appendBatLog(line.strip())()
            proc.wait()
            eel.appendBatLog(f"[TAMAM] Çıkış Kodu: {proc.returncode}")()
        except Exception as e:
            eel.appendBatLog(f"[HATA] {str(e)}")()
    threading.Thread(target=_run, daemon=True).start()
    return {"success": True}

def on_close(page, sockets):
    if state.engine:
        state.engine.on_closing()
    state.discord_rpc.stop()
    os._exit(0)

def main():
    state.init_engine()
    # eel baslat - Web dosyaları `gui/web` içerisinde.
    web_dir = resource_path('gui/web')
    eel.init(web_dir)
    try:
        eel.start('index.html', size=(1000, 660), close_callback=on_close, mode='chrome', cmdline_args=['--disable-infobars'])
    except Exception as e:
        # Eğer Edge Chromium bulunamazsa default tarayıcıyla (edge vs) dene
        eel.start('index.html', size=(1000, 660), close_callback=on_close, mode='edge')

if __name__ == '__main__':
    main()
