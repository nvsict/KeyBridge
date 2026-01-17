import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from core.config import cfg
from .components import SafeButton

class SettingsTab:
    def __init__(self, parent_notebook):
        self.tab = ttk.Frame(parent_notebook)
        parent_notebook.add(self.tab, text="⚙ Settings")
        
        self._init_macro_editor()
        
    def _init_macro_editor(self):
        lbl_frame = ttk.LabelFrame(self.tab, text="Macro Manager", padding=10)
        lbl_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox
        self.lst_macros = tk.Listbox(lbl_frame, height=10)
        self.lst_macros.pack(fill="both", expand=True, pady=5)
        self._refresh_list()
        
        # Buttons
        btn_frame = ttk.Frame(lbl_frame)
        btn_frame.pack(fill="x")
        
        SafeButton(btn_frame, text="+ Add New", command=self._add_macro).pack(side="left", padx=5)
        SafeButton(btn_frame, text="- Delete Selected", command=self._del_macro).pack(side="left", padx=5)

    def _refresh_list(self):
        self.lst_macros.delete(0, "end")
        for name, text in cfg.macros.items():
            self.lst_macros.insert("end", f"{name} : {text}")

    def _add_macro(self):
        name = simpledialog.askstring("New Macro", "Button Label (e.g. 'My Email'):")
        if not name: return
        text = simpledialog.askstring("New Macro", "Text to Type:")
        if not text: return
        
        cfg.add_macro(name, text)
        self._refresh_list()

    def _del_macro(self):
        sel = self.lst_macros.curselection()
        if not sel: return
        
        item = self.lst_macros.get(sel[0])
        name = item.split(" : ")[0]
        
        cfg.remove_macro(name)
        self._refresh_list()