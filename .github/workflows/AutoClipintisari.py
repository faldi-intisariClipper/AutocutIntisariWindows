# ============================================================================
# ⚠️ INSTRUKSI MUTLAK & MENGIKAT UNTUK AI (DO NOT DELETE OR MODIFY) ⚠️
# ============================================================================
# KEPADA AI SELANJUTNYA:
# 1. BASE CODE ADALAH V7.21 (FINAL FIX MAC/WIN).
# 2. DATA PATH MENGGUNAKAN LOGIKA PLATFORM (APPDATA / LIBRARY).
# 3. FITUR UTAMA: 
#    - SYNC FOLDER TXT & SMART NAMING.
#    - INTERNET DATE CHECK (ANTI-CHEAT).
#    - SILENT CHECKER (AUTO-KILL).
#    - SETTINGS UI: YT, HOOKS, & DATA FOLDER MANAGERS.
#    - FORCED UPDATE SYSTEM (BLUEPRINT 2).
#    - SILENT AUTO-UPDATE (WINDOWS: BAT | MAC: BROWSER).
# 4. LINK LISENSI: TETAP MENGGUNAKAN DATABASE PC (TERPISAH).
# ============================================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys
import json
import time
import webbrowser
import shutil
import platform # WAJIB ADA untuk deteksi Mac/Windows
from datetime import datetime
import uuid
import random
import re 

# --- IMPORT LIBRARY DOWNLOADER ---
try:
    import requests
    import yt_dlp 
except ImportError:
    pass 

# ============================================================================
# KONFIGURASI APLIKASI & PATH SYSTEM (HYBRID WINDOWS & MAC)
# ============================================================================
CURRENT_VERSION = "7.21" 

LICENSE_URL = "https://gist.githubusercontent.com/faldi-intisariClipper/794da43201a68e0e72737d6d6d808993/raw"

# Deteksi URL download berdasarkan OS
if platform.system() == "Windows":
    GITHUB_EXE_URL = "https://github.com/faldi-intisariClipper/AutocutIntisariWindows/releases/latest/download/AutoClipintisari.exe"
else:
    # Untuk Mac, arahkan ke file ZIP/DMG
    GITHUB_EXE_URL = "https://github.com/faldi-intisariClipper/AutocutIntisariWindows/releases/latest/download/Intisari-Clipper-MacOS.zip"

VERSION_URL = "https://raw.githubusercontent.com/faldi-intisariClipper/AutocutIntisariWindows/main/version.txt"
ADMIN_WA = "628567870040" 

GOOGLE_SHEET_API = "https://script.google.com/macros/s/AKfycbz1snzcZOhlZHvF9piJJJ9tyiQOUsJIkV78yXU8KOdBOhknaz5QZdt6x-RMAVGu0uZA/exec"

MEMBER_ID = "TRIAL-USER"
CURRENT_LICENSE_KEY = "" 

# --- KONFIGURASI FLAG SUBPROCESS (FIX CRASH MAC) ---
# SETTING FLAG AGAR TIDAK CRASH DI MAC
if platform.system() == "Windows":
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0 # Di Mac nilainya 0 (tidak dipakai)

# --- PATH SYSTEM CERDAS (MAC & WINDOWS) ---
if platform.system() == "Windows":
    FFMPEG_DIR = r"C:\ProgramData\ffmpeg"
    base_data_dir = os.getenv('APPDATA')
else:
    # Menggunakan path standar Mac / Linux
    FFMPEG_DIR = "/usr/local/bin" 
    base_data_dir = os.path.expanduser("~/Library/Application Support")

# Gabungkan path
USER_DATA_DIR = os.path.join(base_data_dir, "IntisariSmart")

if not os.path.exists(USER_DATA_DIR):
    try: os.makedirs(USER_DATA_DIR)
    except: pass

DATA_FILE = os.path.join(USER_DATA_DIR, "inti_stats.json")
LICENSE_FILE = os.path.join(USER_DATA_DIR, "inti_id.key") 

# Migrasi data lama (Khusus Windows)
if platform.system() == "Windows":
    old_data_path = os.path.join(FFMPEG_DIR, "inti_stats.json")
    try:
        if os.path.exists(old_data_path) and not os.path.exists(DATA_FILE):
            shutil.copy2(old_data_path, DATA_FILE)
    except: pass

if getattr(sys, 'frozen', False):
    APP_EXE_NAME = os.path.basename(sys.executable)
    APP_DIR = os.path.dirname(sys.executable)
    # Tambahan untuk Mac App Bundle
    if platform.system() == "Darwin" and ".app" in APP_DIR: 
        APP_DIR = os.path.expanduser("~/Downloads") 
else:
    APP_EXE_NAME = "AutoClipintisari.py"
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOAD_DIR = os.path.join(APP_DIR, "Downloads")
if not os.path.exists(DOWNLOAD_DIR):
    try: os.makedirs(DOWNLOAD_DIR)
    except: pass

# --- TEMA TAMPILAN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
COLOR_BG = "#1e1e2e"          
COLOR_SIDEBAR = "#252535"     
COLOR_CARD_BG = "#2b2b3b"     
COLOR_ACCENT = "#e67e22"
COLOR_INPUT_BG = "#2b2b3b"      
COLOR_DASH_BLUE = "#3498db"
COLOR_DASH_GREEN = "#2ecc71"
COLOR_DASH_PURPLE = "#9b59b6"
COLOR_DASH_RED = "#e74c3c"
COLOR_TEXT_SUB = "#bdc3c7"
COLOR_PRO_BG = "#1f3a4d"
COLOR_PRO_BORDER = "#3498db"
COLOR_HISTORY_CARD = "#232330"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_persistent_random_id():
    try:
        if os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, 'r') as f:
                saved_id = f.read().strip()
                if len(saved_id) > 5: return saved_id
        random_suffix = ''.join(random.choices('ABCDEF0123456789', k=6))
        new_id = f"INTI-{random_suffix}"
        with open(LICENSE_FILE, 'w') as f: f.write(new_id)
        return new_id
    except: return f"INTI-{uuid.uuid4().hex[:6].upper()}"

def get_ffmpeg_path():
    # 1. Cek jika aplikasi berjalan sebagai Bundle (PyInstaller untuk Mac/Win)
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        if platform.system() == "Windows":
            ffmpeg_bin = "ffmpeg.exe"
        else:
            ffmpeg_bin = "ffmpeg"
            
        bundled_path = os.path.join(bundle_dir, ffmpeg_bin)
        if os.path.exists(bundled_path):
            return bundled_path

    # 2. Cek path manual sistem (Fallback)
    system_ffmpeg = os.path.join(FFMPEG_DIR, "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")
    if os.path.exists(system_ffmpeg): return system_ffmpeg
    
    # 3. Cek di folder aplikasi
    local_candidates = [
        os.path.join(APP_DIR, "ffmpeg.exe"), 
        os.path.join(os.getcwd(), "ffmpeg.exe"),
        os.path.join(APP_DIR, "ffmpeg"),
        os.path.join(os.getcwd(), "ffmpeg")
    ]
    for path in local_candidates:
        if os.path.exists(path): return path     
    
    return "ffmpeg"

def sanitize_filename(name):
    return "".join([c for c in name if c.isalnum() or c in " ._-"])

def get_internet_date():
    try:
        r = requests.get("http://worldtimeapi.org/api/timezone/Asia/Jakarta", timeout=5)
        data = r.json()
        return int(data['datetime'][:10].replace('-', ''))
    except:
        return int(datetime.now().strftime("%Y%m%d"))

# --- BLUEPRINT 2: LOGIKA VERSI CHECKER ---
def get_remote_version():
    try:
        r = requests.get(f"{VERSION_URL}?t={int(time.time())}", timeout=5)
        return r.text.strip() if r.status_code == 200 else CURRENT_VERSION
    except:
        return CURRENT_VERSION

def is_update_required(remote_v):
    def parse(v): return tuple(map(int, v.split('.')))
    try:
        return parse(remote_v) > parse(CURRENT_VERSION)
    except:
        return False

# ============================================================================
# UI COMPONENTS
# ============================================================================
class ActionCard(ctk.CTkFrame):
    def __init__(self, parent, title, desc, icon, color, command):
        super().__init__(parent, fg_color=color, corner_radius=15)
        self.command = command
        self.bind("<Button-1>", self.on_click)
        self.configure(cursor="hand2")
        self.grid_columnconfigure(0, weight=1)
        self.lbl_icon = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 42))
        self.lbl_icon.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        self.lbl_title = ctk.CTkLabel(self, text=title, font=("Segoe UI", 20, "bold"), text_color="white")
        self.lbl_title.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 0))
        self.lbl_desc = ctk.CTkLabel(self, text=desc, font=("Segoe UI", 12), text_color="#ecf0f1")
        self.lbl_desc.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 20))
        self.btn_arrow = ctk.CTkLabel(self, text="➜", font=("Arial", 18), text_color="white")
        self.btn_arrow.place(relx=0.85, rely=0.1)
        for w in self.winfo_children(): w.bind("<Button-1>", self.on_click); w.configure(cursor="hand2")
    def on_click(self, event):
        if self.command: self.command()

class DownloadTaskRow(ctk.CTkFrame):
    def __init__(self, parent, app, url, target_dir, use_cookies=False):
        super().__init__(parent, fg_color=COLOR_CARD_BG, corner_radius=10, border_width=1, border_color="#333")
        self.app = app 
        self.url = url
        self.target_dir = target_dir
        self.use_cookies = use_cookies
        self.pack(fill="x", pady=5, padx=5)
        self.grid_columnconfigure(1, weight=1)
        
        icon_char = "🌐"; icon_color = "gray"
        if "youtu" in url: icon_char = "▶️"; icon_color = "#ff0000"
        elif "tiktok" in url: icon_char = "🎵"; icon_color = "#00f2ea"
        elif "instagram" in url: icon_char = "📷"; icon_color = "#e1306c"
        elif "facebook" in url: icon_char = "📘"; icon_color = "#1877F2"
        
        self.btn_icon = ctk.CTkButton(self, text=icon_char, width=40, height=40, fg_color="#222", hover=False, font=("Segoe UI Emoji", 20), text_color=icon_color)
        self.btn_icon.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        self.lbl_title = ctk.CTkLabel(self, text=f"Processing: {url[:50]}...", font=("Segoe UI", 13, "bold"), anchor="w")
        self.lbl_title.grid(row=0, column=1, sticky="ew", padx=10, pady=(10, 0))
        self.progress = ctk.CTkProgressBar(self, height=6, progress_color=COLOR_DASH_GREEN)
        self.progress.set(0)
        self.progress.grid(row=1, column=1, sticky="ew", padx=10, pady=(5, 10))
        self.lbl_size = ctk.CTkLabel(self, text="-- MB", font=("Consolas", 11), text_color="gray", width=120) 
        self.lbl_size.grid(row=0, column=2, rowspan=2, padx=10)
        self.lbl_status = ctk.CTkButton(self, text="Pending", width=80, height=24, fg_color="#333", hover=False, font=("Segoe UI", 10, "bold"), corner_radius=12)
        self.lbl_status.grid(row=0, column=3, rowspan=2, padx=10)
        
        # [FIXED] TOMBOL OPEN FOLDER CROSS-PLATFORM
        self.btn_open = ctk.CTkButton(self, text="📂", width=30, height=30, fg_color="#444", command=self.open_target_folder)
        self.btn_open.grid(row=0, column=4, rowspan=2, padx=(0, 10))
        threading.Thread(target=self.start_download, daemon=True).start()

    def open_target_folder(self):
        if os.path.exists(self.target_dir):
            if platform.system() == "Windows":
                os.startfile(self.target_dir)
            else:
                subprocess.run(["open", self.target_dir])

    def on_progress(self, d):
        if d['status'] == 'downloading':
            try:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_mb = downloaded / 1048576
                total_mb = total / 1048576
                if total > 0:
                    self.lbl_size.configure(text=f"{downloaded_mb:.1f}/{total_mb:.1f} MB")
                    self.progress.set(downloaded / total)
                else:
                    self.lbl_size.configure(text=f"{downloaded_mb:.1f} MB")
            except: pass
        elif d['status'] == 'finished': self.update_status("Merging...", COLOR_ACCENT)

    def start_download(self):
        if not os.path.exists(self.target_dir): os.makedirs(self.target_dir, exist_ok=True)
        ffmpeg_exe = get_ffmpeg_path()
        prefix = "HK"; is_yt = False
        if "youtube.com" in self.url or "youtu.be" in self.url: prefix = "YT"; is_yt = True
        elif "instagram" in self.url: prefix = "IG"
        elif "facebook" in self.url: prefix = "FB"
        elif "tiktok" in self.url: prefix = "TK"

        try:
            self.update_status("Fetching Info...", COLOR_DASH_BLUE)
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(self.url, download=False)
                raw_title = info.get('title', 'Video')

            if is_yt:
                clean_title = "".join([c if c.isalnum() or c.isspace() else "" for c in raw_title])
                words = clean_title.split()[:4]
                final_name = f"YT_{'_'.join(words)}"
                short_name = final_name

                txt_folder = self.app.app_data.get("txt_source_path")
                if not txt_folder or not os.path.exists(txt_folder):
                    txt_folder = os.path.join(DOWNLOAD_DIR, "INTISARI_DATA")
                    os.makedirs(txt_folder, exist_ok=True)
                
                txt_file_path = os.path.join(txt_folder, f"{short_name}.txt")
                
                if not os.path.exists(txt_file_path):
                    with open(txt_file_path, "w", encoding="utf-8") as f:
                        f.write(f"# Timestamp for: {short_name}\n# Format: Start|End|Name\n")
                    self.app.after(0, lambda: self.lbl_status.configure(text=f"Ready: .txt"))

            else:
                if "counters" not in self.app.app_data:
                    self.app.app_data["counters"] = {"YT": 0, "IG": 0, "FB": 0, "TK": 0, "HK": 0}
                current_count = self.app.app_data["counters"].get(prefix, 0)
                self.app.app_data["counters"][prefix] = current_count + 1
                count = self.app.app_data["counters"][prefix]
                self.app.save_data()
                final_name = f"{prefix}_{count:04d}"
        except Exception as e:
            print(f"Naming Error: {e}"); final_name = f"{prefix}_Video_{int(time.time())}"; raw_title = "Unknown Video"

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(self.target_dir, f"{final_name}.%(ext)s"),
            'progress_hooks': [self.on_progress],
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
            'noplaylist': True, 'quiet': True, 'no_warnings': True, 'overwrites': True
        }

        if ffmpeg_exe and ffmpeg_exe != "ffmpeg": ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_exe)
        if self.use_cookies: ydl_opts['cookiesfrombrowser'] = ('chrome',); self.update_status("Cookies...", "orange")

        try:
            self.update_status("Downloading", COLOR_DASH_BLUE)
            self.lbl_title.configure(text=f"{final_name} ({raw_title[:20]}...)")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                final_full_path = os.path.join(self.target_dir, f"{final_name}.mp4")
                self.app.log_download_activity(self.url, raw_title, "Success", full_path=final_full_path)
                self.app.kirim_data_sheet("Download PC", f"Sukses download dari {prefix}")
                
            self.update_status("Completed", COLOR_DASH_GREEN); self.progress.set(1)
        except Exception as e:
            raw_err = str(e)
            clean_err = re.sub(r'\x1b\[[0-9;]*m', '', raw_err)
            
            if "ffmpeg" in clean_err.lower(): 
                display_err = "ERROR: FFmpeg not found!"
            elif "Sign in" in clean_err: 
                display_err = "Login Required (Use Secure Mode)"
            else: 
                display_err = f"ERR: {clean_err[:30]}..."
                
            self.lbl_title.configure(text=display_err)
            self.app.log_download_activity(self.url, "FAILED_VIDEO", "Error", error_msg=clean_err[:80])
            self.update_status("Failed", COLOR_DASH_RED)
            self.app.kirim_data_sheet("Error PC", f"Gagal Download {prefix} | Link: {self.url} | Info: {clean_err[:100]}")

    def update_status(self, text, color):
        try: self.lbl_status.configure(text=text, fg_color=color)
        except: pass

class UpdateBlocker(ctk.CTk):
    def __init__(self, new_ver):
        super().__init__()
        self.title("CRITICAL UPDATE REQUIRED")
        self.geometry("450x300")
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
        
        x = (self.winfo_screenwidth()/2) - (450/2); y = (self.winfo_screenheight()/2) - (300/2)
        self.geometry('%dx%d+%d+%d' % (450, 300, x, y))

        frame = ctk.CTkFrame(self, fg_color="#1e1e2e")
        frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="🚀 VERSI BARU TERSEDIA", font=("Arial", 22, "bold"), text_color="#e67e22").pack(pady=30)
        ctk.CTkLabel(frame, text=f"Versi {CURRENT_VERSION} sudah tidak didukung.\nSilakan update ke v{new_ver} untuk lanjut.", font=("Arial", 14)).pack(pady=5)
        
        # [MODIFIED] Tombol Update sekarang memanggil method self.start_update
        ctk.CTkButton(frame, text="PROSES UPDATE OTOMATIS", height=50, fg_color="#2ecc71", 
                      command=self.start_update).pack(pady=30, padx=50, fill="x")

    def start_update(self):
        # DETEKSI OS DULU
        if platform.system() == "Windows":
            # Logika Windows (Script Bat)
            bat_script = f"""
@echo off
timeout /t 2 /nobreak
del "{sys.executable}"
curl -L -o "AutoClipintisari.exe" "{GITHUB_EXE_URL}"
start AutoClipintisari.exe
del "%~f0"
            """
            bat_path = os.path.join(os.path.dirname(sys.executable), "updater_temp.bat")
            with open(bat_path, "w") as f: f.write(bat_script)
            
            # Gunakan CREATE_NEW_CONSOLE khusus Windows agar command prompt muncul terpisah
            subprocess.Popen([bat_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit()
        else:
            # Logika Mac (Buka Browser)
            messagebox.showinfo("Update Tersedia", "Versi baru tersedia untuk macOS.\nSilakan download dan replace aplikasi lama.")
            webbrowser.open("https://github.com/faldi-intisariClipper/AutocutIntisariWindows/releases")
            sys.exit()

# ============================================================================
# LOGIN WINDOW
# ============================================================================
class LoginWindow(ctk.CTk):
    def __init__(self, current_id):
        super().__init__()
        self.title("Aktivasi Lisensi - Intisari Clips")
        self.geometry("400x450")
        self.current_id = current_id
        x = (self.winfo_screenwidth()/2) - (400/2); y = (self.winfo_screenheight()/2) - (450/2)
        self.geometry('%dx%d+%d+%d' % (400, 450, x, y))
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG); main_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(main_frame, text="🔑 INPUT LICENSE", font=("Segoe UI", 22, "bold"), text_color=COLOR_DASH_BLUE).pack(pady=(40, 5))
        
        ctk.CTkLabel(main_frame, text="Masukkan Lisensi Key atau Kode Trial.\n(Contoh Trial: AUTOCUT-TRIAL-0502)", font=("Segoe UI", 12), text_color="gray").pack()
        
        box = ctk.CTkFrame(main_frame, fg_color=COLOR_CARD_BG, corner_radius=10); box.pack(pady=30, padx=30, fill="x")
        ctk.CTkLabel(box, text="License Key / Machine ID:", font=("Arial", 10), text_color="gray").pack(pady=(15,0))
        self.entry_id = ctk.CTkEntry(box, justify="center", font=("Consolas", 14, "bold"), width=280, fg_color="#1a1a24", border_width=1, border_color="#555")
        self.entry_id.insert(0, self.current_id); self.entry_id.configure(state="normal"); self.entry_id.pack(pady=(5, 20), padx=10)
        ctk.CTkButton(main_frame, text="1. Beli Lisensi (WhatsApp)", fg_color="#25D366", command=self.open_wa).pack(pady=10, padx=40, fill="x")
        self.btn_check = ctk.CTkButton(main_frame, text="2. Cek Lisensi / Masuk", fg_color=COLOR_DASH_BLUE, command=self.check_again); self.btn_check.pack(pady=10, padx=40, fill="x")
        self.lbl_status = ctk.CTkLabel(main_frame, text="...", font=("Arial", 11, "italic"), text_color="gray"); self.lbl_status.pack(side="bottom", pady=20)
    
    def open_wa(self):
        current_input = self.entry_id.get().strip(); self.clipboard_clear(); self.clipboard_append(current_input); self.update()
        msg = f"Halo Admin, saya mau beli lisensi Intisari Clipper.\nLicense ID saya: {current_input}"
        msg_encoded = msg.replace(' ', '%20').replace('\n', '%0A')
        webbrowser.open(f"https://wa.me/{ADMIN_WA}?text={msg_encoded}")
        self.lbl_status.configure(text="ID disalin! Paste di WhatsApp.", text_color="#2ecc71")
    
    def check_again(self):
        input_key = self.entry_id.get().strip()
        if not input_key: self.unlock_fail("Lisensi tidak boleh kosong."); return
        self.btn_check.configure(state="disabled", text="Memeriksa...", fg_color="gray")
        
        def _do_check():
            try:
                check_url = f"{LICENSE_URL}?t={int(time.time())}"
                response = requests.get(check_url, timeout=10)
                if response.status_code == 200:
                    db_text = response.text
                    
                    if input_key in db_text: 
                        global MEMBER_ID
                        global CURRENT_LICENSE_KEY
                        
                        match_trial = re.match(r"^INTISARI-TRIAL(\d+)-(\d{4})$", input_key)

                        if match_trial:
                            try:
                                trial_id = match_trial.group(1) 
                                mmdd = match_trial.group(2)     
                                bulan, hari = mmdd[:2], mmdd[2:4]
                                tgl_expired = int(f"2026{bulan}{hari}")
                                tgl_sekarang = get_internet_date()

                                if tgl_sekarang > tgl_expired:
                                    self.after(0, lambda: self.unlock_fail(f"Masa Trial Habis (Bln {bulan} Tgl {hari})"))
                                    return
                                MEMBER_ID = f"#TRIAL-{trial_id} (Exp: {hari}/{bulan})"
                            except:
                                self.after(0, lambda: self.unlock_fail("Gagal membaca tanggal Trial."))
                                return
                        else:
                            lines = db_text.splitlines()
                            for idx, line in enumerate(lines):
                                if input_key in line:
                                    MEMBER_ID = f"#{idx + 1 + 99}"
                                    break

                        CURRENT_LICENSE_KEY = input_key 
                        
                        if input_key != self.current_id:
                            with open(LICENSE_FILE, 'w') as f: f.write(input_key)
                        self.after(0, self.unlock_success); return
                        
                    self.after(0, lambda: self.unlock_fail("Lisensi tidak terdaftar."))
            except: self.after(0, lambda: self.unlock_fail("Gagal koneksi internet."))
            
        threading.Thread(target=_do_check, daemon=True).start()
    
    def unlock_fail(self, msg): self.btn_check.configure(state="normal", text="2. Cek Lisensi / Masuk", fg_color=COLOR_DASH_BLUE); self.lbl_status.configure(text=msg, text_color=COLOR_DASH_RED)
    def unlock_success(self): self.destroy(); app = ModernClipper(); app.mainloop()

# ============================================================================
# MAIN APPLICATION
# ============================================================================
class ModernClipper(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"INTISARI CLIPS v{CURRENT_VERSION} - Ultimate Edition")
        self.geometry("1200x800")
        self.app_data = self.load_data()
        self.nav_buttons = {} 
        self.download_queue_ui = None 
        
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.sidebar = self.create_sidebar(); self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG); self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1); self.content.grid_columnconfigure(0, weight=1)
        
        self.pages = {
            "dashboard": self.ui_dashboard(self.content),
            "batch_add": self.ui_batch_add(self.content),        
            "active_tasks": self.ui_active_tasks(self.content),  
            "clipper": self.ui_clipper(self.content),
            "history": self.ui_history(self.content),
            "settings": self.ui_settings(self.content)
        }
        self.switch_page("dashboard")
        
        self.after(3000, self.silent_update_check)
        self.after(5000, self.start_silent_license_checker)

    def silent_security_check(self):
        try:
            if not os.path.exists(LICENSE_FILE):
                messagebox.showerror("Security", "Lisensi Hilang! Silakan Login Ulang."); self.destroy(); sys.exit()
                
            with open(LICENSE_FILE, 'r') as f:
                saved_key = f.read().strip()
            
            r = requests.get(f"{LICENSE_URL}?t={int(time.time())}", timeout=5)
            if saved_key not in r.text:
                messagebox.showerror("Akses Terputus", "Lisensi tidak terdaftar atau sudah dicabut Admin. Aplikasi akan ditutup.")
                try: os.remove(LICENSE_FILE)
                except: pass
                self.destroy(); sys.exit()

            match_trial = re.match(r"^INTISARI-TRIAL(\d+)-(\d{4})$", saved_key)
            if match_trial:
                try:
                    mmdd = match_trial.group(2) 
                    bulan, hari = mmdd[:2], mmdd[2:4]
                    tgl_expired = int(f"2026{bulan}{hari}")
                    tgl_sekarang = get_internet_date()

                    if tgl_sekarang > tgl_expired:
                        messagebox.showerror("Masa Habis", f"Masa Trial Habis (Bln {bulan} Tgl {hari}).\nSilakan hubungi Admin WA: {ADMIN_WA}.")
                        try: os.remove(LICENSE_FILE)
                        except: pass
                        self.destroy(); sys.exit() 
                except: pass

            return True 
            
        except requests.exceptions.RequestException:
            return True 

    def start_silent_license_checker(self):
        def _checker_loop():
            while True:
                time.sleep(600) 
                try:
                    with open(LICENSE_FILE, 'r') as f: key = f.read().strip()
                    r = requests.get(f"{LICENSE_URL}?t={int(time.time())}", timeout=10)
                    if key not in r.text:
                        self.force_kill_app()
                        break
                except: pass
        
        threading.Thread(target=_checker_loop, daemon=True).start()

    def force_kill_app(self):
        if os.path.exists(LICENSE_FILE):
            try: os.remove(LICENSE_FILE)
            except: pass
        self.after(0, lambda: messagebox.showerror("License Revoked", "Lisensi Anda telah dinonaktifkan oleh Admin.\nAplikasi akan ditutup."))
        self.after(2000, lambda: os._exit(0)) 

    def load_data(self):
        default_txt_path = os.path.join(DOWNLOAD_DIR, "INTISARI_DATA")
        if not os.path.exists(default_txt_path):
            try: os.makedirs(default_txt_path, exist_ok=True)
            except: pass

        default = {
            "total_clips": 0, "last_run": "-", "history": [], "save_path": "",
            "yt_download_path": os.path.join(APP_DIR, "Downloads", "YouTube"),
            "hook_download_path": os.path.join(APP_DIR, "Downloads", "Hooks"),
            "txt_source_path": default_txt_path,
            "counters": {"YT": 0, "IG": 0, "FB": 0, "TK": 0, "HK": 0} 
        }
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f: 
                    data = json.load(f)
                    if "save_path" not in data: data["save_path"] = ""
                    if "yt_download_path" not in data: data["yt_download_path"] = default["yt_download_path"]
                    if "hook_download_path" not in data: data["hook_download_path"] = default["hook_download_path"]
                    if "txt_source_path" not in data: data["txt_source_path"] = default["txt_source_path"]
                    if "counters" not in data: data["counters"] = default["counters"]
                    return data
        except: pass
        return default
    
    def save_data(self):
        try:
            if not os.path.exists(USER_DATA_DIR): os.makedirs(USER_DATA_DIR)
            with open(DATA_FILE, 'w') as f: json.dump(self.app_data, f, indent=4)
        except Exception as e: print(f"Save error: {e}")

    def log_download_activity(self, url, title, status, error_msg="", full_path=None):
        platform = "Unknown"
        if "youtube" in url or "youtu.be" in url: platform = "YouTube"
        elif "tiktok" in url: platform = "TikTok"
        elif "instagram" in url: platform = "Instagram"
        elif "facebook" in url or "fb.watch" in url: platform = "Facebook"

        log_entry = {
            "type": "DOWNLOAD_LOG", 
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform,
            "url": url,
            "title": title,
            "status": status,
            "error": error_msg,
            "full_path": full_path, 
            "count": 1 
        }
        self.app_data["history"].insert(0, log_entry)
        if status == "Success":
            self.app_data["last_run"] = log_entry["date"]
        
        self.save_data()
        self.refresh_dashboard() 

    def kirim_data_sheet(self, aksi, detail):
        def _send():
            try:
                tipe = "Trial" if "TRIAL" in CURRENT_LICENSE_KEY.upper() else "Premium"
                payload = {
                    "member_id": f"#{MEMBER_ID.replace('#','')}",
                    "tipe_user": tipe,
                    "android_ver": "Windows PC",
                    "aksi": aksi,
                    "total_cut": str(self.app_data.get("total_clips", 0)),
                    "detail": detail
                }
                requests.post(GOOGLE_SHEET_API, json=payload, timeout=5)
            except: pass
        threading.Thread(target=_send, daemon=True).start()

    def load_most_recent(self):
        history = self.app_data.get("history", [])
        if not history:
             messagebox.showinfo("Info", "History kosong.")
             return

        for entry in history:
            video_path = entry.get("full_path")
            if video_path and os.path.exists(video_path):
                self.entry_src.delete(0, "end")
                self.entry_src.insert(0, video_path)
                
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                txt_folder = self.app_data.get("txt_source_path")
                txt_file_path = os.path.join(txt_folder, f"{base_name}.txt")

                status_txt = ""
                if os.path.exists(txt_file_path):
                    try:
                        with open(txt_file_path, 'r', encoding='utf-8') as f:
                            txt_content = f.read()
                        
                        self.txt_data.delete("0.0", "end")
                        self.txt_data.insert("0.0", txt_content)
                        status_txt = "\n✅ Data Timestamps (.txt) juga berhasil dimuat!"
                    except Exception as e:
                        status_txt = "\n⚠️ Gagal membaca file .txt."
                else:
                    status_txt = "\n⚠️ File .txt belum ada/belum dibuat."

                messagebox.showinfo("Auto-Load Sukses", f"Video dimuat: {base_name}{status_txt}")
                return
        
        messagebox.showinfo("Info", "Belum ada file download valid di history.")

    def contact_support(self):
        global MEMBER_ID
        is_premium = "TRIAL" not in str(MEMBER_ID).upper()

        if not is_premium:
            messagebox.showwarning(
                "Akses Dibatasi", 
                "Maaf, Fitur Support & Grup Diskusi hanya tersedia untuk Member PREMIUM.\n\n"
                "Untuk user Trial, silakan pelajari tutorial yang sudah disediakan di folder panduan atau YouTube kami."
            )
        else:
            choice = messagebox.askquestion(
                "Premium Support Hub", 
                "Pilih Jenis Bantuan:\n\n'Yes' : Masuk ke Grup Diskusi VIP\n'No' : Chat Admin Langsung (Private)",
                icon='question'
            )
            if choice == 'yes':
                webbrowser.open("https://chat.whatsapp.com/HqdL9MyyBTVIYvrclrjP48")
            else:
                msg = f"Halo Admin, saya Member Premium {MEMBER_ID}.\nButuh bantuan terkait Intisari Clips v{CURRENT_VERSION}..."
                msg_encoded = msg.replace(' ', '%20').replace('\n', '%0A')
                webbrowser.open(f"https://wa.me/{ADMIN_WA}?text={msg_encoded}")

    def switch_page(self, name):
        for page in self.pages.values(): page.grid_forget()
        self.pages[name].grid(row=0, column=0, sticky="nsew")
        for n, btn in self.nav_buttons.items(): btn.configure(fg_color="transparent", text_color=COLOR_TEXT_SUB)
        if name in self.nav_buttons: self.nav_buttons[name].configure(fg_color=COLOR_DASH_BLUE, text_color="white")
        if name == "dashboard": self.refresh_dashboard()
        if name == "history": self.refresh_history()

    def create_sidebar(self):
        frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        frame.grid_rowconfigure(10, weight=1) 
        
        logo_box = ctk.CTkFrame(frame, fg_color="transparent")
        logo_box.grid(row=0, column=0, pady=(40, 30), padx=20, sticky="ew")
        ctk.CTkLabel(logo_box, text="⚡ INTISARI CLIPS", font=("Arial Black", 18), text_color=COLOR_DASH_BLUE).pack(anchor="w")
        
        current_member = globals().get('MEMBER_ID', 'PC-USER')
        ctk.CTkLabel(logo_box, text=f"MEMBER ID: {current_member}", font=("Arial", 10, "bold"), text_color="white", fg_color=COLOR_ACCENT, corner_radius=5).pack(anchor="w", pady=(2,0))
        
        ctk.CTkLabel(frame, text="MAIN MENU", font=("Arial", 10, "bold"), text_color="gray").grid(row=1, column=0, padx=20, pady=(10,0), sticky="w")
        self.add_nav_btn(frame, "📊  Dashboard", "dashboard", 2)
        self.add_nav_btn(frame, "✂️  Batch Clipper", "clipper", 3)
        
        ctk.CTkLabel(frame, text="DOWNLOADER", font=("Arial", 10, "bold"), text_color="gray").grid(row=4, column=0, padx=20, pady=(20,0), sticky="w")
        self.add_nav_btn(frame, "➕  Add Batch Links", "batch_add", 5)
        self.add_nav_btn(frame, "⬇️  Active Tasks", "active_tasks", 6)
        
        ctk.CTkLabel(frame, text="SYSTEM", font=("Arial", 10, "bold"), text_color="gray").grid(row=7, column=0, padx=20, pady=(20,0), sticky="w")
        self.add_nav_btn(frame, "📜  History Log", "history", 8)
        self.add_nav_btn(frame, "⚙️  Settings", "settings", 9)
        ctk.CTkLabel(frame, text=f"v{CURRENT_VERSION}", font=("Arial", 10), text_color="gray").grid(row=11, column=0, pady=10)
        return frame

    def add_nav_btn(self, parent, text, name, row):
        btn = ctk.CTkButton(parent, text=text, anchor="w", font=("Segoe UI", 12, "bold"), height=40, corner_radius=8, fg_color="transparent", hover_color="#303040", command=lambda: self.switch_page(name))
        btn.grid(row=row, column=0, padx=15, pady=2, sticky="ew")
        self.nav_buttons[name] = btn

    def ui_dashboard(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        is_premium = "TRIAL" not in str(MEMBER_ID).upper()
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))

        status_text = "✨ PREMIUM STATUS" if is_premium else "⚠️ TRIAL MODE"
        status_color = COLOR_DASH_GREEN if is_premium else "#e74c3c"

        ctk.CTkLabel(header, text="Dashboard", font=("Segoe UI", 32, "bold"), text_color="white").pack(anchor="w")
        badge = ctk.CTkLabel(header, text=status_text, font=("Arial", 10, "bold"), text_color="white", fg_color=status_color, corner_radius=5)
        badge.pack(anchor="w", pady=(5,0))
        ctk.CTkLabel(header, text="Selamat datang kembali. Pilih menu di bawah untuk memulai.", font=("Segoe UI", 14), text_color="gray").pack(anchor="w")

        grid_cards = ctk.CTkFrame(frame, fg_color="transparent")
        grid_cards.pack(fill="x", padx=40, pady=10)
        grid_cards.grid_columnconfigure((0, 1, 2), weight=1, uniform="card") 

        card1 = ActionCard(grid_cards, title="Start Clipping", desc="Proses video otomatis (Auto-cut).", icon="✂️", color=COLOR_DASH_BLUE, command=lambda: self.switch_page("clipper"))
        card1.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        card2 = ActionCard(grid_cards, title="View History", desc="Lihat log hasil generate sebelumnya.", icon="📜", color=COLOR_DASH_GREEN, command=lambda: self.switch_page("history"))
        card2.grid(row=0, column=1, sticky="ew", padx=7.5)

        card3 = ActionCard(grid_cards, title="Settings & Update", desc="Cek update & Lisensi.", icon="⚙️", color=COLOR_DASH_PURPLE, command=lambda: self.switch_page("settings"))
        card3.grid(row=0, column=2, sticky="ew", padx=(15, 0))

        stats_box = ctk.CTkFrame(frame, fg_color=COLOR_CARD_BG, corner_radius=15, height=120)
        stats_box.pack(fill="x", padx=40, pady=20) 
        
        def add_stat_item(parent, icon, label, val_attr):
            box = ctk.CTkFrame(parent, fg_color="transparent")
            box.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            ctk.CTkLabel(box, text=icon, font=("Segoe UI Emoji", 30)).pack(side="left", padx=(0, 15))
            v_layout = ctk.CTkFrame(box, fg_color="transparent")
            v_layout.pack(side="left")
            val_lbl = ctk.CTkLabel(v_layout, text="...", font=("Segoe UI", 24, "bold"), text_color="white")
            val_lbl.pack(anchor="w")
            ctk.CTkLabel(v_layout, text=label, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")
            return val_lbl

        self.lbl_dash_total = add_stat_item(stats_box, "🎬", "Total Clips Created", "total_clips")
        ctk.CTkFrame(stats_box, width=1, height=60, fg_color="#404050").pack(side="left") 
        self.lbl_dash_last = add_stat_item(stats_box, "📅", "Last Activity", "last_run")

        support_btn_text = "💬 VIP SUPPORT & GROUP" if is_premium else "🔒 SUPPORT LOCKED (PREMIUM ONLY)"
        support_btn_color = "#25D366" if is_premium else "#333333"

        self.btn_support = ctk.CTkButton(
            frame, 
            text=support_btn_text, 
            fg_color=support_btn_color, 
            hover_color="#128C7E" if is_premium else "#333333",
            height=50, 
            font=("Arial", 14, "bold"),
            command=self.contact_support
        )
        self.btn_support.pack(pady=10, padx=40, fill="x")
        
        return frame

    def refresh_dashboard(self):
        if hasattr(self, 'lbl_dash_total'): self.lbl_dash_total.configure(text=str(self.app_data["total_clips"]))
        if hasattr(self, 'lbl_dash_last'): self.lbl_dash_last.configure(text=self.app_data["last_run"])

    def ui_batch_add(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        center_box = ctk.CTkFrame(frame, fg_color="transparent"); center_box.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.8)
        ctk.CTkLabel(center_box, text="Paste Multiple Links", font=("Segoe UI", 24, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(center_box, text="Supports YouTube, TikTok, Instagram, Facebook.", text_color="gray").pack(pady=(0, 20))
        self.txt_links = ctk.CTkTextbox(center_box, height=250, font=("Consolas", 14), fg_color="#1a1a24", border_width=1, border_color="#333", corner_radius=10); self.txt_links.pack(fill="x", pady=10)
        act_row = ctk.CTkFrame(center_box, fg_color=COLOR_CARD_BG, corner_radius=10, height=60); act_row.pack(fill="x", pady=10)
        
        self.btn_upd_engine = ctk.CTkButton(act_row, text="🔄 Update Engine", width=120, height=35, 
                                             fg_color="#444", font=("Segoe UI", 11, "bold"),
                                             command=lambda: threading.Thread(target=self.update_ytdlp_manual).start())
        self.btn_upd_engine.place(x=380, y=12) 

        ctk.CTkLabel(act_row, text="Video (Best Quality)", font=("Segoe UI", 12, "bold")).place(x=20, y=20)
        self.check_cookies = ctk.CTkCheckBox(act_row, text="Secure Mode (Chrome Cookies)", font=("Segoe UI", 11), text_color=COLOR_ACCENT); self.check_cookies.place(x=180, y=18)
        btn = ctk.CTkButton(act_row, text="✚ ADD TO QUEUE", width=150, height=35, fg_color=COLOR_DASH_BLUE, font=("Segoe UI", 12, "bold"), command=self.process_batch_links); btn.place(relx=0.95, rely=0.5, anchor="e")
        return frame

    def ui_active_tasks(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        head = ctk.CTkFrame(frame, fg_color="transparent"); head.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(head, text="Download Manager", font=("Segoe UI", 24, "bold")).pack(side="left")
        ctk.CTkButton(head, text="+ Add More", width=100, fg_color="#333", command=lambda: self.switch_page("batch_add")).pack(side="right")
        tbl_head = ctk.CTkFrame(frame, fg_color="transparent", height=30); tbl_head.pack(fill="x", padx=40)
        ctk.CTkLabel(tbl_head, text="FILE NAME", text_color="gray", font=("Arial", 10, "bold")).place(x=70, y=5)
        ctk.CTkLabel(tbl_head, text="SIZE", text_color="gray", font=("Arial", 10, "bold")).place(relx=0.6, y=5)
        ctk.CTkLabel(tbl_head, text="STATUS", text_color="gray", font=("Arial", 10, "bold")).place(relx=0.75, y=5)
        ctk.CTkLabel(tbl_head, text="ACTIONS", text_color="gray", font=("Arial", 10, "bold")).place(relx=0.9, y=5)
        self.scroll_tasks = ctk.CTkScrollableFrame(frame, fg_color="transparent"); self.scroll_tasks.pack(fill="both", expand=True, padx=30, pady=10)
        self.download_queue_ui = self.scroll_tasks
        return frame
    
    def update_ytdlp_silent(self):
        try:
            # [FIXED] GUNAKAN FLAG KHUSUS
            subprocess.Popen([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"], 
                             creationflags=CREATE_NO_WINDOW)
        except: pass

    def update_ytdlp_manual(self):
        self.lbl_status.configure(text="Updating Engine... Mohon tunggu sebentar.")
        self.btn_upd_engine.configure(state="disabled", text="Updating...")
        
        try:
            # [FIXED] GUNAKAN FLAG KHUSUS
            process = subprocess.Popen([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"], 
                                        creationflags=CREATE_NO_WINDOW)
            process.wait() 
            messagebox.showinfo("Update Success", "Engine Download (yt-dlp) berhasil diperbarui ke versi terbaru!")
        except Exception as e:
            messagebox.showerror("Update Error", f"Gagal memperbarui engine: {str(e)}")
        
        self.btn_upd_engine.configure(state="normal", text="🔄 Update Engine")
        self.lbl_status.configure(text="Ready to process")

    def process_batch_links(self):
        if not self.silent_security_check(): return 

        raw = self.txt_links.get("1.0", "end").strip()
        if not raw: return
        
        threading.Thread(target=self.update_ytdlp_silent, daemon=True).start()

        links = [l.strip() for l in raw.split('\n') if l.strip().startswith('http')]
        use_cookie = self.check_cookies.get()
        if not links: messagebox.showwarning("Warning", "No valid links detected."); return
        
        self.switch_page("active_tasks")
        for url in links:
            if "youtube.com" in url or "youtu.be" in url:
                target_dir = self.app_data.get("yt_download_path")
            else:
                target_dir = self.app_data.get("hook_download_path")
            
            DownloadTaskRow(self.download_queue_ui, self, url, target_dir, use_cookies=use_cookie)
            
        self.txt_links.delete("1.0", "end")

    def ui_clipper(self, parent):
        frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text="Batch Video Clipper", font=("Arial", 28, "bold"), text_color="white").grid(row=0, column=0, pady=(30, 20), padx=40, sticky="w")
        
        box_source = ctk.CTkFrame(frame, fg_color=COLOR_INPUT_BG, corner_radius=15)
        box_source.grid(row=1, column=0, padx=40, pady=(0, 20), sticky="ew")
        
        row_src_head = ctk.CTkFrame(box_source, fg_color="transparent"); row_src_head.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(row_src_head, text="SOURCE VIDEO", font=("Arial", 12, "bold"), text_color=COLOR_DASH_BLUE).pack(side="left")
        
        row_file = ctk.CTkFrame(box_source, fg_color="transparent")
        row_file.pack(fill="x", padx=20, pady=(0, 15))
        
        self.entry_src = ctk.CTkEntry(row_file, placeholder_text="Select video or click Latest...", height=40)
        self.entry_src.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(row_file, text="⚡ Latest", width=80, height=40, 
                      fg_color=COLOR_DASH_GREEN, hover_color="#27ae60",
                      command=self.load_most_recent).pack(side="right", padx=(0, 10))
        
        ctk.CTkButton(row_file, text="📂 Browse", width=100, height=40, 
                      fg_color="#3f3f4f", command=self.browse_file).pack(side="right")

        row_out = ctk.CTkFrame(box_source, fg_color="transparent"); row_out.pack(fill="x", padx=20, pady=(0, 15))
        frame_path = ctk.CTkFrame(row_out, fg_color="#222", corner_radius=6)
        frame_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.lbl_save_path = ctk.CTkLabel(frame_path, text=self.app_data.get("save_path") or "Default: Same as Video Source", text_color="gray", font=("Consolas", 10), anchor="w")
        self.lbl_save_path.pack(side="left", padx=10, pady=5)
        ctk.CTkButton(frame_path, text="Change Folder", width=80, height=20, fg_color="#444", font=("Arial", 10), command=self.change_save_path).pack(side="right", padx=5, pady=5)
        frame_proj = ctk.CTkFrame(row_out, fg_color="transparent")
        frame_proj.pack(side="right")
        ctk.CTkLabel(frame_proj, text="Project Name:", font=("Arial", 11, "bold"), text_color="gray").pack(side="left", padx=(0,5))
        self.entry_project = ctk.CTkEntry(frame_proj, width=150, placeholder_text="Ex: Horor_Eps1")
        self.entry_project.pack(side="left")

        box_pro = ctk.CTkFrame(frame, fg_color=COLOR_PRO_BG, border_width=2, border_color=COLOR_PRO_BORDER, corner_radius=15)
        box_pro.grid(row=2, column=0, padx=40, pady=(0, 20), sticky="ew")
        badge = ctk.CTkLabel(box_pro, text=" PRO FEATURES ", fg_color=COLOR_PRO_BORDER, text_color="white", font=("Arial", 10, "bold"), corner_radius=6); badge.place(x=15, y=-10)
        grid_pro = ctk.CTkFrame(box_pro, fg_color="transparent"); grid_pro.pack(fill="x", padx=15, pady=(20, 15))
        col1 = ctk.CTkFrame(grid_pro, fg_color="transparent"); col1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="SOCIAL MEDIA RATIO", font=("Arial", 11, "bold"), text_color=COLOR_DASH_BLUE).pack(anchor="w")
        self.combo_ratio = ctk.CTkComboBox(col1, values=["Original (16:9)", "TikTok/Reels (9:16)", "Instagram Feed (1:1)"]); self.combo_ratio.pack(fill="x", pady=(5, 10))
        col2 = ctk.CTkFrame(grid_pro, fg_color="transparent"); col2.pack(side="left", fill="both", expand=True, padx=(5, 5))
        ctk.CTkLabel(col2, text="PLAYBACK SPEED", font=("Arial", 11, "bold"), text_color=COLOR_DASH_BLUE).pack(anchor="w")
        self.combo_speed = ctk.CTkComboBox(col2, values=["1.0x (Normal)", "1.25x (Faster)", "1.5x (Speed Up)", "0.8x (Slow)"]); self.combo_speed.pack(fill="x", pady=(5, 10))
        col3 = ctk.CTkFrame(grid_pro, fg_color="transparent"); col3.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(col3, text="BACKGROUND MODE", font=("Arial", 11, "bold"), text_color=COLOR_DASH_BLUE).pack(anchor="w")
        self.combo_bg = ctk.CTkComboBox(col3, values=["Blur Effect (Default)", "Solid Black", "Solid White"])
        self.combo_bg.pack(fill="x", pady=(5, 10))
        self.check_merge = ctk.CTkCheckBox(box_pro, text="🔀 Merge All Clips into One Video (Compilation Mode)", font=("Arial", 12, "bold"), text_color="white"); self.check_merge.pack(anchor="w", padx=20, pady=(0, 20))

        box_std = ctk.CTkFrame(frame, fg_color=COLOR_INPUT_BG, corner_radius=15)
        box_std.grid(row=3, column=0, padx=40, pady=(0, 20), sticky="ew")
        row_pad = ctk.CTkFrame(box_std, fg_color="transparent"); row_pad.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(row_pad, text="PADDING (Offset Detik):", font=("Arial", 11, "bold"), text_color="gray").pack(side="left", padx=(0, 10))
        self.entry_pad_start = ctk.CTkEntry(row_pad, width=60, placeholder_text="Awal"); self.entry_pad_start.pack(side="left", padx=5)
        ctk.CTkLabel(row_pad, text="+s", font=("Arial", 10), text_color="gray").pack(side="left", padx=(0, 15))
        self.entry_pad_end = ctk.CTkEntry(row_pad, width=60, placeholder_text="Akhir"); self.entry_pad_end.pack(side="left", padx=5)
        ctk.CTkLabel(row_pad, text="+s", font=("Arial", 10), text_color="gray").pack(side="left", padx=(0, 15))
        ctk.CTkLabel(row_pad, text="MODE:", font=("Arial", 11, "bold"), text_color="gray").pack(side="left", padx=(20, 10))
        self.combo_mode = ctk.CTkComboBox(row_pad, values=["Fast Cut (Copy Stream)", "Re-Encode (High Quality)"], width=180); self.combo_mode.pack(side="left")

        box_data = ctk.CTkFrame(frame, fg_color=COLOR_INPUT_BG, corner_radius=15); box_data.grid(row=4, column=0, padx=40, pady=(0, 20), sticky="nsew")
        hdr_data = ctk.CTkFrame(box_data, fg_color="transparent"); hdr_data.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(hdr_data, text="TIMESTAMPS (Start|End|Name)", font=("Arial", 12, "bold"), text_color=COLOR_DASH_BLUE).pack(side="left")
        ctk.CTkButton(hdr_data, text="📥 Import .txt", width=100, height=25, fg_color="#3f3f4f", command=self.import_txt_data).pack(side="right")
        self.txt_data = ctk.CTkTextbox(box_data, font=("Consolas", 14), height=150, wrap="none", fg_color="#1a1a24", text_color="#dcdcdc"); self.txt_data.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        bar = ctk.CTkFrame(frame, fg_color="transparent"); bar.grid(row=5, column=0, padx=40, pady=(0, 40), sticky="ew")
        self.lbl_status = ctk.CTkLabel(bar, text="Ready to process", font=("Arial", 12)); self.lbl_status.pack(side="top", anchor="w", pady=(0, 5))
        self.progress = ctk.CTkProgressBar(bar, height=12, progress_color=COLOR_ACCENT); self.progress.set(0); self.progress.pack(side="top", fill="x", pady=(0, 15))
        self.btn_process = ctk.CTkButton(bar, text="START PROCESSING", height=55, font=("Arial", 16, "bold"), fg_color=COLOR_ACCENT, hover_color="#d35400", corner_radius=10, command=self.run_process_thread); self.btn_process.pack(fill="x")
        return frame

    def ui_history(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        head = ctk.CTkFrame(frame, fg_color="transparent")
        head.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(head, text="History Logs", font=("Segoe UI", 24, "bold")).pack(side="left")
        ctk.CTkButton(head, text="Clear", width=80, fg_color=COLOR_DASH_RED, command=self.clear_history).pack(side="right")
        self.scroll_hist = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self.scroll_hist.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        return frame

    def refresh_history(self):
        for w in self.scroll_hist.winfo_children(): w.destroy()
        logs = self.app_data.get("history", [])

        if not logs:
            ctk.CTkLabel(self.scroll_hist, text="Belum ada history.", text_color="gray", font=("Segoe UI", 14)).pack(pady=50)
            return

        for log in logs:
            if log.get("type") == "DOWNLOAD_LOG":
                card = ctk.CTkFrame(self.scroll_hist, fg_color="#1a1a24", border_width=1, border_color="#333")
                card.pack(fill="x", pady=5, padx=10)
                
                status = log.get('status', 'Unknown')
                status_color = COLOR_DASH_GREEN if status == "Success" else COLOR_DASH_RED
                header = ctk.CTkFrame(card, fg_color="transparent")
                header.pack(fill="x", padx=10, pady=5)
                
                platform = log.get('platform', 'Unknown')
                ctk.CTkLabel(header, text=f"🌐 {platform}", font=("Arial", 11, "bold")).pack(side="left")
                ctk.CTkLabel(header, text=status, text_color=status_color, font=("Arial", 10, "bold")).pack(side="right")
                
                title = log.get('title', 'No Title')
                if len(title) > 60: title = title[:57] + "..."
                ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(anchor="w", padx=10)
                
                if status == "Error":
                    err = log.get('error', 'Unknown Error')
                    ctk.CTkLabel(card, text=f"⚠️ {err}", text_color="orange", font=("Arial", 10, "italic")).pack(anchor="w", padx=10)
                
                btn_row = ctk.CTkFrame(card, fg_color="transparent")
                btn_row.pack(anchor="e", padx=10, pady=5)

                if status == "Success":
                    file_display_name = os.path.basename(log.get('full_path', 'Unknown'))
                    ctk.CTkButton(btn_row, text="📄 Copy Name", width=100, height=24, fg_color="#34495e",
                                  command=lambda n=file_display_name: self.copy_to_clipboard(n, "Nama Video")).pack(side="left", padx=5)
                
                ctk.CTkButton(btn_row, text="🔗 Copy Link", width=100, height=24, fg_color="#34495e",
                              command=lambda u=log.get('url', ''): self.copy_to_clipboard(u, "Link")).pack(side="left", padx=5)
            
            else:
                card = ctk.CTkFrame(self.scroll_hist, fg_color=COLOR_CARD_BG, corner_radius=10)
                card.pack(fill="x", pady=8, padx=10)
                h_row = ctk.CTkFrame(card, fg_color="transparent")
                h_row.pack(fill="x", padx=15, pady=15)
                
                src_text = log.get('source', 'Unknown')
                if len(src_text) > 40: src_text = src_text[:37] + "..."
                ctk.CTkLabel(h_row, text="🎬 Source:", font=("Segoe UI", 11, "bold"), text_color=COLOR_DASH_BLUE).pack(side="left")
                ctk.CTkLabel(h_row, text=src_text, font=("Segoe UI", 13, "bold"), text_color="white").pack(side="left", padx=5)
                
                count = log.get('count', 1) 
                ctk.CTkLabel(h_row, text=f"Total: {count} Clips", font=("Segoe UI", 12, "bold"), text_color=COLOR_ACCENT).pack(side="right")
                
                s_row = ctk.CTkFrame(card, fg_color="transparent")
                s_row.pack(fill="x", padx=15, pady=(0, 10))
                ctk.CTkLabel(s_row, text=f"🕒 {log.get('date', '-')}", font=("Segoe UI", 10), text_color="gray").pack(side="left")
                
                content_box = ctk.CTkFrame(card, fg_color="transparent")
                content_box.pack(fill="x", padx=15, pady=(10, 15))
                btn_box = ctk.CTkFrame(content_box, fg_color="transparent")
                btn_box.pack(fill="x", pady=(0, 5))
                
                clips = log.get('clips', [])
                clip_text = "\n".join([f"• {c}" for c in clips])
                btn_copy_list = ctk.CTkButton(btn_box, text="📋 Copy Filenames", width=120, height=24, fg_color="#444", hover_color="#555", font=("Arial", 11), command=lambda t=clip_text: self.copy_to_clipboard(t, "Daftar File"))
                btn_copy_list.pack(side="right", padx=(5,0))
                
                raw_txt = log.get('raw_txt', "") 
                if raw_txt:
                    btn_reuse = ctk.CTkButton(btn_box, text="📝 Copy Raw Timestamps", width=160, height=24, fg_color=COLOR_DASH_BLUE, hover_color="#2980b9", font=("Arial", 11, "bold"), command=lambda t=raw_txt: self.copy_to_clipboard(t, "Timestamps"))
                    btn_reuse.pack(side="right")
                
                box_files = ctk.CTkTextbox(content_box, height=80, fg_color="#20202b", text_color="#ccc", font=("Consolas", 10))
                box_files.pack(fill="x")
                box_files.insert("0.0", clip_text)
                box_files.configure(state="disabled")

    def copy_to_clipboard(self, text, info_type="Teks"):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        try:
            if hasattr(self, 'lbl_status'):
                self.lbl_status.configure(text=f"Copied: {info_type}!")
        except: pass
        messagebox.showinfo("Copied", f"{info_type} berhasil disalin!\nAnda bisa mem-paste-nya kembali.")

    def clear_history(self):
        if messagebox.askyesno("Hapus Log", "Yakin ingin menghapus semua riwayat?\n(Total Stats tidak akan direset)"):
            self.app_data["history"] = []
            self.save_data()
            self.refresh_history()
    
    def ui_settings(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(frame, text="Settings & Path Management", font=("Segoe UI", 24, "bold")).pack(pady=(40, 20))
        
        yt_box = ctk.CTkFrame(frame, fg_color=COLOR_CARD_BG, corner_radius=10); yt_box.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(yt_box, text="YouTube Master Folder:", font=("Arial", 11, "bold")).pack(side="left", padx=15, pady=15)
        self.lbl_yt_path = ctk.CTkLabel(yt_box, text=self.app_data.get("yt_download_path"), text_color="gray")
        self.lbl_yt_path.pack(side="left", padx=10)
        ctk.CTkButton(yt_box, text="Change", width=80, command=lambda: self.change_specific_path("yt_download_path")).pack(side="right", padx=15)
        
        hook_box = ctk.CTkFrame(frame, fg_color=COLOR_CARD_BG, corner_radius=10); hook_box.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(hook_box, text="Hook Videos Folder (TikTok/FB/IG):", font=("Arial", 11, "bold")).pack(side="left", padx=15, pady=15)
        self.lbl_hook_path = ctk.CTkLabel(hook_box, text=self.app_data.get("hook_download_path"), text_color="gray")
        self.lbl_hook_path.pack(side="left", padx=10)
        ctk.CTkButton(hook_box, text="Change", width=80, command=lambda: self.change_specific_path("hook_download_path")).pack(side="right", padx=15)

        txt_box = ctk.CTkFrame(frame, fg_color=COLOR_CARD_BG, corner_radius=10); txt_box.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(txt_box, text="Timestamp Data Folder (.txt):", font=("Arial", 11, "bold")).pack(side="left", padx=15, pady=15)
        self.lbl_txt_path = ctk.CTkLabel(txt_box, text=self.app_data.get("txt_source_path"), text_color="gray")
        self.lbl_txt_path.pack(side="left", padx=10)
        ctk.CTkButton(txt_box, text="Change", width=80, command=lambda: self.change_specific_path("txt_source_path")).pack(side="right", padx=15)

        ctk.CTkButton(frame, text="Check App Update", height=40, fg_color=COLOR_DASH_BLUE, command=self.manual_update_check).pack(pady=30)
        ctk.CTkLabel(frame, text=f"Current Version: {CURRENT_VERSION}", text_color="gray").pack(pady=10)
        return frame

    def change_specific_path(self, key):
        d = filedialog.askdirectory()
        if d:
            self.app_data[key] = d
            self.save_data()
            if key == "yt_download_path": self.lbl_yt_path.configure(text=d)
            elif key == "hook_download_path": self.lbl_hook_path.configure(text=d)
            elif key == "txt_source_path": self.lbl_txt_path.configure(text=d)

    def browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.mkv *.avi *.mov")]); 
        if f: self.entry_src.delete(0, "end"); self.entry_src.insert(0, f)
    
    def change_save_path(self):
        d = filedialog.askdirectory()
        if d:
            self.app_data["save_path"] = d
            self.save_data()
            self.lbl_save_path.configure(text=d)

    def import_txt_data(self):
        f = filedialog.askopenfilename(filetypes=[("Text File", "*.txt")])
        if f:
            try:
                with open(f, 'r', encoding='utf-8') as file: content = file.read()
                self.txt_data.delete("0.0", "end"); self.txt_data.insert("0.0", content)
                messagebox.showinfo("Success", "Data timestamps imported!")
            except Exception as e: messagebox.showerror("Error", str(e))

    def run_process_thread(self): 
        if not self.silent_security_check(): return
        
        threading.Thread(target=self.process_video, daemon=True).start()
    
    def get_seconds(self, time_str):
        try:
            parts = list(map(float, time_str.split(':')))
            if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2]
            elif len(parts) == 2: return parts[0]*60 + parts[1]
            return 0
        except: return 0

    def process_video(self):
        src = self.entry_src.get()
        if not src or not os.path.exists(src): messagebox.showerror("Error", "Invalid Source Video"); return
        raw_content = self.txt_data.get("1.0", "end").strip()
        lines = [l for l in raw_content.split('\n') if l.strip()]
        if not lines: messagebox.showerror("Error", "No Data Found"); return
        ratio_val = self.combo_ratio.get(); speed_val = self.combo_speed.get()
        bg_mode = self.combo_bg.get(); merge_on = self.check_merge.get(); mode_val = self.combo_mode.get()
        need_reencode = False
        if "Original" not in ratio_val or "1.0x" not in speed_val: need_reencode = True
        if "Re-Encode" in mode_val: need_reencode = True
        self.btn_process.configure(state="disabled", text="PROCESSING (0%)...", fg_color="gray"); self.progress.set(0)
        ffmpeg_cmd = get_ffmpeg_path()
        try:
            custom_path = self.app_data.get("save_path", "")
            base_dir = custom_path if (custom_path and os.path.exists(custom_path)) else os.path.dirname(src)
            proj_name = self.entry_project.get().strip()
            folder_name = sanitize_filename(proj_name) if proj_name else os.path.splitext(os.path.basename(src))[0] + "_CLIPS"
            out_dir = os.path.join(base_dir, folder_name)
            os.makedirs(out_dir, exist_ok=True)
            try: pad_start = float(self.entry_pad_start.get()) if self.entry_pad_start.get() else 0
            except: pad_start = 0
            try: pad_end = float(self.entry_pad_end.get()) if self.entry_pad_end.get() else 0
            except: pad_end = 0
            total = len(lines); success_files = []
            
            startupinfo = None
            if os.name == 'nt': 
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            speed_map = {"1.0x": 1.0, "1.25x": 1.25, "1.5x": 1.5, "0.8x": 0.8}; speed_f = speed_map.get(speed_val.split(' ')[0], 1.0)
            for i, line in enumerate(lines):
                percent = int(((i) / total) * 100); self.btn_process.configure(text=f"PROCESSING ({percent}%)...")
                parts = line.split('|')
                if len(parts) < 3: continue
                s_str, e_str, n = parts[0].strip(), parts[1].strip(), parts[2].strip()
                t_start = self.get_seconds(s_str) - pad_start; t_end = self.get_seconds(e_str) + pad_end
                t_start = max(0, t_start); duration = t_end - t_start
                if duration <= 0: continue
                n = sanitize_filename(n)
                if not n.lower().endswith('.mp4'): n += '.mp4'
                out_path = os.path.join(out_dir, n)
                self.lbl_status.configure(text=f"Processing ({i+1}/{total}): {n}")
                
                cmd = [ffmpeg_cmd, '-y', '-ss', str(t_start), '-t', str(duration), '-i', src]
                
                vf_filters = []
                if "9:16" in ratio_val:
                    if "Black" in bg_mode: vf_filters.append("scale=1080:1920:force_original_aspect_ratio=decrease[fg];color=c=black:s=1080:1920[bg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
                    elif "White" in bg_mode: vf_filters.append("scale=1080:1920:force_original_aspect_ratio=decrease[fg];color=c=white:s=1080:1920[bg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
                    else: vf_filters.append("split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20[bg];[b]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
                elif "1:1" in ratio_val:
                    if "Black" in bg_mode: vf_filters.append("scale=1080:1080:force_original_aspect_ratio=decrease[fg];color=c=black:s=1080:1080[bg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
                    elif "White" in bg_mode: vf_filters.append("scale=1080:1080:force_original_aspect_ratio=decrease[fg];color=c=white:s=1080:1080[bg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
                    else: vf_filters.append("split[a][b];[a]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,boxblur=20[bg];[b]scale=1080:1080:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
                
                if speed_f != 1.0: pts = 1.0 / speed_f; vf_filters.append(f"setpts={pts}*PTS")
                
                if need_reencode:
                    if vf_filters: ft = ",".join(vf_filters); cmd.extend(['-filter_complex', ft] if ft else [])
                    if speed_f != 1.0: cmd.extend(['-filter:a', f"atempo={speed_f}"])
                    cmd.extend(['-c:v', 'libx264', '-preset', 'ultrafast', '-g', '48', '-sc_threshold', '0', '-c:a', 'aac'])
                else: 
                    cmd.extend(['-c', 'copy', '-avoid_negative_ts', 'make_zero'])
                
                cmd.append(out_path)
                subprocess.run(cmd, capture_output=True, startupinfo=startupinfo)
                success_files.append(out_path)
                self.progress.set((i + 1) / total)
            if merge_on and success_files:
                self.lbl_status.configure(text="Merging clips..."); self.btn_process.configure(text="MERGING...")
                list_txt = os.path.join(out_dir, "merge_list.txt")
                with open(list_txt, 'w') as f:
                    for path in success_files: f.write(f"file '{path}'\n")
                merge_out = os.path.join(out_dir, "FULL_COMPILATION.mp4")
                cmd_merge = [ffmpeg_cmd, '-y', '-f', 'concat', '-safe', '0', '-i', list_txt, '-c', 'copy', merge_out]
                subprocess.run(cmd_merge, capture_output=True, startupinfo=startupinfo)
                os.remove(list_txt); success_files.append(merge_out)
            if success_files:
                entry = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "source": os.path.basename(src), "count": len(success_files), "clips": [os.path.basename(f) for f in success_files], "raw_txt": raw_content}
                self.app_data["history"].insert(0, entry)
                self.app_data["total_clips"] += len(success_files)
                self.app_data["last_run"] = entry["date"]
                self.save_data()
                self.refresh_dashboard()
                
                self.kirim_data_sheet("Auto-Cut PC", f"Berhasil memotong {len(success_files)} Klip. File: {os.path.basename(src)}")

            messagebox.showinfo("Success", f"Done! Files saved in:\n{out_dir}")
        except Exception as err: messagebox.showerror("Error", str(err))
        finally: self.btn_process.configure(state="normal", text="START PROCESSING", fg_color=COLOR_ACCENT); self.lbl_status.configure(text="Ready to process"); self.progress.set(0)

    def silent_update_check(self): 
        if 'requests' in sys.modules: threading.Thread(target=self._upd, args=(True,), daemon=True).start()
    def manual_update_check(self): threading.Thread(target=self._upd, args=(False,), daemon=True).start()
    
    def _upd(self, silent):
        try:
            check_url = f"{VERSION_URL}?t={int(time.time())}"
            print(f"[AutoUpdate] Checking: {check_url}")
            r = requests.get(check_url, timeout=10)
            if r.status_code == 200:
                remote_ver = r.text.strip()
                if remote_ver > CURRENT_VERSION:
                    if not silent:
                        if messagebox.askyesno("Update Found", f"Versi baru v{remote_ver} tersedia!\nBuka browser untuk download?"): webbrowser.open(GITHUB_EXE_URL)
                    else: 
                        try: self.nav_buttons["settings"].configure(text_color="#e74c3c", text="⚙️  Settings (Update!)")
                        except: pass
                else:
                    if not silent: messagebox.showinfo("Info", "Aplikasi sudah versi terbaru.")
            elif not silent: messagebox.showwarning("Info", "Gagal mengambil data versi server.")
        except Exception as e:
            print(f"Update error: {e}")
            if not silent: messagebox.showerror("Error", f"Gagal cek update: {str(e)}")

# ============================================================================
# BOOTSTRAPING
# ============================================================================
def check_license_and_run():
    persistent_id = get_persistent_random_id()
    if 'requests' not in sys.modules: LoginWindow(persistent_id).mainloop(); return
    try:
        r = requests.get(f"{LICENSE_URL}?t={int(time.time())}", timeout=10)
        if r.status_code == 200:
            db_text = r.text
            if persistent_id in db_text: 
                global MEMBER_ID, CURRENT_LICENSE_KEY
                CURRENT_LICENSE_KEY = persistent_id
                
                match_trial = re.match(r"^INTISARI-TRIAL(\d+)-(\d{4})$", persistent_id)

                if match_trial:
                    trial_id = match_trial.group(1) 
                    mmdd = match_trial.group(2)    
                    bulan, hari = mmdd[:2], mmdd[2:4]
                    MEMBER_ID = f"#TRIAL-{trial_id} (Exp: {hari}/{bulan})"
                else:
                    lines = db_text.splitlines()
                    for idx, line in enumerate(lines):
                        if persistent_id in line:
                            MEMBER_ID = f"#{idx + 100}"
                            break
                            
                ModernClipper().mainloop(); return
        LoginWindow(persistent_id).mainloop()
    except: LoginWindow(persistent_id).mainloop()

if __name__ == "__main__":
    remote_v = get_remote_version()
    if is_update_required(remote_v):
        app_upd = UpdateBlocker(remote_v)
        app_upd.mainloop()
    else:
        check_license_and_run()