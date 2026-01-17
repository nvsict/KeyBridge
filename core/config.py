import json
import os
from pynput import keyboard
from .utils import resource_path



# Check if we have a bundled adb.exe, otherwise fall back to system 'adb'
BUNDLED_ADB = resource_path(os.path.join("assets", "adb.exe"))

if os.path.exists(BUNDLED_ADB):
    ADB_PATH = BUNDLED_ADB
else:
    ADB_PATH = "adb"

# Key Mappings (PC -> Android Keycodes)
SPECIAL_KEYS = {
    keyboard.Key.enter: 66,      # KEYCODE_ENTER
    keyboard.Key.backspace: 67,  # KEYCODE_DEL
    keyboard.Key.tab: 61,        # KEYCODE_TAB
    keyboard.Key.esc: 111,       # KEYCODE_ESCAPE
    keyboard.Key.up: 19,         # KEYCODE_DPAD_UP
    keyboard.Key.down: 20,       # KEYCODE_DPAD_DOWN
    keyboard.Key.left: 21,       # KEYCODE_DPAD_LEFT
    keyboard.Key.right: 22,      # KEYCODE_DPAD_RIGHT
    keyboard.Key.page_up: 92,    # KEYCODE_PAGE_UP
    keyboard.Key.page_down: 93,  # KEYCODE_PAGE_DOWN
    keyboard.Key.home: 122,      # KEYCODE_MOVE_HOME
    keyboard.Key.end: 123,       # KEYCODE_MOVE_END
    keyboard.Key.delete: 112,    # KEYCODE_FORWARD_DEL
    
    # Function Keys
    keyboard.Key.f10: 24,        # Vol UP
    keyboard.Key.f9: 25,         # Vol DOWN
    keyboard.Key.f8: 85,         # Play/Pause
    keyboard.Key.f7: 26          # Power
}

APP_SHORTCUTS = {
    "Chrome": "com.android.chrome",
    "YouTube": "com.google.android.youtube",
    "WhatsApp": "com.whatsapp",
    "Settings": "com.android.settings",
}

# --- CONFIG MANAGER (Settings) ---
CONFIG_FILE = "user_config.json"

DEFAULT_MACROS = {
    "My Email": "user@example.com",
    "Address": "123 Tech Street",
}

class ConfigManager:
    def __init__(self):
        self.macros = DEFAULT_MACROS.copy()
        self.apps = APP_SHORTCUTS.copy()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.macros = data.get("macros", self.macros)
                    # We can add app persistence here later if needed
            except: pass 

    def save(self):
        data = {"macros": self.macros}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def add_macro(self, name, text):
        self.macros[name] = text
        self.save()

    def remove_macro(self, name):
        if name in self.macros:
            del self.macros[name]
            self.save()

# Create the global instance
cfg = ConfigManager()