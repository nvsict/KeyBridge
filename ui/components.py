import tkinter as tk
from tkinter import ttk

class SafeButton(ttk.Button):
    """A Button that immediately releases focus after being clicked.
    Prevents the 'Spacebar Loop' issue."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Bind the click event to reset focus
        self.bind("<ButtonRelease-1>", self._reset_focus)

    def _reset_focus(self, event):
        # Move focus to the root window (background)
        self.winfo_toplevel().focus_set()