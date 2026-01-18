# 🌉 KeyBridge Pro (v1.2)
**The Ultimate PC-to-Android Keyboard Bridge**

KeyBridge allows you to type on your Android device using your PC keyboard. It works over **USB** or **Wi-Fi**, features a **Zero-Lag Input Engine**, and includes a **Global Hotkey** with a Heads-Up Display (HUD) so you can type without looking away.

![Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🚀 New in v1.2 (The Ultimate Update)
* **⚡ Zero-Lag Typing:** New "Smart Batching" engine groups keystrokes for instant text input.
* **🪄 Wireless Wizard:** One-click tool to switch from USB to Wi-Fi mode automatically.
* **🔓 Android 11+ Pairing:** Support for "Pair with Code" – connect wirelessly without ever touching a USB cable.
* **🕶️ Global Hotkey & HUD:** Press **`Ctrl + F12`** anywhere to toggle typing mode. A floating red HUD keeps you informed.
* **📋 Clipboard Beam:** Support for multi-line text, poems, and code snippets.
* **🎨 UX Polish:** New Splash Screen, High-DPI scaling, and System Tray integration.

---

## ✨ Features
* **Type Anywhere:** Works in WhatsApp, Chrome, Notes, Terminal, etc.
* **Soft Keys:** Control Home, Back, and App Switcher from your PC.
* **File Beam:** Push files directly to your phone's Download folder.
* **System Tray:** Minimizes to tray to keep your taskbar clean.
* **Auto-Recovery:** Detects connection drops and stabilizes the link automatically.

---

## 🎮 How to Use

### 1. Wired Mode (USB)
1. Enable **USB Debugging** on your phone.
2. Plug it into your PC.
3. Open **KeyBridge**.
4. Click **Connect USB**.
5. Press **`Ctrl + F12`** to start typing!

### 2. Wireless Mode (The Magic Way)
1. Plug in via USB **once**.
2. Go to the **Wireless Tab**.
3. Click **"🚀 Start USB -> Wi-Fi Wizard"**.
4. Wait for the success message, then unplug the cable.
5. You are now wireless!

### 3. Android 11+ Mode (No Cable Needed)
1. **On Phone:** Go to **Developer Options** > **Wireless Debugging** > **Pair with Code**.
2. **In KeyBridge:** Go to **Wireless Tab** > **Option A**.
3. Enter the **IP**, **Port**, and **Pairing Code** shown on your phone.
4. Click **Pair Device**, then connect using the main IP.

---

## ⌨️ Shortcuts & Controls

| Key / Action | Function |
| :--- | :--- |
| **`Ctrl + F12`** | **Master Toggle** (Start/Stop Typing Mode) |
| **`ESC`** | **Emergency Stop** (Exit Typing Mode) |
| **`Home` / `End`** | Moves cursor on phone |
| **`F12`** | Alternative Toggle |
| **Tray Icon** | Left-click to **Open** / Right-click to **Quit** |

---

## 🛠️ Troubleshooting

* **"Typing is lagging":**
  The v1.2 engine fixes this. Ensure you are not running two instances of the app.

* **"Enter creates new line instead of sending":**
  This is an app setting. In WhatsApp/Telegram, go to Settings and enable **"Enter is Send"**.

* **"Connection Failed":**
  Make sure your PC and Phone are on the **same Wi-Fi network**.

---

## ❤️ Contributing

Issues and Pull Requests are welcome!

1. **Fork** the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a **Pull Request**

---

**Made with 🐍 Python & ADB**

## 📥 Installation

### Option A: Download (Recommended)
1.  Go to the [**Releases Page**](https://github.com/nvsict06/KeyBridge/releases).
2.  Download the latest `KeyBridge.exe`.
3.  Run it! (No installation required).

### Option B: Run from Source
If you are a developer, you can run the raw Python code:
```bash
# 1. Clone the repo
git clone [https://github.com/nvsict/KeyBridge.git](https://github.com/nvsict/KeyBridge.git)
cd KeyBridge

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py



