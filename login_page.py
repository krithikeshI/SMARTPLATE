# smartplate/ui/login_page.py
import tkinter as tk
from tkinter import messagebox, ttk
from .theme_manager import ThemeManager
# Import db functions and oracledb ONLY inside attempt_db_connection
from .main_window import MainWindow 
from .widgets import ThemedLabel, ThemedEntry, AccentButton, ThemedButton

class LoginPage(tk.Toplevel): 
    def __init__(self, root):
        super().__init__(root)
        self.root = root # Store reference to the main hidden root window
        
        self.title("SmartPlate — Login")
        self.geometry("420x400")
        
        # --- Build BASIC UI structure FIRST ---
        self.container = ttk.Frame(self, style='TFrame'); self.container.pack(expand=True, padx=30, pady=20)
        self.status_label = tk.Label(self.container, text="Initializing..."); self.status_label.pack(pady=(10, 0))
        print("LoginPage minimal structure built.") 
        
        # --- Setup window properties ---
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.transient(root) 
        self.grab_set()      
        
        # Center the login window
        self.update_idletasks() 
        print("Centering login window...") 
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
        print("Login window centered.") 

        # --- Force window visibility BEFORE applying theme ---
        print("Attempting to force window visibility...")
        self.deiconify() 
        self.lift()      
        self.focus_force() 
        self.update_idletasks() 
        print("Window visibility forced.")

        # --- NOW Apply Theme and Build Themed Widgets ---
        try:
            print("Applying theme style...")
            ThemeManager.setup_style(self) # Apply style to this Toplevel
            self.configure(bg=ThemeManager.bg()) # Set background color now
            self.status_label.configure( # Configure status label for theme
                text="Building UI...", 
                bg=ThemeManager.bg(), 
                fg=ThemeManager.muted(),
                font=('Segoe UI', 10) # Ensure font matches theme
            ) 
            self.update_idletasks() 
            print("Theme style applied. Building themed widgets...")
            self.build_themed_widgets() 
            print("Themed widgets built.")
        except Exception as e:
            print(f"ERROR applying theme or building widgets: {e}")
            messagebox.showerror("Theme Error", f"Failed to apply theme or build UI:\n{e}", parent=self)
            self.root.destroy()
            return 

        # Bind the Enter key after entries are created
        if hasattr(self, 'email_entry') and hasattr(self, 'pwd_entry'):
             self.email_entry.bind("<Return>", lambda event: self.pwd_entry.focus())
             self.pwd_entry.bind("<Return>", lambda event: self.login()) 
        else:
             print("Warning: Email/Password entries not found for key binding.")

        print("LoginPage __init__ finished.")

    def build_themed_widgets(self):
        """Builds the themed widgets within the container."""
        for widget in self.container.winfo_children():
            if widget != self.status_label: widget.destroy()

        ThemedLabel(self.container, text="SmartPlate", font=("Segoe UI", 24, "bold"), foreground=ThemeManager.accent()).pack(pady=(0, 15)) 
        ThemedLabel(self.container, text="Email").pack(anchor="w", pady=(5, 2))
        self.email_entry = ThemedEntry(self.container); self.email_entry.pack(fill="x") 
        ThemedLabel(self.container, text="Password").pack(anchor="w", pady=(5, 2))
        self.pwd_entry = ThemedEntry(self.container, show="*"); self.pwd_entry.pack(fill="x", pady=(0, 20)) 
        self.login_button = AccentButton(self.container, text="Login", command=self.login, state="disabled"); self.login_button.pack(fill="x", ipady=5) 
        self.signup_button = ThemedButton(self.container, text="Sign up", command=self.signup, state="disabled"); self.signup_button.pack(fill="x", pady=5)
        self.guest_button = ThemedButton(self.container, text="Continue as Guest", command=self.guest, state="disabled"); self.guest_button.pack(fill="x")
        self.status_label.pack_forget() 
        self.status_label.pack(side=tk.BOTTOM, pady=(10, 0))
        self.status_label.config(text="Connecting to database...", foreground=ThemeManager.muted())


    def attempt_db_connection(self):
        """ ✅ Tries to initialize the driver and connect to the DB (FINAL, CORRECTED) """
        try:
            # --- ✅ Import the correct functions from db.py ---
            from ..db import init_oracle_driver, init_db_schema
            
            # --- ✅ Call the driver initializer first ---
            print("Attempting to initialize Oracle client..."); 
            if not init_oracle_driver():
                # If driver fails, init_oracle_driver() prints details
                raise Exception("Failed to initialize Oracle client driver. Check console log for details.") 
            print("Oracle client initialized.")

            # --- ✅ Call the schema initializer ---
            print("Attempting to initialize database tables..."); 
            init_db_schema() # This function connects and creates tables
            print("Database tables initialized.")
            
            # --- Update UI ---
            self.status_label.config(text="Connection successful!", foreground=ThemeManager.accent())
            self.login_button.config(state="normal"); self.signup_button.config(state="normal"); self.guest_button.config(state="normal")
            
            print("Forcing UI update after DB connect...")
            self.update_idletasks() 
            print("UI update forced after DB connect.")
            
            self.status_label.after(2000, lambda: self.status_label.pack_forget())
            
        except Exception as e:
            print(f"CRITICAL: Database connection failed: {e}")
            self.status_label.config(text="Connection failed.", foreground="red")
            self.update_idletasks() 
            messagebox.showerror("Database Error", f"Could not connect to database:\n{e}", parent=self)
            if hasattr(self, 'root') and self.root:
                 self.root.destroy() 
            else:
                 self.destroy()

    def login(self):
        from ..db import authenticate 
        email = self.email_entry.get().strip(); password = self.pwd_entry.get().strip()
        if not email or not password: messagebox.showwarning("Input Required", "Please enter both email and password.", parent=self); return
        user = authenticate(email, password)
        if user: self.open_main_app(user)
        else: messagebox.showerror("Login Failed", "Invalid email or password.", parent=self)

    def signup(self):
        from ..db import create_user 
        em = self.email_entry.get().strip(); pw = self.pwd_entry.get().strip()
        if not em or not pw: messagebox.showwarning("Sign up", "Please enter both email and password.", parent=self); return
        try:
            if create_user(em, pw): messagebox.showinfo("Sign up", "Account created successfully! Logging you in...", parent=self); self.login() 
            else: messagebox.showerror("Sign up Failed", "An account with that email already exists.", parent=self)
        except Exception as e: messagebox.showerror("Database Error", f"An error occurred during sign up: {e}", parent=self)

    def guest(self):
        guest_user = {"id": 0, "email": "guest@smartplate.com", "name": "Guest"}
        self.open_main_app(guest_user)

    def open_main_app(self, user_data):
        print("Opening main application window...") 
        self.destroy() 
        self.root.deiconify() 
        main_app = MainWindow(self.root, user_data) 
        print("Main application window should be open.") 

    def _on_close(self):
        print("Login window closed by user.") 
        self.root.destroy()