import time
import threading

try:
    from pypresence import Presence
except ImportError:
    Presence = None

class DiscordRPCManager:
    def __init__(self, client_id="1488472058395361352"):
        self.client_id = client_id
        self.rpc = None
        self.running = False
        self.current_profile = "Bilinmiyor"
        self.start_time = int(time.time())
        self.thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self):
        if not Presence:
            print("[Discord RPC] 'pypresence' kurulu değil. Es geçiliyor.")
            return
        self.running = True
        self.thread.start()

    def update_profile(self, profile_name):
        self.current_profile = profile_name
        # Force immediate update if connected by skipping the usual delay 
        # (Though we shouldn't spam Discord API too fast, 15s is the normal rate limit)

    def _connect(self):
        try:
            if self.rpc:
                self.rpc.close()
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            print("[Discord RPC] Discord'a bağlanıldı!")
            return True
        except Exception as e:
            # Sadece kapalıyken veya sorun varken log spamı yapmamak için printi kaldırabiliriz.
            # print(f"[Discord RPC] Bağlantı başarısız (Discord kapalı olabilir): {e}")
            self.rpc = None
            return False

    def _run_loop(self):
        connected = False
        while self.running:
            if not connected:
                connected = self._connect()
                if not connected:
                    time.sleep(15) # Reconnect denemesi için bekle
                    continue
            
            try:
                self.rpc.update(
                    state=f"Aktif Profil: {self.current_profile}",
                    details="Sky Project Makro Oynuyor",
                    start=self.start_time,
                    large_image="sky_logo", # Kullanıcı portalden bu isimde resim yüklerse gözükür
                    large_text="Sky Project Premium"
                )
            except Exception as e:
                # print(f"[Discord RPC] Güncelleme Hatası: {e}")
                connected = False
            
            # Discord API allows updates every 15 seconds
            for _ in range(15):
                if not self.running:
                    break
                time.sleep(1)

    def stop(self):
        self.running = False
        if self.rpc:
            try:
                self.rpc.close()
            except:
                pass
