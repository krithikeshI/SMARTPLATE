# smartplate/ui/theme_manager.py
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk

SETTINGS = Path.home() / ".smartplate_settings.json"

class ThemeManager:
    PALETTES = {
        "Dark Mint": {"bg": "#0F1720", "panel": "#1E293B", "text": "#E2E8F0", "accent": "#34D399", "muted": "#64748B"},
        "Dark Blue": {"bg": "#0B1120", "panel": "#1C274C", "text": "#E0E7FF", "accent": "#60A5FA", "muted": "#5A6788"},
        "Light Teal": {"bg": "#F0FDFA", "panel": "#FFFFFF", "text": "#0F172A", "accent": "#14B8A6", "muted": "#9CA3AF"},
        "Light Coral": {"bg": "#FFF5F5", "panel": "#FFFFFF", "text": "#1F2937", "accent": "#EF4444", "muted": "#A1A1AA"}
    }
    DEFAULT = "Dark Mint"
    _theme = DEFAULT
    _spoonacular_api_key = ""
    # --- ✅ Store Groq Key ---
    _groq_api_key = ""
    # --- End Change ---
    style = None

    @classmethod
    def setup_style(cls, root):
        """Initializes or reconfigures the ttk style."""
        if cls.style is None:
            if root is None:
                temp_root = tk.Tk(); temp_root.withdraw(); cls.style = ttk.Style(temp_root)
            else:
                cls.style = ttk.Style(root)
        cls.apply_theme_to_style()

    @classmethod
    def apply_theme_to_style(cls):
        """Applies the current theme colors to ttk widget styles."""
        if cls.style is None:
            print("ERROR: ThemeManager.style not initialized.")
            return

        p = cls.palette()
        print(f"Applying theme: {cls.theme_name()} with palette: {p}")

        # --- ✅ Base Theme: Corrected Try/Except Indentation ---
        try:
            cls.style.theme_use('clam')
            print("Using 'clam' base theme.")
        except tk.TclError:
            print("Warning: 'clam' theme not available, trying others...")
            try:
                cls.style.theme_use('vista')
                print("Using 'vista' base theme.")
            except tk.TclError:
                try:
                    cls.style.theme_use('xpnative')
                    print("Using 'xpnative' base theme.")
                except tk.TclError:
                    print("Error: Could not set any custom base theme (clam, vista, xpnative).")
                    try:
                         cls.style.theme_use('default') # Last resort
                         print("Using 'default' base theme.")
                    except tk.TclError:
                         print("FATAL: No ttk themes seem to be available.")
        # --- End Correction ---


        # --- Calculate Contrasting Foreground for Accent ---
        try:
             hex_color = p['accent'].lstrip('#')
             rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
             luminance = (rgb[0]*299 + rgb[1]*587 + rgb[2]*114) / 1000
             accent_fg = p['text'] # Use main text color
             print(f"Calculated accent foreground: {accent_fg}")
        except Exception as e:
             print(f"Warn: Contrast calc failed: {e}. Falling back.")
             accent_fg = p['bg'] # Fallback contrast

        # --- Configure Global Styles ---
        cls.style.configure('.', background=p['bg'], foreground=p['text'],
                            fieldbackground=p['panel'], insertcolor=p['text'],
                            font=('Segoe UI', 10))

        # --- Specific Widget Styles (Keep as before) ---
        cls.style.configure('TFrame', background=p['bg'])
        cls.style.configure('TLabel', background=p['bg'], foreground=p['text'])
        cls.style.configure('TButton', background=p['panel'], foreground=p['text'], font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=(10, 5), relief='flat')
        cls.style.map('TButton', background=[('active', p['muted']), ('disabled', p['panel'])], foreground=[('disabled', p['muted']), ('active', p['text']), ('!disabled', p['text'])])
        cls.style.configure('Accent.TButton', background=p['accent'], foreground=accent_fg, font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=(10, 5), relief='flat')
        cls.style.map('Accent.TButton', background=[('active', p['text']), ('disabled', p['panel']), ('!disabled', p['accent'])], foreground=[('active', p['accent']), ('disabled', p['muted']), ('!disabled', accent_fg)])
        cls.style.configure('TEntry', fieldbackground=p['panel'], foreground=p['text'], bordercolor=p['muted'], insertcolor=p['text'], borderwidth=1)
        cls.style.map('TEntry', bordercolor=[('focus', p['accent'])])
        cls.style.configure('TCombobox', fieldbackground=p['panel'], background=p['panel'], foreground=p['text'], bordercolor=p['muted'], arrowcolor=p['text'])
        cls.style.map('TCombobox', fieldbackground=[('readonly', p['panel'])], bordercolor=[('focus', p['accent'])])
        cls.style.configure('Treeview', background=p['panel'], fieldbackground=p['panel'], foreground=p['text'], rowheight=25)
        cls.style.map('Treeview', background=[('selected', p['accent'])], foreground=[('selected', accent_fg)])
        cls.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background=p['bg'], foreground=p['text'], padding=8, relief='flat', borderwidth=0)
        cls.style.map('Treeview.Heading', background=[('active', p['muted'])])
        try: cls.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        except tk.TclError: print("Warn: Treeview layout failed.")

    @classmethod
    def load_settings(cls):
        """Loads theme and API keys from the settings file."""
        print(f"Loading settings from {SETTINGS}...")
        cls._theme = cls.DEFAULT
        cls._spoonacular_api_key = ""
        cls._groq_api_key = "" # Reset defaults
        try:
            if SETTINGS.exists():
                with open(SETTINGS, 'r') as f:
                    d = json.load(f)
                cls._theme = d.get("theme", cls.DEFAULT)
                cls._spoonacular_api_key = d.get("spoonacular_api_key", "")
                cls._groq_api_key = d.get("groq_api_key", "") # Load Groq key
                print(f"  Loaded theme: {cls._theme}, Spoonacular: '{cls._spoonacular_api_key[:4]}...', Groq: '{cls._groq_api_key[:4]}...'")
            else:
                print("  Settings file not found.")
        except (json.JSONDecodeError, IOError, Exception) as e:
             print(f"  Error loading settings: {e}. Using defaults.")
             cls._theme = cls.DEFAULT # Ensure defaults on error
             cls._spoonacular_api_key = ""
             cls._groq_api_key = ""

    @classmethod
    def save_settings(cls):
        """Saves current theme and API keys to the settings file."""
        print(f"Saving settings to {SETTINGS}...")
        try:
            settings_data = {
                "theme": cls._theme,
                "spoonacular_api_key": cls._spoonacular_api_key,
                "groq_api_key": cls._groq_api_key # Save Groq key
            }
            with open(SETTINGS, 'w') as f:
                json.dump(settings_data, f, indent=4)
            print(f"  Saved theme: {cls._theme}, Spoonacular: '{cls._spoonacular_api_key[:4]}...', Groq: '{cls._groq_api_key[:4]}...'")
        except (IOError, Exception) as e:
            print(f"  Error saving settings: {e}")

    # --- Theme Management ---
    @classmethod
    def set_theme(cls, name):
        """Sets the current theme and saves it."""
        if name in cls.PALETTES:
            cls._theme = name
            cls.save_settings()

    # --- API Key Management ---
    @classmethod
    def save_spoonacular_api_key(cls, api_key):
        cls._spoonacular_api_key = api_key; cls.save_settings()
    @classmethod
    def get_spoonacular_api_key(cls):
        return cls._spoonacular_api_key

    @classmethod
    def save_groq_api_key(cls, api_key):
        print(f"Updating Groq API Key: '{api_key[:4]}...'")
        cls._groq_api_key = api_key; cls.save_settings()
    @classmethod
    def get_groq_api_key(cls):
        print(f"Client getting Groq API Key: '{cls._groq_api_key[:4]}...'")
        return cls._groq_api_key

    # --- Color Palette Helpers ---
    @classmethod
    def theme_name(cls): return cls._theme
    @classmethod
    def palette(cls): return cls.PALETTES.get(cls._theme, cls.PALETTES[cls.DEFAULT])
    @classmethod
    def bg(cls): return cls.palette()["bg"]
    @classmethod
    def accent(cls): return cls.palette()["accent"]
    @classmethod
    def text(cls): return cls.palette()["text"]
    @classmethod
    def muted(cls): return cls.palette()["muted"]