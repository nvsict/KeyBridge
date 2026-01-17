import tkinter as tk
from tkinter import ttk
import qrcode
from PIL import Image, ImageTk
import webbrowser

# --- CONFIGURATION ---
BMC_LINK = "https://buymeacoffee.com/mohittarkar"
UPI_VPA = "PINKEE2@PTYES"
UPI_NAME = "KeyBridge_Dev"

# --- COLORS ---
BG_COLOR = "#f4f6f8"
CARD_COLOR = "#ffffff"
ACCENT_UPI = "#2962ff" # Royal Blue for UPI
ACCENT_BMC = "#ffdd00" # BMC Yellow
TEXT_PRIMARY = "#1e293b"
TEXT_SECONDARY = "#64748b"

class SupportDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Support Development")
        self.geometry("440x620")
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)
        
        # Modal setup
        self.transient(parent)
        self.grab_set()
        
        # State
        self.amount_btns = {} # To track button widgets
        self.upi_qr_image = None
        self.bmc_qr_image = None
        
        self._build_ui()
        
    def _build_ui(self):
        # 1. HEADER (Gradient-like look)
        header = tk.Frame(self, bg=CARD_COLOR, pady=20, padx=20)
        header.pack(fill="x")
        
        tk.Label(header, text="🚀 Boost Development", font=("Segoe UI", 16, "bold"), bg=CARD_COLOR, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(header, text="Your support fuels new features & updates.", font=("Segoe UI", 10), bg=CARD_COLOR, fg=TEXT_SECONDARY).pack(anchor="w", pady=(2,0))

        # 2. TABS CONTAINER
        # We use a custom frame to give tabs some padding
        tab_container = tk.Frame(self, bg=BG_COLOR, padx=15, pady=15)
        tab_container.pack(fill="both", expand=True)
        
        # Custom Notebook Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=[12, 8], background="#e2e8f0")
        style.map("TNotebook.Tab", background=[("selected", CARD_COLOR)], foreground=[("selected", ACCENT_UPI)])
        
        tabs = ttk.Notebook(tab_container)
        tabs.pack(fill="both", expand=True)
        
        self._init_upi_tab(tabs)
        self._init_bmc_tab(tabs)

        # 3. FOOTER
        footer = tk.Frame(self, bg=BG_COLOR, pady=10)
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text="Made with ❤️ by Mohit", font=("Segoe UI", 9, "italic"), bg=BG_COLOR, fg="#94a3b8").pack()

    # --- TAB 1: UPI (Super UX) ---
    def _init_upi_tab(self, parent):
        tab = tk.Frame(parent, bg=CARD_COLOR)
        parent.add(tab, text="  🇮🇳 UPI (India)  ")
        
        # A. Smart Amount Chips
        lbl = tk.Label(tab, text="Select Amount to Auto-Fill:", font=("Segoe UI", 9, "bold"), bg=CARD_COLOR, fg=TEXT_SECONDARY)
        lbl.pack(pady=(20, 10))
        
        chip_frame = tk.Frame(tab, bg=CARD_COLOR)
        chip_frame.pack()
        
        # Create interactive buttons
        self._create_chip(chip_frame, "Any", None, is_default=True)
        self._create_chip(chip_frame, "₹50", "50")
        self._create_chip(chip_frame, "₹100", "100")
        self._create_chip(chip_frame, "₹500", "500")

        # B. QR Card Area
        qr_outer = tk.Frame(tab, bg="white", highlightbackground="#e2e8f0", highlightthickness=1, padx=2, pady=2)
        qr_outer.pack(pady=20)
        
        self.lbl_upi_qr = tk.Label(qr_outer, bg="white")
        self.lbl_upi_qr.pack(padx=10, pady=10)
        
        # Initial Render
        self._update_upi_qr(None)

        # C. Payment Hints
        apps_frame = tk.Frame(tab, bg=CARD_COLOR)
        apps_frame.pack()
        tk.Label(apps_frame, text="Scan using:", bg=CARD_COLOR, fg=TEXT_SECONDARY, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(apps_frame, text=" GPay • PhonePe • Paytm", bg=CARD_COLOR, fg=TEXT_PRIMARY, font=("Segoe UI", 9, "bold")).pack(side="left")

        # D. VPA Box (Copyable)
        vpa_box = tk.Frame(tab, bg="#f8fafc", padx=10, pady=10, highlightbackground="#cbd5e1", highlightthickness=1)
        vpa_box.pack(fill="x", padx=30, pady=20)
        
        # VPA Text
        tk.Label(vpa_box, text=UPI_VPA, font=("Consolas", 11, "bold"), bg="#f8fafc", fg="#334155").pack(side="left")
        
        # Verified Badge
        tk.Label(vpa_box, text="VERIFIED", font=("Segoe UI", 7, "bold"), bg="#dcfce7", fg="#15803d", padx=4).pack(side="left", padx=5)

        # Copy Button
        self.btn_copy = tk.Button(vpa_box, text="Copy ID", bg="white", relief="groove", font=("Segoe UI", 8),
                                  command=self._copy_vpa, cursor="hand2")
        self.btn_copy.pack(side="right")

    # --- TAB 2: INTERNATIONAL ---
    def _init_bmc_tab(self, parent):
        tab = tk.Frame(parent, bg=CARD_COLOR)
        parent.add(tab, text="  ☕ International  ")
        
        # Hero Section
        tk.Label(tab, text="Buy Me a Coffee", font=("Segoe UI", 14, "bold"), bg=CARD_COLOR, fg=TEXT_PRIMARY).pack(pady=(30, 5))
        tk.Label(tab, text="Accepts Credit Cards & PayPal", font=("Segoe UI", 10), bg=CARD_COLOR, fg=TEXT_SECONDARY).pack()
        
        # QR Code
        qr_img = self._generate_qr(BMC_LINK, color="#444")
        self.bmc_qr_image = qr_img
        
        qr_frame = tk.Frame(tab, bg="white", highlightbackground="#e2e8f0", highlightthickness=1)
        qr_frame.pack(pady=20)
        tk.Label(qr_frame, image=qr_img, bg="white").pack(padx=10, pady=10)
        
        # Big Yellow Action Button
        btn = tk.Button(tab, text="Open Payment Page ➜", bg=ACCENT_BMC, fg="black", 
                        font=("Segoe UI", 11, "bold"), relief="flat", padx=30, pady=10, cursor="hand2",
                        activebackground="#fdd835",
                        command=lambda: webbrowser.open(BMC_LINK))
        btn.pack(pady=10)

    # --- INTERACTIVE LOGIC ---
    def _create_chip(self, parent, text, amount_val, is_default=False):
        # A 'Chip' is a button that toggles appearance
        btn = tk.Button(parent, text=text, font=("Segoe UI", 9), relief="flat", 
                        padx=10, pady=4, cursor="hand2")
        
        # Store metadata on the widget itself
        btn.amount_val = amount_val
        
        # Bind click
        btn.config(command=lambda: self._on_chip_click(btn))
        
        btn.pack(side="left", padx=4)
        self.amount_btns[text] = btn
        
        # Set initial style
        if is_default:
            self._set_active_chip(btn)
        else:
            self._set_inactive_chip(btn)

    def _on_chip_click(self, btn):
        # Reset all
        for b in self.amount_btns.values():
            self._set_inactive_chip(b)
        # Set active
        self._set_active_chip(btn)
        # Update QR
        self._update_upi_qr(btn.amount_val)

    def _set_active_chip(self, btn):
        btn.config(bg=ACCENT_UPI, fg="white", font=("Segoe UI", 9, "bold"))

    def _set_inactive_chip(self, btn):
        btn.config(bg="#e2e8f0", fg=TEXT_PRIMARY, font=("Segoe UI", 9))

    def _update_upi_qr(self, amount):
        uri = f"upi://pay?pa={UPI_VPA}&pn={UPI_NAME}&cu=INR"
        if amount:
            uri += f"&am={amount}" # Add amount param
            
        img = self._generate_qr(uri, color="black")
        self.upi_qr_image = img
        self.lbl_upi_qr.config(image=img)

    def _generate_qr(self, data, color="black"):
        qr = qrcode.QRCode(box_size=7, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=color, back_color="white")
        return ImageTk.PhotoImage(img)

    def _copy_vpa(self):
        self.clipboard_clear()
        self.clipboard_append(UPI_VPA)
        
        orig_text = self.btn_copy.cget("text")
        self.btn_copy.config(text="✓ Copied", bg="#dcfce7", fg="#15803d")
        self.after(2000, lambda: self.btn_copy.config(text=orig_text, bg="white", fg="#333"))