# smartplate/ui/home_page.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .base_page import BasePage
from .widgets import ThemedLabel, AccentButton
# --- ✅ Import Groq Client ---
from ..groq_client import GroqClient
# --- End Change ---
import threading

class HomePage(BasePage):
    PAGE_NAME = "Home"

    def __init__(self, master, **kwargs):
        # --- ✅ Initialize Groq Client ---
        self.ai_client = GroqClient()
        # --- End Change ---
        super().__init__(master, **kwargs)

    def build(self):
        # Welcome
        ThemedLabel(self, text="Welcome to SmartPlate!", font=("Segoe UI", 24, "bold"), foreground=self.theme.accent()).pack(pady=(30, 10))
        ThemedLabel(self, text="Your intelligent meal planning and tracking assistant.", font=("Segoe UI", 14)).pack(pady=5)

        # AI Section
        ai_frame = ttk.Frame(self, style="TFrame", padding=20); ai_frame.pack(fill="both", expand=True, padx=50, pady=20); ai_frame.columnconfigure(0, weight=1)

        # --- ✅ Update Labels ---
        ThemedLabel(ai_frame, text="Ask Groq (Llama 3) about Health or Nutrition:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 5))

        # Input
        self.ai_input = tk.Text(ai_frame, height=4, width=80, relief="flat", bg=self.theme.palette()['panel'], fg=self.theme.text(), insertbackground=self.theme.text(), font=("Segoe UI", 10), bd=1, wrap="word")
        self.ai_input.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.ai_input.bind("<FocusIn>", lambda e: self.ai_input.config(bd=1, highlightbackground=self.theme.accent(), highlightcolor=self.theme.accent(), highlightthickness=2))
        self.ai_input.bind("<FocusOut>", lambda e: self.ai_input.config(bd=1, highlightbackground=self.theme.muted(), highlightthickness=1))

        # Button
        self.ask_button = AccentButton(ai_frame, text="Ask AI", command=self.ask_ai_thread)
        self.ask_button.grid(row=2, column=0, sticky="w", pady=5)

        # Output
        ThemedLabel(ai_frame, text="AI Response:", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 5))
        # --- End Update ---
        self.ai_output = scrolledtext.ScrolledText(ai_frame, height=10, width=80, relief="flat", bg=self.theme.palette()['panel'], fg=self.theme.text(), font=("Segoe UI", 10), bd=1, wrap="word", state="disabled")
        self.ai_output.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        ai_frame.rowconfigure(4, weight=1)

        # Status
        self.ai_status = ThemedLabel(ai_frame, text="", font=("Segoe UI", 9), foreground=self.theme.muted())
        self.ai_status.grid(row=5, column=0, columnspan=2, sticky="w")

    # --- (Methods are identical, no changes needed) ---
    def ask_ai_thread(self):
        prompt = self.ai_input.get("1.0", tk.END).strip()
        if not prompt: messagebox.showwarning("Input Needed", "Please enter your question.", parent=self); return
        self.ask_button.config(state="disabled"); self.ai_status.config(text="AI is thinking...")
        self.ai_output.config(state="normal"); self.ai_output.delete("1.0", tk.END); self.ai_output.config(state="disabled")
        self.update_idletasks()
        thread = threading.Thread(target=self.call_ai_api, args=(prompt,))
        thread.start()

    def call_ai_api(self, prompt):
        response = self.ai_client.generate_response(prompt)
        self.after(0, self.update_ai_output, response)

    def update_ai_output(self, response):
        self.ai_output.config(state="normal"); self.ai_output.insert(tk.END, response); self.ai_output.config(state="disabled")
        self.ask_button.config(state="normal"); self.ai_status.config(text="")
        print("AI response displayed.")