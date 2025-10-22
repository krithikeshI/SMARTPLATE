# smartplate/ui/settings_page.py
from tkinter import ttk, messagebox
from .base_page import BasePage
from .widgets import ThemedLabel, ThemedEntry, AccentButton, ThemedButton
from .theme_manager import ThemeManager

class SettingsPage(BasePage):
    PAGE_NAME = "Settings"
    def __init__(self, master, on_theme_change=None):
        self.on_theme_change_callback = on_theme_change; super().__init__(master)

    def build(self):
        main_container=ttk.Frame(self, style="TFrame"); main_container.pack(pady=30, padx=50, fill="x", expand=True, anchor="n")
        content_frame=ttk.Frame(main_container, style="TFrame", width=600); content_frame.pack(anchor="n"); content_frame.columnconfigure(0, weight=1)
        ThemedLabel(content_frame, text="Settings", font=("Segoe UI", 20, "bold"), foreground=self.theme.accent()).grid(row=0, column=0, pady=(0, 25), sticky="w")

        # Theme (Keep)
        ThemedLabel(content_frame, text="Theme Palettes:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", pady=(10, 5))
        theme_btn_frame = ttk.Frame(content_frame, style='TFrame'); theme_btn_frame.grid(row=2, column=0, sticky="ew", pady=(0, 30)); theme_btn_frame.columnconfigure(0, weight=1)
        for i, name in enumerate(self.theme.PALETTES.keys()):
            ThemedButton(theme_btn_frame, text=name, command=lambda n=name: self.set_theme(n)).grid(row=i, column=0, sticky="ew", pady=5, ipady=5)

        # Spoonacular (Keep)
        ThemedLabel(content_frame, text="Spoonacular API Key (Nutrition):", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, sticky="w", pady=(10, 5))
        sp_key_frame = ttk.Frame(content_frame, style='TFrame'); sp_key_frame.grid(row=4, column=0, sticky="ew"); sp_key_frame.columnconfigure(1, weight=1)
        ThemedLabel(sp_key_frame, text="API Key:").grid(row=0, column=0, sticky="w", padx=(0,10))
        self.spoonacular_key_entry = ThemedEntry(sp_key_frame); self.spoonacular_key_entry.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        self.spoonacular_key_entry.insert(0, self.theme.get_spoonacular_api_key())
        AccentButton(content_frame, text="Save Spoonacular Key", command=self.save_spoonacular_key).grid(row=5, column=0, sticky="w", pady=(0, 20), ipadx=10, ipady=5)

        # --- ✅ Groq API Key ---
        ThemedLabel(content_frame, text="Groq API Key (AI Chat):", font=("Segoe UI", 11, "bold")).grid(row=6, column=0, sticky="w", pady=(10, 5))
        groq_token_frame = ttk.Frame(content_frame, style='TFrame'); groq_token_frame.grid(row=7, column=0, sticky="ew"); groq_token_frame.columnconfigure(1, weight=1)
        ThemedLabel(groq_token_frame, text="API Key:").grid(row=0, column=0, sticky="w", padx=(0,10))
        self.groq_token_entry = ThemedEntry(groq_token_frame, show="*"); # Hide token
        self.groq_token_entry.grid(row=0, column=1, sticky="ew", pady=(0, 10))
        self.groq_token_entry.insert(0, self.theme.get_groq_api_key()) # Use new getter
        AccentButton(content_frame, text="Save Groq API Key", command=self.save_groq_api_key).grid(row=8, column=0, sticky="w", pady=(0, 20), ipadx=10, ipady=5) # Use new save command
        # --- End Change ---

    def set_theme(self, name):
        self.theme.set_theme(name);
        if self.on_theme_change_callback: self.on_theme_change_callback()

    def save_spoonacular_key(self):
        api_key = self.spoonacular_key_entry.get().strip();
        if not api_key: messagebox.showwarning("Missing Info", "Enter Spoonacular API Key.", parent=self); return
        self.theme.save_spoonacular_api_key(api_key);
        messagebox.showinfo("Success", "Spoonacular API Key saved.", parent=self)

    # --- ✅ Save Groq Token Function ---
    def save_groq_api_key(self):
        token = self.groq_token_entry.get().strip();
        if not token: messagebox.showwarning("Missing Info", "Enter Groq API Key.", parent=self); return
        self.theme.save_groq_api_key(token); # Use new save method
        messagebox.showinfo("Success", "Groq API Key saved.", parent=self)
    # --- End Change ---