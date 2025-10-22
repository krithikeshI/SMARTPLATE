# smartplate/ui/widgets.py
import tkinter as tk
from tkinter import ttk
from .theme_manager import ThemeManager

# --- Basic Themed Widgets ---

class ThemedLabel(ttk.Label):
    def __init__(self, master=None, **kwargs):
        style = kwargs.pop('style', 'TLabel')
        super().__init__(master, style=style, **kwargs)

class ThemedEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        style = kwargs.pop('style', 'TEntry')
        super().__init__(master, style=style, **kwargs)
        # Add border highlighting on focus
        self.bind("<FocusIn>", lambda e: self.configure(style='Focus.TEntry'))
        self.bind("<FocusOut>", lambda e: self.configure(style='TEntry'))
        # Create the focused style if it doesn't exist
        s = ttk.Style()
        s.configure('Focus.TEntry', bordercolor=ThemeManager.accent(), fieldbackground=ThemeManager.palette()['panel'])


class ThemedButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        style = kwargs.pop('style', 'TButton')
        super().__init__(master, style=style, **kwargs)

class AccentButton(ThemedButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, style='Accent.TButton', **kwargs)

# --- ✅ ADDED: Helper Widget for Meal Log Page ---

class InfoLabel(ttk.Frame):
     """A simple frame containing a bold label and a normal value label."""
     def __init__(self, master, label_text, value_text, **kwargs):
         # Make sure the frame itself uses the theme's background
         super().__init__(master, style='TFrame', **kwargs) 
         # Use ThemedLabel for consistency
         ThemedLabel(self, text=label_text, font=('Segoe UI', 10, 'bold')).pack(side="left")
         ThemedLabel(self, text=value_text, font=('Segoe UI', 10)).pack(side="left", padx=(5,0))