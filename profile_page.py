# smartplate/ui/profile_page.py
from tkinter import ttk, messagebox, TclError
from .base_page import BasePage
from .widgets import ThemedLabel, ThemedEntry, AccentButton

class ProfilePage(BasePage):
    PAGE_NAME = "Profile"
    def __init__(self, master, user): self.user = user; self.entries = {}; super().__init__(master)
    def build(self):
        main_container = ttk.Frame(self, style="TFrame"); main_container.pack(expand=True)
        left_frame = ttk.Frame(main_container, style="TFrame", width=400); left_frame.pack(side="left", fill="y", padx=(0, 30))
        ThemedLabel(left_frame, text="User Profile", font=("Segoe UI", 20, "bold"), foreground=self.theme.accent()).pack(pady=(0, 20))
        fields = {"name": ("Name", ThemedEntry),"dob": ("Date of Birth (YYYY-MM-DD)", ThemedEntry),"height_cm": ("Height (cm)", ThemedEntry),"weight_kg": ("Weight (kg)", ThemedEntry),"activity_level": ("Activity Level", ttk.Combobox)}
        for key, (label, widget_class) in fields.items():
            row = ttk.Frame(left_frame, style="TFrame"); row.pack(fill="x", pady=6)
            ThemedLabel(row, text=f"{label}:", width=25).pack(side="left")
            if widget_class == ttk.Combobox: entry = widget_class(row, values=["Sedentary: little or no exercise","Light: 1-3 days/week exercise","Moderate: 3-5 days/week exercise","Active: 6-7 days/week exercise","Very Active: physical job or training"], style='TCombobox', state='readonly', width=30) # Added width
            else: entry = widget_class(row)
            entry.pack(side="left", fill="x", expand=True); self.entries[key] = entry
        AccentButton(left_frame, text="Save Profile", command=self.save_data).pack(pady=25, ipady=5, ipadx=10)
        right_frame = ttk.Frame(main_container, style="TFrame"); right_frame.pack(side="left", fill="y")
        ThemedLabel(right_frame, text="Health Metrics", font=("Segoe UI", 20, "bold"), foreground=self.theme.accent()).pack(pady=(0, 20))
        self.bmi_label = ThemedLabel(right_frame, text="BMI: -", font=("Segoe UI", 14)); self.bmi_label.pack(anchor="w")
        self.bmi_category_label = ThemedLabel(right_frame, text="Category: -", font=("Segoe UI", 11)); self.bmi_category_label.pack(anchor="w", pady=(5,0))
        # load_data is called by main_window on navigate
    def save_data(self):
        from ..db import update_profile # Import here
        if self.user["id"] == 0: messagebox.showinfo("Guest Mode", "Cannot save profile in Guest Mode.", parent=self); return
        try:
            # Use get() safely, providing 0 if empty or invalid
            height_str = self.entries["height_cm"].get()
            weight_str = self.entries["weight_kg"].get()
            height = float(height_str) if height_str else 0
            weight = float(weight_str) if weight_str else 0
            name = self.entries["name"].get(); dob = self.entries["dob"].get(); activity = self.entries["activity_level"].get()
            update_profile(self.user["id"], name, dob, height, weight, activity)
            messagebox.showinfo("Success", "Profile saved.", parent=self); self.calculate_bmi()
        except ValueError: messagebox.showerror("Invalid Input", "Height and Weight must be numbers.", parent=self)
        except Exception as e: messagebox.showerror("Error", f"Failed to save profile: {e}", parent=self)
    def load_data(self):
        from ..db import get_profile # Import here
        if self.user["id"] == 0: return
        profile = get_profile(self.user["id"])
        if profile:
            for key, widget in self.entries.items():
                val = profile.get(key)
                if val is not None:
                    if isinstance(widget, ttk.Combobox): widget.set(val)
                    else: widget.delete(0, 'end'); widget.insert(0, str(val))
        else: # Clear if no profile
            for widget in self.entries.values():
                 if isinstance(widget, ttk.Combobox): widget.set('')
                 else: widget.delete(0, 'end')
        self.calculate_bmi() # Calculate even if profile is empty/new
    def calculate_bmi(self):
        try:
            # Use get() safely
            height_str = self.entries["height_cm"].get()
            weight_str = self.entries["weight_kg"].get()
            h = float(height_str) if height_str else 0
            w = float(weight_str) if weight_str else 0
            if h <= 0 or w <= 0: raise ValueError("Height and weight must be positive.")
            bmi = round(w / ((h / 100) ** 2), 1)
            if bmi < 18.5: cat = "Underweight"
            elif 18.5 <= bmi < 24.9: cat = "Normal weight"
            elif 25 <= bmi < 29.9: cat = "Overweight"
            else: cat = "Obesity"
            self.bmi_label.config(text=f"BMI: {bmi}"); self.bmi_category_label.config(text=f"Category: {cat}")
        except (ValueError, TclError): self.bmi_label.config(text="BMI: -"); self.bmi_category_label.config(text="Category: -")