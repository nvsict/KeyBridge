import tkinter as tk
from tkinter import ttk, messagebox
from pystray import Icon as TrayIcon, MenuItem as Item
from PIL import Image, ImageDraw, ImageTk
from ui.app_window import KeyBridgeWindow
import threading
import sys
import os
import ctypes
import socket
import time
import traceback

# --- CONFIGURATION ---
APP_NAME = "KeyBridge Pro"
SINGLE_INSTANCE_PORT = 64209
VERSION = "v1.2"

# --- SYSTEM HELPERS ---
def set_dpi_awareness():
    """ Makes text sharp on 4K/High-DPI screens. """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass

def check_single_instance():
    """ Returns socket lock if unique, else None. """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', SINGLE_INSTANCE_PORT))
        return s
    except socket.error:
        return None

def create_icon_image():
    """ Generates the Green Box Icon. """
    image = Image.new('RGB', (64, 64), color=(30, 30, 30))
    d = ImageDraw.Draw(image)
    d.rectangle([0, 0, 63, 63], outline="#007acc", width=3) # Blue Border
    d.rectangle([16, 16, 48, 48], fill="#007acc") # Center Box
    return image

def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')

# --- MODERN SPLASH SCREEN ---
class SplashScreen(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.overrideredirect(True) # No Window Frame
        self.config(bg="#1e1e1e")
        self.attributes("-topmost", True)
        
        # Layout
        w, h = 320, 180
        center_window(self, w, h)
        
        # 1. App Title
        tk.Label(self, text="KEYBRIDGE", font=("Segoe UI Black", 22), fg="white", bg="#1e1e1e").pack(pady=(35, 0))
        tk.Label(self, text=f"ULTIMATE {VERSION}", font=("Segoe UI", 9, "bold"), fg="#007acc", bg="#1e1e1e").pack(pady=(0, 20))
        
        # 2. Status Text
        self.lbl_status = tk.Label(self, text="Initializing...", font=("Consolas", 9), fg="#888", bg="#1e1e1e")
        self.lbl_status.pack(side="bottom", pady=10)

        # 3. Progress Bar (Green)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("green.Horizontal.TProgressbar", background="#007acc", troughcolor="#333", bordercolor="#1e1e1e")
        
        self.progress = ttk.Progressbar(self, style="green.Horizontal.TProgressbar", orient="horizontal", length=280, mode="determinate")
        self.progress.pack(side="bottom", pady=(0, 5))

    def update_status(self, text, percent):
        self.lbl_status.config(text=text)
        self.progress['value'] = percent
        self.update()
        time.sleep(0.3) # Fake delay to make it feel "techy"

# --- MAIN APPLICATION ---
class MainApp:
    def __init__(self):
        # 1. Global Crash Handler
        sys.excepthook = self.handle_crash

        # 2. Instance Check
        self.instance_lock = check_single_instance()
        if not self.instance_lock:
            messagebox.showinfo(APP_NAME, "KeyBridge is already running.\nCheck your system tray area.")
            sys.exit(0)

        set_dpi_awareness()
        self.root = tk.Tk()
        self.root.withdraw() # Hide main window immediately

        # Icon Setup
        self.icon_img = create_icon_image()
        self.tk_icon = ImageTk.PhotoImage(self.icon_img)
        self.root.iconphoto(True, self.tk_icon)

        # 3. Show Splash Sequence
        splash = SplashScreen(self.root)
        
        splash.update_status("Loading Core Engine...", 20)
        # (Importing heavy libraries happens here usually)
        
        splash.update_status("Checking ADB Connection...", 50)
        # (We could check adb here, but UI handles it gracefully)
        
        splash.update_status("Initializing UI...", 80)
        self.window = KeyBridgeWindow(self.root) # Heavy lifting
        
        splash.update_status("Ready!", 100)
        splash.destroy()

        # 4. Launch Main Window
        self.root.deiconify()
        center_window(self.root, 700, 750)
        
        # 5. Setup Tray
        self.tray_icon = None
        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

    def _minimize_to_tray(self):
        self.root.withdraw()
        if not self.tray_icon:
            self._start_tray()
        else:
            # If tray icon thread died, restart it
            pass 

    def _start_tray(self):
        menu = (Item('Open KeyBridge', self._show_window, default=True), Item('Quit', self._quit_app))
        self.tray_icon = TrayIcon(APP_NAME, self.icon_img, f"{APP_NAME} (Running)", menu)
        # This enables Left-Click to open!
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def _quit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.after(0, self._force_exit)

    def _force_exit(self):
        if hasattr(self.window, 'engine'):
            self.window.engine.stop()
        if self.instance_lock:
            self.instance_lock.close()
        self.root.destroy()
        sys.exit(0)

    def handle_crash(self, exc_type, exc_value, exc_traceback):
        """ Catches unexpected errors and shows a popup instead of silent death """
        err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        messagebox.showerror("KeyBridge Crashed", f"An unexpected error occurred:\n\n{exc_value}\n\n(See log for details)")
        # In a real app, you might save 'err_msg' to a file here
        sys.exit(1)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()