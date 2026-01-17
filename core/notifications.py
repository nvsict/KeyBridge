import threading
import subprocess
import time
import re
from plyer import notification

class NotificationSync:
    def __init__(self, adb_path):
        self.adb_path = adb_path
        self.running = False
        self.seen_keys = set() # Track seen notifications to avoid duplicates
        self.device_id = None
        
        # [CRITICAL] Flag to hide black console window
        self.NO_WINDOW = subprocess.CREATE_NO_WINDOW

    def start(self, device_id):
        self.device_id = device_id
        self.running = True
        threading.Thread(target=self._poll_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _poll_loop(self):
        """
        Polls 'dumpsys notification' every 5s. 
        Note: This is the most compatible way to get text without a custom app.
        """
        while self.running:
            try:
                # Get list of visible notifications
                cmd = [self.adb_path, '-s', self.device_id, 'shell', 'dumpsys', 'notification', '--noredact']
                
                # [FIX] Added creationflags to prevent black window flashing
                res = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8', 
                    errors='ignore',
                    creationflags=self.NO_WINDOW
                )
                
                self._parse_and_notify(res.stdout)
                
            except Exception as e:
                # Silently ignore errors to keep thread alive
                pass
            
            time.sleep(5) # Poll interval

    def _parse_and_notify(self, dump_output):
        # Regex to find Notification Records
        # Looks for: "pkg=com.whatsapp" ... "tickerText=Message from Mom"
        current_pkg = "Unknown"
        
        for line in dump_output.split('\n'):
            line = line.strip()
            
            if "pkg=" in line:
                # Extract package name
                match = re.search(r'pkg=([a-zA-Z0-9.]+)', line)
                if match: current_pkg = match.group(1)
            
            if "tickerText=" in line and "tickerText=null" not in line:
                try:
                    text = line.split("tickerText=")[1]
                    key = f"{current_pkg}:{text}"
                    
                    if key not in self.seen_keys:
                        self.seen_keys.add(key)
                        self._show_toast(current_pkg, text)
                        
                        # Cleanup cache if too big to save memory
                        if len(self.seen_keys) > 50: self.seen_keys.clear()
                except:
                    pass

    def _show_toast(self, title, message):
        try:
            notification.notify(
                title=f"📱 {title}",
                message=message,
                app_name="KeyBridge",
                timeout=5
            )
        except:
            pass