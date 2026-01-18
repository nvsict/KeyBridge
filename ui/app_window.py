import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
from pynput import keyboard
import shlex
import webbrowser

# --- INTERNAL IMPORTS ---
from core.engine import ADBEngine
from core.config import cfg, ADB_PATH, SPECIAL_KEYS
from core.notifications import NotificationSync
from ui.components import SafeButton
from ui.settings_tab import SettingsTab
from ui.support_dialog import SupportDialog

class KeyBridgeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyBridge Studio")
        self.root.geometry("700x750") # Increased height for new wireless tab
        self.root.configure(bg="#f3f3f3")
        
        # Initialize Backend
        self.engine = ADBEngine(self.log, self.set_status)
        self.notifier = NotificationSync(ADB_PATH)
        self.capture_active = False
        self.listener = None

        # Setup Look & Feel
        self._setup_styles()
        self._build_layout()
        
        # Start Background Tasks
        self._refresh_devices()
        self.root.after(2000, self._heartbeat)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # General Styles
        style.configure(".", font=("Segoe UI", 10), background="#f3f3f3")
        style.configure("TFrame", background="#f3f3f3")
        style.configure("TLabel", background="#f3f3f3", foreground="#333")
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        
        # Custom Classes
        style.configure("Accent.TButton", background="#007acc", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#005f9e")])
        
        style.configure("Red.TButton", background="#d32f2f", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Capture.TButton", font=("Segoe UI", 12, "bold"))
        
        style.configure("Card.TLabelframe", background="#ffffff", relief="flat")
        style.configure("Card.TLabelframe.Label", background="#ffffff", font=("Segoe UI", 11, "bold"), foreground="#007acc")

    def _build_layout(self):
        # 1. HEADER
        header = tk.Frame(self.root, bg="#ffffff", height=60, padx=15, pady=10)
        header.pack(fill="x", side="top")
        
        tk.Label(header, text="KEYBRIDGE", bg="white", fg="#333", font=("Segoe UI Black", 16)).pack(side="left")
        tk.Label(header, text="ULTIMATE", bg="white", fg="#007acc", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(5,0), pady=(8,0))
        
        btn_donate = tk.Button(header, text="☕ Support Dev", bg="#FFDD00", fg="black", 
                               font=("Segoe UI", 9, "bold"), relief="flat", padx=15, pady=4,
                               command=lambda: SupportDialog(self.root))
        btn_donate.pack(side="right")

        # 2. STATUS BAR
        status_bar = tk.Frame(self.root, bg="#007acc", height=25, padx=10)
        status_bar.pack(side="bottom", fill="x")
        self.lbl_status = tk.Label(status_bar, text="Ready", bg="#007acc", fg="white", font=("Consolas", 9))
        self.lbl_status.pack(side="left")
        self.lbl_device = tk.Label(status_bar, text="No Device", bg="#007acc", fg="#e0e0e0", font=("Consolas", 9))
        self.lbl_device.pack(side="right")

        # 3. TERMINAL
        term_frame = tk.Frame(self.root, bg="#1e1e1e", height=120)
        term_frame.pack(side="bottom", fill="x")
        self.log_text = tk.Text(term_frame, height=7, bg="#1e1e1e", fg="#00ff00", 
                                font=("Consolas", 9), relief="flat", state="disabled")
        self.log_text.pack(fill="both", padx=5, pady=5)

        # 4. TABS
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._init_dashboard_tab()
        self._init_wireless_tab()
        self._init_tools_tab()
        self._init_clipboard_tab()
        SettingsTab(self.tabs)

    # --- TAB 1: DASHBOARD ---
    def _init_dashboard_tab(self):
        tab = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(tab, text="  🎮 Dashboard  ")
        
        # Connection
        f_conn = ttk.LabelFrame(tab, text="Connection Manager", style="Card.TLabelframe", padding=15)
        f_conn.pack(fill="x", pady=(0, 15))
        
        ttk.Label(f_conn, text="Select Device:", background="white").pack(side="left")
        self.device_combo = ttk.Combobox(f_conn, state="readonly", width=25)
        self.device_combo.pack(side="left", padx=10)
        
        SafeButton(f_conn, text="↻", width=3, command=self._refresh_devices).pack(side="left")
        self.btn_connect = SafeButton(f_conn, text="Connect USB", style="Accent.TButton", command=self._toggle_connect)
        self.btn_connect.pack(side="right")

        # Nav
        f_nav = ttk.LabelFrame(tab, text="Soft Keys", style="Card.TLabelframe", padding=15)
        f_nav.pack(fill="x", pady=(0, 15))
        f_nav.columnconfigure((0,1,2), weight=1)
        SafeButton(f_nav, text="🔙 BACK", command=lambda: self.engine.send_cmd("input keyevent 4")).grid(row=0, column=0, sticky="ew", padx=2)
        SafeButton(f_nav, text="🏠 HOME", command=lambda: self.engine.send_cmd("input keyevent 3")).grid(row=0, column=1, sticky="ew", padx=2)
        SafeButton(f_nav, text="▢ APPS", command=lambda: self.engine.send_cmd("input keyevent 187")).grid(row=0, column=2, sticky="ew", padx=2)

        # Capture
        f_cap = ttk.LabelFrame(tab, text="Keyboard Input", style="Card.TLabelframe", padding=20)
        f_cap.pack(fill="both", expand=True)
        self.btn_capture = SafeButton(f_cap, text="START CAPTURE (F12)", style="Capture.TButton", command=self._toggle_capture)
        self.btn_capture.pack(fill="x", pady=(10, 5), ipady=10)
        ttk.Label(f_cap, text="Press ESC to Stop | F12 to Toggle", background="white", foreground="#888").pack()

    # --- TAB 2: WIRELESS (Dual Mode) ---
    def _init_wireless_tab(self):
        tab = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(tab, text="  📡 Wireless  ")
        
        # SECTION 1: ANDROID 11+ PAIRING
        f_pair = ttk.LabelFrame(tab, text="Option A: Android 11+ (No Cable)", style="Card.TLabelframe", padding=15)
        f_pair.pack(fill="x", pady=(0, 20))
        
        ttk.Label(f_pair, text="1. Go to Wireless Debugging > 'Pair with code'", background="white", foreground="#666").pack(anchor="w")
        
        row_pair = ttk.Frame(f_pair, style="Card.TLabelframe")
        row_pair.pack(fill="x", pady=5)
        
        ttk.Label(row_pair, text="IP:Port :", background="white").pack(side="left")
        self.pair_ip = ttk.Entry(row_pair, width=20)
        self.pair_ip.pack(side="left", padx=5)
        
        ttk.Label(row_pair, text="Code:", background="white").pack(side="left")
        self.pair_code = ttk.Entry(row_pair, width=10)
        self.pair_code.pack(side="left", padx=5)
        
        SafeButton(row_pair, text="Pair Device", style="Accent.TButton", command=self._do_pairing).pack(side="left", padx=10)

        # SECTION 2: USB WIZARD
        f_wiz = ttk.LabelFrame(tab, text="Option B: USB Cable Setup (Standard)", style="Card.TLabelframe", padding=15)
        f_wiz.pack(fill="x", pady=(0, 20))
        
        SafeButton(f_wiz, text="🚀 Start USB -> Wi-Fi Wizard", command=self.engine.setup_wireless_auto).pack(fill="x")

        # SECTION 3: CONNECT
        f_conn = ttk.LabelFrame(tab, text="Final Step: Connect", style="Card.TLabelframe", padding=15)
        f_conn.pack(fill="x")
        
        ttk.Label(f_conn, text="Enter the MAIN IP:Port shown on phone:", background="white").pack(anchor="w")
        
        row_conn = ttk.Frame(f_conn, style="Card.TLabelframe")
        row_conn.pack(fill="x", pady=5)
        
        self.ip_entry = ttk.Entry(row_conn)
        self.ip_entry.pack(side="left", fill="x", expand=True)
        self.ip_entry.insert(0, "192.168.1.x:5555")
        
        SafeButton(row_conn, text="Connect", style="Accent.TButton", command=self._connect_ip).pack(side="right", padx=(5,0))

    # --- TAB 3: TOOLS ---
    def _init_tools_tab(self):
        tab = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(tab, text="  🧰 Tools  ")
        
        f1 = ttk.LabelFrame(tab, text="File Beam", style="Card.TLabelframe", padding=15)
        f1.pack(fill="x", pady=(0, 15))
        SafeButton(f1, text="📂 Push File to Downloads", command=self._beam_file).pack(fill="x")
        
        f2 = ttk.LabelFrame(tab, text="Macro Snippets", style="Card.TLabelframe", padding=15)
        f2.pack(fill="both", expand=True)
        SafeButton(f2, text="↻ Reload Macros", command=lambda: self._load_macros(self.macro_container)).pack(anchor="e")
        self.macro_container = ttk.Frame(f2, style="Card.TLabelframe")
        self.macro_container.pack(fill="both", expand=True, pady=5)
        self._load_macros(self.macro_container)

    def _load_macros(self, parent):
        for w in parent.winfo_children(): w.destroy()
        if not cfg.macros:
            ttk.Label(parent, text="No macros. Add in Settings!", background="white").pack(pady=10)
            return
        for lbl, txt in cfg.macros.items():
            SafeButton(parent, text=lbl, command=lambda t=txt: self.engine.send_text(t)).pack(fill="x", pady=2)

    # --- TAB 4: CLIPBOARD ---
    def _init_clipboard_tab(self):
        tab = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(tab, text="  📋 Clipboard  ")
        f = ttk.LabelFrame(tab, text="PC ➔ Phone", style="Card.TLabelframe", padding=15)
        f.pack(fill="both", expand=True)
        self.txt_clipboard = tk.Text(f, height=10, relief="flat", bg="#f9f9f9", font=("Segoe UI", 10))
        self.txt_clipboard.pack(fill="both", expand=True, pady=10)
        row = ttk.Frame(f, style="Card.TLabelframe")
        row.pack(fill="x")
        SafeButton(row, text="Paste from PC", command=self._get_pc_clipboard).pack(side="left", fill="x", expand=True, padx=(0,5))
        SafeButton(row, text="Type on Phone", style="Accent.TButton", command=self._send_clipboard_text).pack(side="left", fill="x", expand=True, padx=(5,0))

    # --- LOGIC METHODS ---
    def _refresh_devices(self):
        try:
            res = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            lines = res.stdout.strip().split("\n")[1:]
            devices = [l.split()[0] for l in lines if "device" in l]
            self.device_combo['values'] = devices
            if devices: self.device_combo.current(0)
            self.log(f"Scan complete. Found {len(devices)} device(s).")
        except Exception as e:
            self.log(f"Error scanning devices: {e}")

    def _toggle_connect(self):
        if self.engine.running:
            self.engine.stop()
            self.notifier.stop()
            self.set_status(False)
        else:
            dev = self.device_combo.get()
            if dev:
                if self.engine.connect(dev):
                    self.notifier.start(dev)
                    self.set_status(True, dev)
                else:
                    self.log("Connection Failed.")
            else:
                messagebox.showwarning("Select Device", "Please select a device.")

    def _do_pairing(self):
        ip_port = self.pair_ip.get().strip()
        code = self.pair_code.get().strip()
        if not ip_port or not code:
            self.log("Error: Enter both IP:Port and Code.")
            return
        if self.engine.pair_device(ip_port, code):
            messagebox.showinfo("Success", "Device Paired! \nNow enter the main IP:Port in the 'Connect' box.")
        else:
            messagebox.showerror("Failed", "Pairing failed. Check IP/Code.")

    def _connect_ip(self):
        ip = self.ip_entry.get().strip()
        if not ip: return
        if self.engine.connect_wireless_ip(ip):
            self.log("Wireless Connected!")
            self._refresh_devices()
            # Auto-select the new wireless device in combo
            self.device_combo.set(ip if ":" in ip else f"{ip}:5555")
        else:
            self.log("Wireless Connection Failed.")

    def _auto_find_ip(self):
        # Kept for compatibility if needed, but not used in UI anymore
        ip = self.engine.get_device_ip()
        if ip: self.ip_entry.insert(0, ip)

    def _toggle_capture(self):
        if not self.engine.running:
            messagebox.showerror("Not Connected", "Please connect to a device first.")
            return
        if self.capture_active: self._stop_capture()
        else: self._start_capture()

    def _start_capture(self):
        self.capture_active = True
        self.root.attributes("-topmost", True)
        self.btn_capture.configure(text="⚠ CAPTURING INPUT... (ESC)", style="Red.TButton")
        self.listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
        self.listener.start()
        self.log("Keyboard Capture: ON")

    def _stop_capture(self):
        self.capture_active = False
        self.root.attributes("-topmost", False)
        self.btn_capture.configure(text="START CAPTURE (F12)", style="Capture.TButton")
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.log("Keyboard Capture: OFF")

    def _on_key_press(self, key):
        if not self.capture_active: return
        try:
            if key in SPECIAL_KEYS: self.engine.send_cmd(f"input keyevent {SPECIAL_KEYS[key]}")
            elif hasattr(key, 'char'): self.engine.send_text(key.char)
            elif key == keyboard.Key.space: self.engine.send_text(" ")
        except: pass

    def _on_key_release(self, key):
        if key == keyboard.Key.esc: self.root.after(0, self._stop_capture)

    def _beam_file(self):
        path = filedialog.askopenfilename()
        if path: self.engine.push_file(path)

    def _get_pc_clipboard(self):
        try:
            content = self.root.clipboard_get()
            self.txt_clipboard.delete("1.0", "end")
            self.txt_clipboard.insert("end", content)
        except: pass

    def _send_clipboard_text(self):
        content = self.txt_clipboard.get("1.0", "end-1c")
        if content.strip(): self.engine.send_text(content)

    def _heartbeat(self):
        if self.engine.running and not self.engine.check_health():
            self.engine.stop()
            self.notifier.stop()
            self.set_status(False)
            self.log("Heartbeat: Connection Lost.")
        self.root.after(2000, self._heartbeat)

    def log(self, msg):
        self.root.after(0, lambda: self._write_log(msg))

    def _write_log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"> {msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def set_status(self, connected, device_name="No Device"):
        self.btn_connect.configure(text="Disconnect" if connected else "Connect USB", 
                                   style="Red.TButton" if connected else "Accent.TButton")
        self.lbl_status.configure(text="CONNECTED" if connected else "DISCONNECTED", bg="#4caf50" if connected else "#d32f2f")
        self.lbl_device.configure(text=device_name)