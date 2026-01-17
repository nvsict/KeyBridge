# 🌉 KeyBridge Ultimate

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.x-blue?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-Stable-success?style=flat-square)

KeyBridge Ultimate solves a simple but annoying problem: Typing on a phone screen is slow.

Instead of pairing a Bluetooth keyboard or buying expensive hardware, KeyBridge lets you use your existing wired PC keyboard to type directly on your Android device.

The MVP Magic: It runs quietly in the background. When you need to type a WhatsApp message or an email on your phone, you just hit F12.

Instantly, your PC keyboard strokes are redirected to your phone.

Type at full speed with zero latency.

Hit ESC (or F12 again) to instantly switch back to controlling your PC.

It feels like having a hardware switch for your keyboard, but it's pure software.

It works entirely over ADB (Android Debug Bridge), which means **no app installation is required on your phone**, and no root is needed. Just plug and play! 🚀

---

## ✨ Features

KeyBridge isn't just a keyboard; it's a complete control center for your phone.

* **🎮 Zero-Latency Typing:** Use your PC keyboard to type on your phone instantly. Great for long messages or emails.
* **📡 Wireless Wizard:** Switch from USB to Wi-Fi connection with a single click. No command-line knowledge needed.
* **📂 File Beam:** Drag & drop files (APKs, PDFs, Images) from your PC to your phone's Download folder.
* **📋 Smart Clipboard:** Seamlessly paste text from your PC clipboard to your phone.
* **🔔 Notification Sync:** See your Android notifications (WhatsApp, SMS, etc.) pop up right on your Windows desktop.
* **🇮🇳 UPI Helper:** Quickly generate QR codes for payments to share with others.

## 🚀 Installation & Usage

### Option A: The Easy Way (Recommended)
1.  Go to the **[Releases Page](../../releases)**.
2.  Download the latest `KeyBridge.exe`.
3.  Connect your Android phone via USB.
4.  Run the app! (Ensure "USB Debugging" is enabled on your phone).

### Option B: For Developers (Source Code)
If you want to tweak the code or run it via Python:

```bash
# Clone the repository
git clone [https://github.com/nvsict/KeyBridge.git](https://github.com/nvsict/KeyBridge.git)
cd KeyBridge

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
