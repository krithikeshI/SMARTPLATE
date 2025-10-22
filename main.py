# smartplate/main.py
import tkinter as tk
from .ui.theme_manager import ThemeManager 
from .ui.login_page import LoginPage
import sys

# Global variable to hold the login window reference
login_window_ref = None 

def create_login_window(root):
    """Creates the LoginPage Toplevel window."""
    global login_window_ref
    if login_window_ref is None or not login_window_ref.winfo_exists():
        print("Creating LoginPage...")
        login_window_ref = LoginPage(root)
        # We still need to delay the DB connection attempt
        root.after(100, login_window_ref.attempt_db_connection) 
        print("LoginPage created.")
    else:
        print("LoginPage already exists.")
        login_window_ref.lift() # Bring to front if already created

def start_application():
    """Initializes and runs the main application."""
    print("Starting SmartPlate (No Withdraw Test)...")
    
    root = tk.Tk()
    # Make the root window small and maybe off-screen initially
    root.geometry("1x1+0+0") 
    
    ThemeManager.load_settings()
    # Apply theme styles to the root window - still needed for Toplevel
    ThemeManager.setup_style(root) 
    
    # --- DO NOT WITHDRAW THE ROOT WINDOW ---
    print("Root window created (will not be withdrawn).")
    
    # Schedule the creation of the login window after mainloop starts
    root.after(50, lambda: create_login_window(root))
    
    print("Starting Tkinter main loop...") 
    root.mainloop()
    print("Tkinter main loop finished.") 
    
    print("SmartPlate has closed.")