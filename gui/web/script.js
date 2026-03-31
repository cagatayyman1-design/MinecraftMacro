// Global State
let activeProfile = "";
let currentData = null;
let batsList = [];
let activeSlot = "left";
let systemHwid = "";


// MUSIC DATA
const gamingPlaylist = [
    { title: "GANG", artist: "Motive", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487195630108784/MOTIVE_-_GANG.m4a?ex=69ccf53a&is=69cba3ba&hm=4f5a6b27be88facbb6a6db67bb28286280ec830af0277cf98e99c6bba82e3fa0&" },
    { title: "YIN YANG", artist: "Motive", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487196406190110/MOTIVE_-_YIN_YANG.m4a?ex=69ccf53a&is=69cba3ba&hm=8139423174a024296dd84201b31422daa726f1ae5dc41d13d7649a7b78602202&" },
    { title: "AQUAFINA", artist: "Motive", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487196762570832/Motive_-_AQUAFINA.m4a?ex=69ccf53a&is=69cba3ba&hm=f5ef5c0c873c7d712a18881123e1cca2323d0caf179e357f6c4322c9f7fb313f&" },
    { title: "HANIMEFENDI", artist: "Motive", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487197123543120/MOTIVE_-_HANIMEFENDI.m4a?ex=69ccf53a&is=69cba3ba&hm=8b86b5a4a2e03fc7d94cd56d915f06fec81e07ee36cbb31b886ebf857dc7d8d8&" },
    { title: "PVG", artist: "Motive", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487197375070281/MOTIVE_-_PVG.m4a?ex=69ccf53a&is=69cba3ba&hm=4cdb2882ed97c96dc6af8206241892d0779bc7687600a26454bc13939d9025d8&" },
    { title: "KARANLIK", artist: "Motive", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487197685579796/MOTIVE_-_KARANLIK.m4a?ex=69ccf53a&is=69cba3ba&hm=f25bcb3605c426b9874c71ae790633c0b86d14c0bcb4c6eb35a592cf42396a5e&" },
    { title: "SAVANA", artist: "Motive", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487198008414308/MOTIVE_-_SAVANA.m4a?ex=69ccf53a&is=69cba3ba&hm=c4b26d0b5effa004b4155a2635dc68c3ac9b96270736e7df526cb5253f22cb06&" },
    { title: "PINGUI", artist: "Savana", url: "https://cdn.discordapp.com/attachments/1488487117662453830/1488487198293753998/Savana_-_PINGUI.m4a?ex=69ccf53a&is=69cba3ba&hm=ec0ff8d8bded2c2e15cf7de707c78d9a092e57353e165eff373ddbc96f5bbe01&" }
];

let musicAudio = new Audio();
musicAudio.volume = 0.5; // Başlangıç sesi %50
let currentTrack = -1;
let isMusicPlaying = false;

eel.expose(updateStatus);
function updateStatus(w_id, enabled) {
    const pill = document.getElementById('status-pill');
    const lbl = document.getElementById('lbl-status');
    if(enabled) {
        pill.className = "status-pill online";
        lbl.innerText = "MAKRO AKTİF";
    } else {
        pill.className = "status-pill offline";
        lbl.innerText = "UYKUDA";
    }
}

eel.expose(appendBatLog);
function appendBatLog(msg) {
    const term = document.getElementById('bat-terminal');
    if (term) {
        term.innerText += msg + "\n";
        term.scrollTop = term.scrollHeight;
    }
}

eel.expose(updateDownloadProgress);
function updateDownloadProgress(percent, finished = false) {
    const container = document.getElementById('dl-progress-container');
    const bar = document.getElementById('dl-progress-bar');
    const pctTxt = document.getElementById('dl-percent');
    
    if (percent === -1) {
        document.getElementById('dl-status-text').innerText = "HATA!";
        document.getElementById('dl-status-text').style.color = "var(--red)";
        return;
    }

    container.classList.remove('hidden');
    bar.style.width = percent + '%';
    pctTxt.innerText = percent + '%';

    if (finished) {
        container.classList.add('hidden');
        document.getElementById('dl-complete-actions').classList.remove('hidden');
    }
}


window.onload = function() {
    // Audio Autoplay Setup
    const audio = document.getElementById('login-audio');
    let hasStarted = false;
    const startAudio = () => {
        if(hasStarted) return;
        if(audio) {
            audio.volume = 0.1;
            audio.play().then(() => {
                hasStarted = true;
                // Remove all triggers
                ["mousedown", "keydown", "mousemove", "touchstart"].forEach(ev => {
                    window.removeEventListener(ev, startAudio);
                });
            }).catch(e => console.log("Audio waiting for stronger interaction..."));
        }
    };
    
    // Add multiple interaction triggers
    ["mousedown", "keydown", "mousemove", "touchstart"].forEach(ev => {
        window.addEventListener(ev, startAudio);
    });

    // HWID Al
    eel.get_system_hwid()(hwid => {
        systemHwid = hwid;
        const hd = document.getElementById('license-key');
        if(hd) hd.value = hwid;
    });

    // Güncelleme Kontrolü - En önce yapalım
    handleUpdateCheck();

    eel.check_saved_login()(res => {
        if(res.success) {
            document.getElementById('login-modal').classList.add('hidden');
            stopLoginMedia();
            document.getElementById('app-container').classList.remove('hidden');
            document.getElementById('lbl-user').innerText = res.user;
            document.getElementById('lbl-expiry').innerText = res.expiry || "Sınırsız";
            loadInitialData();
            setTimeout(renderPlaylist, 100);
        }
    });
};

function copyHwid() {
    if(systemHwid) {
        eel.copy_to_clipboard(systemHwid)(ok => {
            const errorTxt = document.getElementById('login-error');
            errorTxt.style.color = "var(--green)";
            errorTxt.innerText = "✔ HWID Kopyalandı!";
            setTimeout(() => { errorTxt.innerText=""; errorTxt.style.color="var(--red)"; }, 3000);
        });
    }
}

function verifyLogin() {
    const errorTxt = document.getElementById('login-error');
    const btn = document.querySelector('.login-btn');
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> KONTROL EDİLİYOR...';
    btn.disabled = true;

    eel.verify_hwid_login()(res => {
        btn.innerHTML = '<i class="fa-solid fa-shield-halved"></i> GİRİŞ YAP';
        btn.disabled = false;
        
        if(res.success) {
            document.getElementById('login-modal').classList.add('hidden');
            stopLoginMedia();
            document.getElementById('app-container').classList.remove('hidden');
            document.getElementById('lbl-user').innerText = res.user;
            document.getElementById('lbl-expiry').innerText = res.expiry || "Sınırsız";
            loadInitialData();
            setTimeout(renderPlaylist, 100);
        } else {
            errorTxt.style.color = "var(--red)";
            errorTxt.innerText = "✗ " + res.msg;
            setTimeout(() => errorTxt.innerText="", 3500);
        }
    });
}

function doLogout() {
    eel.logout()(res => {
        document.getElementById('app-container').classList.add('hidden');
        const modal = document.getElementById('login-modal');
        modal.classList.remove('hidden');
        
        // Restart media
        const vid = document.getElementById('login-video');
        if(vid) vid.play();
        const aud = document.getElementById('login-audio');
        if(aud) {
            aud.volume = document.getElementById('login-vol').value;
            aud.play();
        }
    });
}

function setLoginVolume(val) {
    const aud = document.getElementById('login-audio');
    const icon = document.getElementById('vol-icon');
    if(aud) aud.volume = val;

    // Dinamik İkon
    if(val == 0) icon.className = "fa-solid fa-volume-xmark";
    else if(val < 0.5) icon.className = "fa-solid fa-volume-low";
    else icon.className = "fa-solid fa-volume-high";
}

let lastVol = 0.1;
function toggleMute() {
    const aud = document.getElementById('login-audio');
    const sl = document.getElementById('login-vol');
    
    if(aud.volume > 0) {
        lastVol = aud.volume;
        setLoginVolume(0);
        sl.value = 0;
    } else {
        setLoginVolume(lastVol || 0.1);
        sl.value = lastVol || 0.1;
    }
}

function stopLoginMedia() {
    const vid = document.getElementById('login-video');
    const aud = document.getElementById('login-audio');
    if(vid) vid.pause();
    if(aud) {
        // Fade out music
        let vol = aud.volume;
        const fade = setInterval(() => {
            if (vol > 0.05) {
                vol -= 0.05;
                aud.volume = vol;
            } else {
                aud.pause();
                clearInterval(fade);
            }
        }, 50);
    }
}

function loadInitialData() {
    eel.get_initial_data()(res => {
        activeProfile = res.active_profile;
        document.getElementById('active-profile-name').value = activeProfile;
        currentData = res.current_profile_data;
        batsList = res.bats;
        
        if(res.theme) document.body.setAttribute('data-theme', res.theme);

        renderProfiles(res.profiles);
        renderSlotUI();
        renderBats();
    });
}

function handleUpdateCheck() {
    eel.check_update()(res => {
        if(res && res.update_available) {
            openUpdateModal(res);
        }
    });
}

function openUpdateModal(data) {
    const modal = document.getElementById('update-modal');
    document.getElementById('update-version').innerText = data.latest_version;
    document.getElementById('update-changelog').innerText = data.changelog;
    
    // Reset UI states
    document.getElementById('update-initial-actions').classList.remove('hidden');
    document.getElementById('dl-progress-container').classList.add('hidden');
    document.getElementById('dl-complete-actions').classList.add('hidden');
    document.getElementById('dl-progress-bar').style.width = '0%';
    document.getElementById('dl-status-text').innerText = "İndiriliyor...";

    const btn = document.getElementById('btn-update-now');
    btn.onclick = () => {
        document.getElementById('update-initial-actions').classList.add('hidden');
        document.getElementById('dl-progress-container').classList.remove('hidden');
        eel.start_download(data.url)();
    };

    modal.classList.remove('hidden');
}

function closeUpdateModal() {
    document.getElementById('update-modal').classList.add('hidden');
}

function switchPage(page) {
    console.log("Switching to page:", page);
    document.querySelectorAll('.page').forEach(e => e.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(e => e.classList.remove('active'));
    
    const targetPage = document.getElementById('page-' + page);
    if (targetPage) {
        targetPage.classList.remove('hidden');
        // Force refresh for certain pages
        if (page === 'music') {
            setTimeout(renderPlaylist, 50);
        }
        if (page === 'bats') {
            renderBats();
        }
    }
    
    const navBtn = document.getElementById('nav-' + page);
    if (navBtn) navBtn.classList.add('active');
}

let isMiniMode = false;
function toggleMiniMode() {
    isMiniMode = !isMiniMode;
    if(isMiniMode) {
        document.body.classList.add('mini-mode');
        // Pencereyi küçültmeye çalış (bazı tarayıcı modları engelleyebilir ama CSS yetecektir)
        window.resizeTo(400, 600);
        showToast("Mini Mod", "Uygulama kompakt görünüme geçti.");
    } else {
        document.body.classList.remove('mini-mode');
        window.resizeTo(1000, 660);
        showToast("Normal Mod", "Geniş görünüme dönüldü.");
    }
}

function showToast(title, msg) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = "toast glass";
    toast.innerHTML = `
        <div class="toast-content">
            <strong>${title}</strong>
            <p>${msg}</p>
        </div>
    `;
    container.appendChild(toast);
    
    // Smooth entry
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

function setSlot(slot) {
    activeSlot = slot;
    document.getElementById('tab-left').classList.remove('active');
    document.getElementById('tab-right').classList.remove('active');
    document.getElementById('tab-'+slot).classList.add('active');
    renderSlotUI();
}

function setActTab(tab) {
    document.querySelectorAll('.act-tab').forEach(e => e.classList.remove('active'));
    document.querySelectorAll('.act-content').forEach(e => e.classList.add('hidden'));
    document.getElementById('act-btn-'+tab).classList.add('active');
    document.getElementById('act-'+tab).classList.remove('hidden');
}

function renderProfiles(profMap) {
    const pdiv = document.getElementById('profile-list');
    pdiv.innerHTML = "";
    Object.keys(profMap).forEach(k => {
        const div = document.createElement('div');
        div.className = "profile-row " + (k === activeProfile ? "active" : "");
        div.innerHTML = `<i class="fa-solid fa-${k===activeProfile?'gem':'diamond'}"></i> ${k}`;
        div.onclick = () => {
            eel.set_active_profile(k)(r => {
                if(r.success) {
                    activeProfile = k;
                    document.getElementById('active-profile-name').value = k;
                    currentData = r.data;
                    renderProfiles(profMap);
                    loadInitialData();
                }
            });
        };
        pdiv.appendChild(div);
    });
}

function newProfile() { eel.new_profile()(res => { if(res.success) loadInitialData(); }); }
function deleteProfile() { eel.delete_profile()(res => { if(res.success) loadInitialData(); }); }
function renameProfile() {
    const n = document.getElementById('active-profile-name').value;
    eel.rename_profile(n)(res => { if(res) loadInitialData(); else document.getElementById('active-profile-name').value=activeProfile; });
}

function renderSlotUI() {
    const data = currentData[activeSlot];
    document.getElementById('sel-trigger').value = data.trigger || "left";
    document.getElementById('sel-helper').value = data.helper_key || "None";
    document.getElementById('btn-hotkey').innerText = (data.hotkey || "TUŞA BAS").toUpperCase();
    
    // NEW: Repeat Settings
    document.getElementById('sel-repeat-mode').value = data.repeat_mode || "while_pressed";
    document.getElementById('inp-repeat-ms').value = data.repeat_delay !== undefined ? data.repeat_delay : 13;
    
    renderSequence();
}

let isListening = false;
function listenHotkey() {
    if(isListening) return;
    isListening = true;
    const btn = document.getElementById('btn-hotkey');
    btn.innerText = "···";
    btn.classList.add('listening');
    
    const handler = (e) => {
        e.preventDefault();
        window.removeEventListener('keydown', handler);
        isListening = false;
        btn.classList.remove('listening');
        
        let key = e.key.toLowerCase();
        if(key===' '||key==='escape'||key==='enter'||key==='backspace') {
            btn.innerText = "Tuşa Bas";
            currentData[activeSlot].hotkey = "";
        } else {
            btn.innerText = key.toUpperCase();
            currentData[activeSlot].hotkey = key;
        }
        markUnsaved();
    };
    window.addEventListener('keydown', handler);
}
function clearHotkey() { document.getElementById('btn-hotkey').innerText = "Tuşa Bas"; currentData[activeSlot].hotkey = ""; markUnsaved(); }
function markUnsaved() {
    const sb = document.getElementById('btn-save');
    sb.innerText = "✓ KAYDET VE UYGULA";
    sb.classList.remove('btn-success');
    sb.classList.add('btn-primary');
}

function renderSequence() {
    const sl = document.getElementById('sequence-list');
    sl.innerHTML = "";
    const seq = currentData[activeSlot].sequence || [];
    if(seq.length === 0) {
        sl.innerHTML = `<div style="text-align:center; padding: 40px; color: var(--text-muted); font-size:12px;">— Henüz eylem eklenmedi —</div>`;
        return;
    }
    seq.forEach((act, i) => {
        const row = document.createElement('div');
        row.className = "action-row";
        let icon = "", name = "";
        if(act.type === "delay") { icon = "stopwatch"; name = `${act.ms} ms  bekleme`; } 
        else if(act.type === "mouse") { icon = "mouse"; name = `Fare · ${act.target} · ${act.action}`; }
        else if(act.type === "keyboard") { icon = "keyboard"; name = `Klavye · [${act.target}] · ${act.action}`; }
        
        row.innerHTML = `
            <div class="act-idx">${(i+1).toString().padStart(2,'0')}</div>
            <div class="act-icon"><i class="fa-solid fa-${icon}"></i></div>
            <div class="act-name">${name}</div>
            <div class="act-ctrls">
                <button class="btn-icon" onclick="moveAct(${i}, -1)"><i class="fa-solid fa-arrow-up"></i></button>
                <button class="btn-icon" onclick="moveAct(${i}, 1)"><i class="fa-solid fa-arrow-down"></i></button>
                <button class="btn-icon danger" onclick="delAct(${i})"><i class="fa-solid fa-xmark"></i></button>
            </div>
        `;
        sl.appendChild(row);
    });
}

function moveAct(idx, dir) {
    const seq = currentData[activeSlot].sequence;
    if(idx+dir >= 0 && idx+dir < seq.length) {
        [seq[idx], seq[idx+dir]] = [seq[idx+dir], seq[idx]];
        renderSequence(); markUnsaved();
    }
}
function delAct(idx) { currentData[activeSlot].sequence.splice(idx,1); renderSequence(); markUnsaved(); }

function addAction() {
    let act = null;
    if(!document.getElementById('act-delay').classList.contains('hidden')) {
        let ms = parseInt(document.getElementById('inp-delay').value) || 50;
        act = { type: "delay", ms: ms };
    } else if(!document.getElementById('act-mouse').classList.contains('hidden')) {
        act = { type: "mouse", target: document.getElementById('inp-mouse-btn').value, action: document.getElementById('inp-mouse-act').value };
    } else {
        let k = document.getElementById('inp-key').value.trim() || 'w';
        act = { type: "keyboard", target: k.toLowerCase(), action: document.getElementById('inp-key-act').value };
    }
    currentData[activeSlot].sequence.push(act);
    renderSequence(); markUnsaved();
}

function saveSettings() {
    const trg = document.getElementById('sel-trigger').value;
    const hlp = document.getElementById('sel-helper').value;
    let hk = document.getElementById('btn-hotkey').innerText.toLowerCase();
    if(hk.includes("bas") || hk.includes("···")) hk = "";
    
    const seq = currentData[activeSlot].sequence;
    
    // VERİ GÜNCELLEME (Bug Fix: Kaydettikten sonra sekmeler arası geçişte veri kaybolmaması için)
    currentData[activeSlot].trigger = trg;
    currentData[activeSlot].helper_key = hlp;
    currentData[activeSlot].hotkey = hk;
    
    // NEW: Repeat Settings
    const repMode = document.getElementById('sel-repeat-mode').value;
    const repDelay = parseInt(document.getElementById('inp-repeat-ms').value) || 0;
    currentData[activeSlot].repeat_mode = repMode;
    currentData[activeSlot].repeat_delay = repDelay;

    eel.save_slot_data(activeSlot, trg, hk, hlp, seq, repMode, repDelay)(res => {
        const sb = document.getElementById('btn-save');
        sb.classList.remove('btn-primary');
        sb.classList.add('btn-success');
        sb.innerText = "✔ KAYDEDİLDİ";
        setTimeout(() => { sb.innerText = "✓ KAYDET VE UYGULA"; }, 2000);
    });
}

let selBat = null;
function renderBats() {
    const bl = document.getElementById('bat-list');
    bl.innerHTML = "";
    if(!batsList.length) { bl.innerHTML = `<div style="text-align:center; padding:30px;font-size:12px;color:var(--text-muted)">Henüz eklenmedi.</div>`; return; }
    batsList.forEach(b => {
        const row = document.createElement('div');
        row.className = "bat-row " + (selBat===b.path ? "active":"");
        row.innerHTML = `<i class="fa-solid fa-bolt"></i> <span style="flex:1">${b.name}</span>`;
        row.onclick = () => selectBat(b);
        bl.appendChild(row);
    });
}
function selectBat(b) {
    selBat = b.path;
    document.getElementById('lbl-bat-name').innerText = "⚡ " + b.name;
    document.getElementById('lbl-bat-path').innerText = b.path;
    document.getElementById('btn-bat-run').disabled = false;
    document.getElementById('btn-bat-delete').disabled = false;
    renderBats();
}
function addBat() { eel.create_dialog_bat()(r => { if(r.success){ batsList=r.bats; renderBats();} }); }
function deleteBat() { eel.delete_bat(selBat)(r => { if(r.success){
    batsList=r.bats; selBat=null; 
    document.getElementById('lbl-bat-name').innerText="Bat dosyası seçin…";
    document.getElementById('lbl-bat-path').innerText="";
    document.getElementById('btn-bat-run').disabled = true;
    document.getElementById('btn-bat-delete').disabled = true;
    renderBats();
}}); }
function runBat() {
    const t = document.getElementById('bat-terminal');
    t.innerText = "";
    window.appendBatLog(`[BAŞLATILIYOR] ${selBat}\n------------------------------------------`);
    eel.run_bat(selBat)();
}

function switchThemeOption(theme) {
    document.body.setAttribute('data-theme', theme);
    eel.save_theme(theme)();
}

// CPS TEST LOGIC
function handleCpsClick() {
    if (!cpsTesting) {
        startCpsTest();
    }
    
    cpsClicks++;
    document.getElementById('total-clicks').innerText = cpsClicks;
}

function startCpsTest() {
    cpsTesting = true;
    cpsClicks = 0;
    cpsStartTime = Date.now();
    document.getElementById('btn-cps-test').innerText = "TIKLA TIKLA TIKLA!";
    
    cpsTimer = setInterval(() => {
        let elapsed = Date.now() - cpsStartTime;
        let remaining = Math.max(0, (CPS_DURATION - elapsed) / 1000);
        
        // Update Timer Text
        document.getElementById('test-timer').innerText = remaining.toFixed(1) + "s";
        
        // Update Circle Progress
        let progress = (elapsed / CPS_DURATION) * 283;
        document.getElementById('cps-progress').style.strokeDashoffset = 283 - progress;
        
        // Update Live CPS
        let currentCps = cpsClicks / (elapsed / 1000);
        document.getElementById('cps-count').innerText = currentCps.toFixed(1);
        
        if (elapsed >= CPS_DURATION) {
            endCpsTest();
        }
    }, 50);
}

function endCpsTest() {
    clearInterval(cpsTimer);
    cpsTesting = false;
    
    let finalCps = cpsClicks / (CPS_DURATION / 1000);
    document.getElementById('cps-count').innerText = finalCps.toFixed(1);
    document.getElementById('btn-cps-test').innerText = "TEKRAR TEST ET";
    document.getElementById('test-timer').innerText = "BİTTİ!";
    
    // Achievement Check
    if (finalCps >= 15) {
        document.querySelector('.ach-item:first-child').classList.add('unlocked');
    }
}

// MUSIC PLAYER LOGIC
function renderPlaylist() {
    console.log("Rendering playlist...");
    const list = document.getElementById('playlist');
    if(!list) {
        console.error("Playlist element not found!");
        return;
    }
    
    list.innerHTML = "";
    
    if(!gamingPlaylist || gamingPlaylist.length === 0) {
        list.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">
            <i class="fa-solid fa-music-slash" style="font-size:32px; margin-bottom:10px; opacity:0.3;"></i>
            <p>Müzik listesi yüklenemedi.</p>
        </div>`;
        return;
    }

    gamingPlaylist.forEach((track, index) => {
        const item = document.createElement('div');
        item.className = "track-item" + (currentTrack == index ? " active" : "");
        item.onclick = () => playTrack(index);
        item.innerHTML = `
            <i class="fa-solid fa-circle-play"></i>
            <div class="track-info">
                <strong>${track.title}</strong>
                <small>${track.artist}</small>
            </div>
        `;
        list.appendChild(item);
    });
}

function playTrack(index) {
    if(index == currentTrack) {
        toggleMusic();
        return;
    }
    currentTrack = index;
    const track = gamingPlaylist[index];
    musicAudio.src = track.url;
    musicAudio.play();
    isMusicPlaying = true;
    updatePlayerUI();
    renderPlaylist();
}

function toggleMusic() {
    if(currentTrack == -1) {
        playTrack(0);
        return;
    }
    if(isMusicPlaying) {
        musicAudio.pause();
        isMusicPlaying = false;
    } else {
        musicAudio.play();
        isMusicPlaying = true;
    }
    updatePlayerUI();
}

function updatePlayerUI() {
    const playBtn = document.getElementById('btn-play-pause');
    const container = document.getElementById('page-music');
    if(isMusicPlaying) {
        playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
        container.classList.add('music-playing');
    } else {
        playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
        container.classList.remove('music-playing');
    }
    
    if(currentTrack != -1) {
        document.getElementById('music-title').innerText = gamingPlaylist[currentTrack].title;
        document.getElementById('music-artist').innerText = gamingPlaylist[currentTrack].artist;
    }
}

function setMusicVolume(val) {
    musicAudio.volume = val;
}

function nextTrack() {
    let next = (currentTrack + 1) % gamingPlaylist.length;
    playTrack(next);
}

function prevTrack() {
    let prev = (currentTrack - 1 + gamingPlaylist.length) % gamingPlaylist.length;
    playTrack(prev);
}

musicAudio.onended = () => {
    nextTrack();
};

musicAudio.ontimeupdate = () => {
    const seek = document.getElementById('music-seek');
    const cur = document.getElementById('music-current');
    if (!isNaN(musicAudio.duration)) {
        seek.value = (musicAudio.currentTime / musicAudio.duration) * 100;
        cur.innerText = formatTime(musicAudio.currentTime);
    }
};

musicAudio.onloadedmetadata = () => {
    const total = document.getElementById('music-total');
    total.innerText = formatTime(musicAudio.duration);
};

function formatTime(seconds) {
    let min = Math.floor(seconds / 60);
    let sec = Math.floor(seconds % 60);
    return min + ":" + (sec < 10 ? "0" + sec : sec);
}

function seekMusic(val) {
    if (!isNaN(musicAudio.duration)) {
        musicAudio.currentTime = (val / 100) * musicAudio.duration;
    }
}
