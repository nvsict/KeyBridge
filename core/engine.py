import subprocess
import threading
import queue
import shlex
import os
import re
import time
from .config import ADB_PATH

class ADBEngine:
    def __init__(self, log_callback, status_callback):
        self.process = None
        self.queue = queue.Queue()
        self.running = False
        self.log = log_callback
        self.update_status = status_callback
        self.NO_WINDOW = subprocess.CREATE_NO_WINDOW

    # --- CONNECTION MANAGEMENT ---
    def connect(self, device_id):
        self.stop()
        device_id = device_id.strip()

        # Handle IP-only input (add port if missing)
        # e.g. "192.168.1.5" -> "192.168.1.5:5555"
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", device_id):
             device_id = f"{device_id}:5555"
             self._run_adb_silent(["connect", device_id])

        cmd = [ADB_PATH, '-s', device_id, 'shell']
        
        try:
            # 1. Start the shell process
            self.process = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,  # Capture errors to debug crashes
                text=True, 
                bufsize=0, # Unbuffered for speed
                creationflags=self.NO_WINDOW
            )
            
            # 2. IMMEDIATE HEALTH CHECK
            # Wait 0.5s to see if it crashes immediately (common with bad wireless links)
            try:
                self.process.wait(timeout=0.5)
                # If we are here, the process exited (Crashed)
                stderr = self.process.stderr.read()
                self.log(f"[!] Connection died immediately: {stderr.strip()}")
                self.update_status(False)
                return False
            except subprocess.TimeoutExpired:
                # Process is still running! This is good.
                pass

            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()
            self.log(f"[+] Connected to {device_id}")
            self.update_status(True)
            return True
        except Exception as e:
            self.log(f"[!] Engine Error: {e}")
            self.update_status(False)
            return False

    # --- WIRELESS FEATURES ---
    def pair_device(self, ip_port, code):
        """ 
        Runs 'adb pair ip:port code'. 
        Used for Android 11+ connection without USB.
        """
        self.log(f"[*] Pairing with {ip_port}...")
        try:
            res = subprocess.run(
                [ADB_PATH, "pair", ip_port, code],
                capture_output=True, 
                text=True, 
                creationflags=self.NO_WINDOW
            )
            output = res.stdout.strip() + res.stderr.strip()
            self.log(f"Pair Result: {output}")
            return "successfully paired" in output.lower()
        except Exception as e:
            self.log(f"[!] Pairing error: {e}")
            return False

    def setup_wireless_auto(self):
        """ 
        The Smart Wizard: 
        1. Find IP -> 2. Switch to TCP Mode -> 3. Wait -> 4. Connect -> 5. Verify 
        """
        def _sequence():
            self.log("Step 1/4: Finding IP address...")
            ip = self.get_device_ip()
            
            if not ip:
                self.log("[!] IP not found. Connect phone to Wi-Fi.")
                return
            
            # Warn if it looks like a USB tethering IP (often 192.0.0.x)
            if ip.startswith("192.0.0"):
                self.log(f"[⚠] Warning: {ip} looks like a USB Tethering IP.")
                self.log("    Wireless mode might fail if you unplug USB.")

            self.log(f"Step 2/4: Found IP {ip}. Enabling TCP Mode...")
            self._run_adb_silent(["tcpip", "5555"])
            
            self.log("Step 3/4: Restarting ADB (Waiting 5s)...")
            time.sleep(5) 
            
            target = f"{ip}:5555"
            self.log(f"Step 4/4: Connecting to {target}...")
            
            # Connect
            res = self._run_adb_capture(["connect", target])
            self.log(f"ADB Output: {res}")

            if "connected" in res.lower():
                # STABILIZATION CHECK
                self.log(">>> Unplug USB now. Verifying link stability... <<<")
                
                # Retry loop to verify connection
                success = False
                for i in range(5):
                    time.sleep(1)
                    # Try to run a simple command
                    check = self._run_adb_capture(["-s", target, "shell", "echo", "ok"])
                    if "ok" in check:
                        success = True
                        break
                    else:
                        self.log(f"Stabilizing... ({i+1}/5)")

                if success:
                    self.log(f"SUCCESS: Link Stable. Starting Engine...")
                    self.connect(target)
                else:
                    self.log("[!] Link unstable. Phone might be offline.")
            else:
                self.log(f"[!] Connection failed. Try manual mode.")

        threading.Thread(target=_sequence, daemon=True).start()

    def connect_wireless_ip(self, ip):
        """ Manually connect to a specific IP """
        ip = ip.strip()
        target = ip if ":" in ip else f"{ip}:5555"
            
        self.log(f"[*] Connecting to {target}...")
        try:
            res = self._run_adb_capture(["connect", target])
            output = res.strip()
            self.log(output)
            return "connected" in output.lower()
        except Exception as e:
            self.log(f"[!] Connection failed: {e}")
            return False

    def get_device_ip(self):
        """ Tries multiple ways to get the WLAN IP """
        try:
            # Method 1: ip route (Standard)
            res = self._run_adb_capture(["shell", "ip route"])
            # Prefer wlan0 IPs
            match = re.search(r'src (\d+\.\d+\.\d+\.\d+).*wlan0', res)
            if match: return match.group(1)
            
            # Fallback: Any src IP that isn't localhost
            match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', res)
            if match and "127.0.0.1" not in match.group(1): return match.group(1)
        except: pass

        return None

    # --- TEXT & FILE HANDLING ---
    def send_text(self, text):
        """ 
        Handles multi-line text by splitting into lines, 
        sanitizing characters, and pressing Enter between lines.
        OPTIMIZED: Does not log every keystroke to save CPU.
        """
        if not self.running or not text: return

        # 1. Split text into separate lines (preserving structure)
        lines = text.split('\n')

        for i, line in enumerate(lines):
            # A. Sanitize specific line
            # Escape backslashes first!
            safe_line = str(line).replace("\\", "\\\\")
            # Escape quotes
            safe_line = safe_line.replace('"', '\\"').replace("'", "\\'")
            # Escape shell metacharacters
            for char in '()<>|;&*~`$#[]!':
                safe_line = safe_line.replace(char, f"\\{char}")
            # Replace spaces with %s (ADB magic)
            safe_line = safe_line.replace(" ", "%s")

            # B. Send the text content
            if safe_line:
                self.queue.put(f"input text {safe_line}")
            
            # C. If there are more lines coming, press ENTER to move down
            if i < len(lines) - 1:
                self.queue.put("input keyevent 66") # 66 = ENTER

    def push_file(self, local_path):
        filename = os.path.basename(local_path)
        remote_path = f"/sdcard/Download/{filename}"
        self.log(f"[*] Sending {filename}...")
        
        def _push_thread():
            self._run_adb_silent(["push", local_path, remote_path])
            self.log(f"[+] Sent: {filename}")
            
        threading.Thread(target=_push_thread, daemon=True).start()

    # --- CORE UTILS ---
    def _run_adb_silent(self, args):
        try:
            subprocess.run([ADB_PATH] + args, creationflags=self.NO_WINDOW)
        except: pass

    def _run_adb_capture(self, args):
        try:
            res = subprocess.run(
                [ADB_PATH] + args, 
                capture_output=True, 
                text=True, 
                creationflags=self.NO_WINDOW
            )
            return res.stdout.strip()
        except: return ""

    # --- CORE WORKER ---
    def _worker(self):
        while self.running:
            cmd = self.queue.get()
            if cmd is None: break
            try:
                if self.process and self.process.poll() is None:
                    self.process.stdin.write(cmd + "\n")
                    self.process.stdin.flush()
                else:
                    self.running = False
                    self.update_status(False)
            except: pass

    def send_cmd(self, adb_cmd):
        if self.running: self.queue.put(adb_cmd)

    def stop(self):
        self.running = False
        self.update_status(False)
        if self.process:
            self.process.terminate()
            self.process = None

    def check_health(self):
        return self.process is not None and self.process.poll() is None