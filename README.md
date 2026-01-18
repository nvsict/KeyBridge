# 🚀 KeyBridge Ultimate

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.x-blue?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

**KeyBridge Ultimate** solves a simple but incredibly annoying problem: **Typing on a phone screen is slow.**

Instead of pairing a Bluetooth keyboard or buying expensive hardware switches, KeyBridge lets you use your **existing wired PC keyboard** to type directly on your Android device.

---

## ✨ The MVP Magic: The Toggle That Changes Everything

KeyBridge runs silently in the background of your PC. 

When you need to reply to a WhatsApp message, write an email, or enter a long password on your phone, just press **`F12`**.

* **🔁 Instantly**, your PC keyboard input is redirected to your Android phone.
* Type at **full speed**, with **zero noticeable latency**.
* Press **`ESC`** (or `F12` again) to instantly switch back to controlling your PC.

It feels like having a physical hardware switch for your keyboard — but it’s **100% software**.

---

## 🔑 Key Features

### ⌨️ The "Magic Toggle" (F12)
Seamlessly switch your keyboard input between your PC and your Phone in milliseconds. No pairing mode, no waiting.

### ⚡ Zero Latency
Uses raw ADB hardware events, not Bluetooth. Typing feels as responsive as plugging your keyboard directly into the phone's USB port.

### 🚫 No App Required
Works entirely through ADB (Android Debug Bridge). **You do not need to install any app on your Android device.**

### 📡 Wireless Mode
Start with USB, then switch to Wi-Fi mode. Keep typing wirelessly even after unplugging the cable.

### 📂 File Beam
Drag & drop files (APKs, images, documents) from your PC straight into your phone’s `Download` folder.

### 📋 Clipboard Sync
Copy text on Windows, paste it instantly on Android.

### 🔔 Notification Mirror (Bonus)
View your phone’s incoming notifications directly on your PC screen while you work, so you never miss a beat.

---

## ❓ Why KeyBridge?

**The Problem: Context Switching**
You are deep in work on your PC, and a long message arrives on your phone. Picking it up, unlocking it, and thumb-typing a reply breaks your flow completely.

**The Solution: Stay in the Zone**
With KeyBridge Ultimate, your hands never leave the keyboard.
1. Press **`F12`**
2. Type your reply
3. Press **`F12`** again
4. Keep working.

No distractions. No interruptions. Just flow.

---

## 🛠 Technical Highlights

* **Core:** Python 3.10+
* **Input Handling:** `pynput` for capturing global hotkeys and redirecting raw key events.
* **Backend:** Pure ADB Shell implementation (Subprocess management).
* **Packaging:** Standalone `.exe` — **No Python installation required for end users.**

---

## ☕ Support the Development

KeyBridge is free and open-source. If this tool saved you time or improved your workflow, consider buying me a coffee!

<div align="center">

<a href="https://buymeacoffee.com/mohittarkar">
  <img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=mohittarkar&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" />
</a>

<br><br>

**Or via UPI (India):** `PINKEE2@PTYES`

</div>

---

<p align="center">
  Made with ❤️ by <b>Mohit Tarkar</b>
</p>
