# smartplate/ui/sidebar.py
import tkinter as tk
from tkinter import ttk
from .theme_manager import ThemeManager
from .widgets import ThemedButton, ThemedLabel 

class Sidebar(ttk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master, style='TFrame', width=220)
        self.on_select = on_select; self.buttons = {}; self.selected_name = "Home"
        self.pack_propagate(False); self.build()
        
    def build(self):
        """Builds the sidebar widgets."""
        # Clear any old widgets first (important for theme refresh)
        for widget in self.winfo_children():
            widget.destroy()
            
        ThemedLabel(self, text="SmartPlate", font=("Segoe UI", 18, "bold"), foreground=ThemeManager.accent()).pack(pady=20)
        
        self.buttons = {} # Reset buttons dictionary
        for name in ["Home", "Profile", "Meal Log", "Analytics", "Settings"]:
            button = ThemedButton(self, text=name, command=lambda n=name: self.on_select(n))
            button.pack(fill="x", padx=15, pady=6, ipady=4); 
            self.buttons[name] = button
            
        # Apply initial highlight based on selected_name
        self.highlight(self.selected_name) 

    def highlight(self, name):
        """Highlights the selected button and resets others."""
        print(f"Sidebar highlighting: {name}")
        # Reset all buttons to default style first
        for btn_name, button in self.buttons.items():
            try:
                if button.winfo_exists():
                    button.configure(style='TButton')
            except tk.TclError:
                 print(f"Warning: TclError configuring button {btn_name} (likely during theme change)")
                 pass # Ignore if button was destroyed during theme change

        # Highlight the new button
        button_to_highlight = self.buttons.get(name)
        if button_to_highlight:
             try:
                 if button_to_highlight.winfo_exists():
                     button_to_highlight.configure(style='Accent.TButton')
                     print(f"  Applied Accent style to {name}")
             except tk.TclError:
                 print(f"Warning: TclError applying accent style to {name}")
                 pass # Ignore if button destroyed during theme change
        else:
             print(f"Warning: Button '{name}' not found in sidebar buttons dictionary.")
             
        self.selected_name = name