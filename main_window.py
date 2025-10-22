# smartplate/ui/main_window.py

# ... (keep imports: tk, ttk, messagebox, Sidebar, ThemeManager) ...
import tkinter as tk
from tkinter import ttk, messagebox
from .sidebar import Sidebar
from .theme_manager import ThemeManager
# --- ✅ Import page classes individually for better error tracking ---
from .home_page import HomePage
from .profile_page import ProfilePage
from .meal_log_page import MealLogPage
from .analytics_page import AnalyticsPage
from .settings_page import SettingsPage

class MainWindow(ttk.Frame):
    # ... (keep __init__ method as is) ...
    def __init__(self, root, user):
        super().__init__(root, style='TFrame')
        self.root = root; self.user = user
        try: self.root.state('zoomed')
        except tk.TclError: print("Note: Could not automatically maximize window.")
        self.root.minsize(1000, 650); self.root.title("SmartPlate")
        self.pack(fill="both", expand=True); print("[MainWindow] Initialized.")
        self.sidebar = Sidebar(self, self.on_nav); self.sidebar.pack(side="left", fill="y", padx=(10,0), pady=10)
        self.container = ttk.Frame(self, style='TFrame'); self.container.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.pages = {}; self.page_classes = {}; self.map_page_classes() # Call the updated function
        if not self.page_classes: print("FATAL: Page mapping failed, cannot show initial page.")
        else: self.show("Home")

    # --- ⬇️ Replace this function ⬇️ ---
    def map_page_classes(self):
        """Imports and maps page classes with detailed error checking."""
        print("[MainWindow] Mapping page classes...")
        self.page_classes = {} # Start with an empty dict
        all_pages_mapped = True
        
        # List of page classes to attempt loading
        page_imports = {
            "Home": HomePage,
            "Profile": ProfilePage,
            "Meal Log": MealLogPage,
            "Analytics": AnalyticsPage,
            "Settings": SettingsPage
        }

        for page_name, PageClass in page_imports.items():
            try:
                # Check if the class has the required PAGE_NAME attribute
                if hasattr(PageClass, 'PAGE_NAME') and PageClass.PAGE_NAME == page_name:
                    self.page_classes[page_name] = PageClass
                    print(f"  Successfully mapped: {page_name}")
                else:
                    print(f"  ERROR: Class for '{page_name}' is missing or has incorrect PAGE_NAME attribute.")
                    all_pages_mapped = False
            except Exception as e:
                # Catch any other unexpected errors during access/check
                print(f"  CRITICAL ERROR mapping page '{page_name}': {e}")
                all_pages_mapped = False
                # Optionally show a popup immediately
                # messagebox.showerror("Page Load Error", f"Critical error loading page class '{page_name}':\n{e}")

        if all_pages_mapped:
            print("[MainWindow] All Page classes mapped successfully.")
        else:
            print("[MainWindow] WARNING: One or more page classes failed to map correctly.")
            # Show a single error message at the end if any failed
            messagebox.showerror("Page Load Error", "One or more application pages failed to load correctly. Check console for details.")
    # --- ⬆️ Replace this function ⬆️ ---


    # ... (keep on_nav, show, on_theme_change methods as is) ...
    def on_nav(self, name):
        print(f"[MainWindow] Navigating to: {name}")
        page = self.show(name);
        if self.sidebar: self.sidebar.highlight(name)
        if page and name == "Analytics" and hasattr(page, 'draw_chart'): page.draw_chart()
        if page and name == "Meal Log" and hasattr(page, 'load_data'): page.load_data()
        if page and name == "Profile" and hasattr(page, 'load_data'): page.load_data()
    def show(self, name):
        for widget in self.container.winfo_children(): widget.pack_forget()
        page_to_show = None
        if name in self.pages: page_to_show = self.pages[name]
        elif name in self.page_classes:
            PageClass = self.page_classes[name]; page_args = {'master': self.container}
            if name == "Settings": page_args['on_theme_change'] = self.on_theme_change
            elif name in ("Profile", "Meal Log", "Analytics"): page_args['user'] = self.user
            try: page = PageClass(**page_args); self.pages[name] = page; page_to_show = page; print(f"  Created instance of {name}")
            except Exception as e: print(f"  ERROR creating {name}: {e}"); messagebox.showerror("Page Load Error", f"Failed to load page '{name}':\n{e}"); return None
        else: # This is where the error message comes from
             print(f"  ERROR: Page name '{name}' not found in mapped classes.")
             ttk.Label(self.container, text=f"Error: Page '{name}' could not be loaded.\nCheck console for mapping errors.", foreground="red").pack(expand=True)
             return None
        if page_to_show: page_to_show.pack(fill="both", expand=True); self.container.update_idletasks(); print(f"  Page '{name}' packed.")
        return page_to_show
    def on_theme_change(self):
        print("[MainWindow] Theme change triggered. Rebuilding UI...")
        current_user = self.user; current_page_name = "Home"
        if hasattr(self, 'sidebar') and self.sidebar: current_page_name = self.sidebar.selected_name
        for widget in self.root.winfo_children(): widget.destroy()
        ThemeManager.apply_theme_to_style()
        new_main_window = MainWindow(self.root, current_user)
        new_main_window.show(current_page_name)
        if hasattr(new_main_window, 'sidebar') and new_main_window.sidebar: new_main_window.sidebar.highlight(current_page_name)