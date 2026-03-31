import threading
import time
import keyboard
import mouse
import ctypes
import ctypes.wintypes
import eel

# ─── Windows Mesaj Sabitleri ───────────────────────────────────────────────────
WH_MOUSE_LL          = 14
WM_LBUTTONDOWN       = 0x0201
WM_LBUTTONUP         = 0x0202
WM_RBUTTONDOWN       = 0x0204
WM_RBUTTONUP         = 0x0205
WM_MBUTTONDOWN       = 0x0207
WM_MBUTTONUP         = 0x0208
WM_XBUTTONDOWN       = 0x020B
WM_XBUTTONUP         = 0x020C
XBUTTON1             = 0x0001
XBUTTON2             = 0x0002
LLMHF_INJECTED       = 0x00000001
LLMHF_LOWER_IL_INJECTED = 0x00000002

user32 = ctypes.windll.user32

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt",          ctypes.wintypes.POINT),
        ("mouseData",   ctypes.wintypes.DWORD),
        ("flags",       ctypes.wintypes.DWORD),
        ("time",        ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.wintypes.ULONG))
    ]

CMPFUNC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int,
    ctypes.wintypes.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT))


# ─────────────────────────────────────────────────────────────────────────────
class PhysicalMouseTracker:
    """
    Düşük seviyeli Windows hook ile fiziksel fare durumunu izler.
    Artık sadece saf tetik tespiti için kullanılır (performans odaklı).
    """

    def __init__(self):
        # Tuş durumları
        self.left_down  = False
        self.right_down = False
        self.mid_down   = False
        self.x1_down    = False
        self.x2_down    = False

        # Hook başlat
        self.hook_id = None
        self.pointer = CMPFUNC(self.hook_proc)
        self.thread  = threading.Thread(target=self._start_hook, daemon=True)
        self.thread.start()

    # ── Hook işleyici ──────────────────────────────────────────────────────────
    def hook_proc(self, nCode, wParam, lParam):
        if nCode >= 0:
            flags    = lParam.contents.flags
            injected = bool(flags & (LLMHF_INJECTED | LLMHF_LOWER_IL_INJECTED))

            if not injected:
                if wParam == WM_LBUTTONDOWN:
                    self.left_down = True
                elif wParam == WM_LBUTTONUP:
                    self.left_down = False
                elif wParam == WM_RBUTTONDOWN:
                    self.right_down = True
                elif wParam == WM_RBUTTONUP:
                    self.right_down = False
                elif wParam == WM_MBUTTONDOWN:
                    self.mid_down = True
                elif wParam == WM_MBUTTONUP:
                    self.mid_down = False
                elif wParam == WM_XBUTTONDOWN:
                    xbtn = (lParam.contents.mouseData >> 16) & 0xFFFF
                    if xbtn == XBUTTON1: self.x1_down = True
                    elif xbtn == XBUTTON2: self.x2_down = True
                elif wParam == WM_XBUTTONUP:
                    xbtn = (lParam.contents.mouseData >> 16) & 0xFFFF
                    if xbtn == XBUTTON1: self.x1_down = False
                    elif xbtn == XBUTTON2: self.x2_down = False

        return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

    def _start_hook(self):
        self.hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, self.pointer, 0, 0)
        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    # ── Temel durum sorguları ──────────────────────────────────────────────────
    def is_down(self, trigger: str) -> bool:
        return {
            "left":  self.left_down,
            "right": self.right_down,
            "mid":   self.mid_down,
            "x1":    self.x1_down,
            "x2":    self.x2_down,
        }.get(trigger, False)


# Tek global tracker örneği
TRACKER = PhysicalMouseTracker()


# ─────────────────────────────────────────────────────────────────────────────
class MacroWorker(threading.Thread):
    """Bir makro slotunu yöneten iş parçacığı."""

    def __init__(self, worker_id, sequence, trigger, tracker, helper_key="None", repeat_mode="while_pressed", repeat_delay=13):
        super().__init__(daemon=True)
        self.worker_id       = worker_id
        self.tracker         = tracker
        self.running         = True
        self.feature_enabled = False
        self.trigger         = trigger
        self.sequence        = sequence
        self.helper_key      = helper_key.lower()
        self.repeat_mode     = repeat_mode
        self.repeat_delay    = repeat_delay

    def toggle(self):
        self.feature_enabled = not self.feature_enabled
        return self.feature_enabled

    def force_stop(self):
        self.feature_enabled = False

    def run(self):
        bypass_active   = False
        can_press = self.trigger in ("left", "right", "mid", "x1", "x2")

        def _mb(btn):
            if btn == "x1": return "x"
            if btn == "mid": return "middle"
            return btn

        has_fired = False
        is_looping = False
        last_pressed_state = False

        while self.running:
            if self.feature_enabled:
                # ── Tetik tuşu basılı mı? ──────────────────────────────────
                is_pressed = self.tracker.is_down(self.trigger)
                
                # Kenar tetikleme tespiti
                just_pressed = is_pressed and not last_pressed_state
                last_pressed_state = is_pressed

                should_run = False
                
                if self.repeat_mode == "while_pressed":
                    should_run = is_pressed
                elif self.repeat_mode == "once":
                    if just_pressed:
                        should_run = True
                elif self.repeat_mode == "toggle":
                    if just_pressed:
                        is_looping = not is_looping
                    should_run = is_looping

                if should_run and self.sequence:
                    # Bypass sistemi
                    h_key = self.helper_key
                    bypass_condition = (h_key != "none" and keyboard.is_pressed(h_key))

                    if bypass_condition:
                        if not bypass_active:
                            if can_press:
                                try: mouse.press(_mb(self.trigger))
                                except: pass
                            bypass_active = True
                        time.sleep(0.01)
                        continue
                    else:
                        if bypass_active:
                            if can_press:
                                try: mouse.release(_mb(self.trigger))
                                except: pass
                            bypass_active = False

                    # Dizi çalıştır
                    active_simulated = set()
                    
                    for action in self.sequence:
                        if not self.running or not self.feature_enabled:
                            break
                        
                        # "while_pressed" modunda eğer tuş bırakılırsa diziyi kes
                        if self.repeat_mode == "while_pressed" and not self.tracker.is_down(self.trigger):
                            break

                        t = action.get("type")
                        if t == "delay":
                            time.sleep(action.get("ms", 0) / 1000.0)
                        elif t == "mouse":
                            act = action.get("action")
                            tgt = _mb(action.get("target", "left"))
                            try:
                                if act == "click":  
                                    try: eel.visualizeClick(tgt, True)()
                                    except: pass
                                    mouse.click(tgt)
                                    try: eel.visualizeClick(tgt, False)()
                                    except: pass
                                elif act == "down": 
                                    try: eel.visualizeClick(tgt, True)()
                                    except: pass
                                    mouse.press(tgt)
                                    active_simulated.add(("mouse", tgt))
                                elif act == "up":   
                                    mouse.release(tgt)
                                    active_simulated.discard(("mouse", tgt))
                                    try: eel.visualizeClick(tgt, False)()
                                    except: pass
                            except: pass
                        elif t == "keyboard":
                            act = action.get("action")
                            tgt = action.get("target", "a")
                            try:
                                if act == "press":  
                                    keyboard.send(tgt)
                                elif act == "down": 
                                    keyboard.press(tgt)
                                    active_simulated.add(("keyboard", tgt))
                                elif act == "up":   
                                    keyboard.release(tgt)
                                    active_simulated.discard(("keyboard", tgt))
                            except: pass

                    # Döngü biterken asılı kalan tuş ve fare tetiklerini temizle
                    for k_type, k_val in active_simulated:
                        try:
                            if k_type == "mouse": mouse.release(k_val)
                            elif k_type == "keyboard": keyboard.release(k_val)
                        except: pass
                    
                    # Global tekrar gecikmesi
                    if self.repeat_delay > 0:
                        time.sleep(self.repeat_delay / 1000.0)
                else:
                    if bypass_active:
                        if can_press:
                            try: mouse.release(_mb(self.trigger))
                            except: pass
                        bypass_active = False

            else:
                # Özellik kapalıyken state'leri sıfırla
                is_looping = False
                last_pressed_state = False

            time.sleep(0.002)


# ─────────────────────────────────────────────────────────────────────────────
class AutoClicker:
    """Tüm makro motorunu yöneten üst sınıf."""

    def __init__(self, update_callback=None):
        self.workers = {}
        self.update_callback = update_callback

    def apply_profiles(self, profiles_data):
        """Active profile verisini alır ve worker'ları günceller."""
        # Klavye kancalarını temizle
        try: keyboard.unhook_all()
        except: pass

        # Eski worker'ları durdur
        for w in self.workers.values():
            w.running = False
            w.force_stop()
        
        self.workers = {}
        
        for prof_name, data in profiles_data.items():
            # "slots" yerine doğrudan "left" ve "right" anahtarlarına bakıyoruz
            for slot in ("left", "right"):
                cfg = data.get(slot)
                if not cfg: continue

                w_id = f"{prof_name}_{slot}"
                worker = MacroWorker(
                    worker_id=w_id,
                    sequence=cfg.get("sequence", []),
                    trigger=cfg.get("trigger", "left"),
                    tracker=TRACKER,
                    helper_key=cfg.get("helper_key", "None"),
                    repeat_mode=cfg.get("repeat_mode", "while_pressed"),
                    repeat_delay=cfg.get("repeat_delay", 13)
                )
                self.workers[w_id] = worker
                worker.start()

                # Hotkey kaydı
                hk = cfg.get("hotkey", "").strip().lower()
                if hk and hk not in ("tuşa bas", "···", ""):
                    try:
                        keyboard.add_hotkey(hk, self.toggle_slot, args=[prof_name, slot], suppress=True)
                    except Exception as e:
                        print(f"Hotkey Error ({hk}): {e}")

    def toggle_slot(self, prof_name, slot):
        w_id = f"{prof_name}_{slot}"
        if w_id in self.workers:
            enabled = self.workers[w_id].toggle()
            if self.update_callback:
                # GUI (worker_id, is_enabled) bekliyor
                self.update_callback(w_id, enabled)
            return enabled
        return False

    def get_slot_state(self, prof_name, slot):
        w_id = f"{prof_name}_{slot}"
        if w_id in self.workers:
            return self.workers[w_id].feature_enabled
        return False

    def on_closing(self):
        for w in self.workers.values():
            w.running = False
