import tkinter as tk
from pystray import Icon as TrayIcon, MenuItem as Item
from PIL import Image, ImageDraw
from ui.app_window import KeyBridgeWindow
import threading

def create_icon_image():
    # Generate a simple 64x64 icon (Green Box)
    image = Image.new('RGB', (64, 64), color = (73, 109, 137))
    d = ImageDraw.Draw(image)
    d.rectangle([16,16,48,48], fill=(0,255,0))
    return image

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.window = KeyBridgeWindow(self.root)
        
        # Tray Setup
        self.tray_icon = None
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_attempt)

    def _on_close_attempt(self):
        # Minimize to Tray instead of closing
        self.root.withdraw() # Hide Window
        self._start_tray()

    def _start_tray(self):
        if not self.tray_icon:
            image = create_icon_image()
            menu = (Item('Show', self._show_window), Item('Quit', self._quit_app))
            self.tray_icon = TrayIcon("KeyBridge", image, "KeyBridge Pro", menu)
            # Run tray in separate thread
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_window(self, icon, item):
        self.root.after(0, self.root.deiconify) # Show Window

    def _quit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def run(self):
        # Global Hotkey for F12
        self.root.bind('<F12>', lambda e: self.window._toggle_capture())
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()