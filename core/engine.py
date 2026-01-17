import subprocess
import threading
import queue
import shlex
import os
import re
from .config import ADB_PATH

class ADBEngine:
    def __init__(self, log_callback, status_callback):
        self.process = None
        self.queue = queue.Queue()
        self.running = False
        self.log = log_callback
        self.update_status = status_callback
        
        # [CRITICAL] This flag tells Windows: "Run silently, do not open a black cmd window"
        # We store it here to re-use it easily.
        self.NO_WINDOW = subprocess.CREATE_NO_WINDOW

    # --- CONNECTION MANAGEMENT ---
    def connect(self, device_id):
        """Starts the persistent shell connection to the specific device."""
        self.stop()
        cmd = [ADB_PATH, '-s', device_id, 'shell']
        
        try:
            # Open persistent shell
            self.process = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL, 
                text=True, 
                bufsize=0,
                creationflags=self.NO_WINDOW  # <--- FIX APPLIED
            )
            self.running = True
            
            # Start the background worker
            threading.Thread(target=self._worker, daemon=True).start()
            
            self.log(f"[+] Connected to {device_id}")
            self.update_status(True)
            return True
        except Exception as e:
            self.log(f"[!] Engine Error: {e}")
            self.update_status(False)
            return False

    def enable_wireless(self):
        """Restarts ADB in TCP mode on port 5555."""
        self.log("[*] Switching to TCP mode...")
        try:
            subprocess.run(
                [ADB_PATH, "tcpip", "5555"], 
                creationflags=self.NO_WINDOW
            )
            self.log("[+] ADB restarted on Port 5555. You can unplug USB soon.")
        except Exception as e:
            self.log(f"[!] Failed to switch mode: {e}")

    def connect_wireless_ip(self, ip):
        """Connects to a specific IP."""
        self.log(f"[*] Connecting to {ip}:5555...")
        try:
            res = subprocess.run(
                [ADB_PATH, "connect", f"{ip}:5555"], 
                capture_output=True, 
                text=True,
                creationflags=self.NO_WINDOW
            )
            output = res.stdout.strip()
            self.log(output)
            return "connected" in output
        except Exception as e:
            self.log(f"[!] Connection failed: {e}")
            return False

    def get_device_ip(self):
        """Attempts to find the device's WLAN IP address via shell."""
        try:
            # Run 'ip route' inside shell to find local IP
            cmd = [ADB_PATH, "shell", "ip route"]
            res = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                creationflags=self.NO_WINDOW
            )
            # Parse output looking for src IP (usually on wlan0)
            # Example output: "192.168.1.5 dev wlan0 ..."
            match = re.search(r'src (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', res.stdout)
            if match:
                return match.group(1)
            return None
        except:
            return None

    # --- TOOLS & UTILITIES ---
    def push_file(self, local_path):
        """Pushes a file to Android Download folder."""
        filename = os.path.basename(local_path)
        remote_path = f"/sdcard/Download/{filename}"
        self.log(f"[*] Sending {filename}...")
        
        def _push_thread():
            try:
                subprocess.run(
                    [ADB_PATH, "push", local_path, remote_path],
                    creationflags=self.NO_WINDOW
                )
                self.log(f"[+] File sent to: Downloads/{filename}")
            except Exception as e:
                self.log(f"[!] Push failed: {e}")
            
        threading.Thread(target=_push_thread, daemon=True).start()

    # --- INPUT HANDLING ---
    def _worker(self):
        """Background thread to feed commands to the persistent shell."""
        while self.running:
            cmd = self.queue.get()
            if cmd is None: break
            try:
                if self.process and self.process.poll() is None:
                    self.process.stdin.write(cmd + "\n")
                    self.process.stdin.flush()
                else:
                    # Process died unexpectedly
                    self.running = False
                    self.update_status(False)
            except: pass

    def send_cmd(self, adb_cmd):
        """Queues a raw shell command (e.g., 'input keyevent 66')."""
        if self.running: self.queue.put(adb_cmd)

    def send_text(self, text):
        """Sanitizes and sends text input."""
        if not self.running: return
        # Python's shlex.quote makes strings safe for shell (handles ' " & | etc)
        safe_text = shlex.quote(text)
        self.queue.put(f"input text {safe_text}")

    def launch_app(self, package_name):
        """Launches an app using the monkey hack (faster than 'am start')."""
        if self.running:
            self.log(f"[*] Launching {package_name}...")
            self.queue.put(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

    def stop(self):
        """Stops the engine and kills the shell process."""
        self.running = False
        self.update_status(False)
        if self.process:
            self.process.terminate()
            self.process = None
            
    def check_health(self):
        """Returns True if the ADB process is still alive."""
        return self.process is not None and self.process.poll() is None