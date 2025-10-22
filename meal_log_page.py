# smartplate/ui/meal_log_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from .base_page import BasePage
from .widgets import ThemedLabel, ThemedEntry, AccentButton, ThemedButton
from ..api_client import ApiClient
from .theme_manager import ThemeManager
import datetime
from ..db import add_meal, get_meals, delete_meal, update_meal

# --- Edit Log Window (from previous step, now used by Edit button) ---
class EditLogWindow(tk.Toplevel):
    def __init__(self, master, meal_data, on_save_callback):
        super().__init__(master)
        self.meal_data = meal_data; self.on_save_callback = on_save_callback
        self.title(f"Edit Log Entry (ID: {meal_data.get('id')})"); self.geometry("450x550")
        self.configure(bg=ThemeManager.bg()); self.transient(master); self.grab_set()
        container = ttk.Frame(self, style='TFrame', padding=20); container.pack(fill="both", expand=True)
        self.entries = {}
        fields = [("date_log", "Date (YYYY-MM-DD)"),("meal", "Meal Description"),("calories", "Calories (kcal)"),("protein", "Protein (g)"),("carbs", "Carbs (g)"),("fat", "Fat (g)"),("fiber", "Fiber (g)"),("sugar", "Sugar (g)"),("sodium", "Sodium (mg)")]
        for i, (key, label) in enumerate(fields):
            ThemedLabel(container, text=label).grid(row=i, column=0, sticky="w", pady=(0, 2))
            entry = ThemedEntry(container, width=50); entry.grid(row=i, column=1, sticky="ew", pady=(0, 10))
            entry.insert(0, self.meal_data.get(key, "")); self.entries[key] = entry
        AccentButton(container, text="Save Changes", command=self.save_changes).grid(row=len(fields), column=0, columnspan=2, pady=(20, 0))
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width()//2) - (self.winfo_width()//2)
        y = master.winfo_rooty() + (master.winfo_height()//2) - (self.winfo_height()//2)
        self.geometry(f'+{x}+{y}')
    def save_changes(self):
        try:
            new_data = {key: entry.get() for key, entry in self.entries.items()}
            update_meal(meal_id=self.meal_data['id'], date_str=new_data['date_log'], meal=new_data['meal'], calories_str=new_data['calories'], protein_str=new_data['protein'], carbs_str=new_data['carbs'], fat_str=new_data['fat'], fiber_str=new_data['fiber'], sugar_str=new_data['sugar'], sodium_str=new_data['sodium'])
            messagebox.showinfo("Success", "Meal log updated successfully.", parent=self)
            self.on_save_callback(); self.destroy()
        except Exception as e: print(f"Error saving meal log: {e}"); messagebox.showerror("Error", f"Failed to update log: {e}", parent=self)

# --- Recipe Selection Window (from previous step) ---
class RecipeSelectionWindow(tk.Toplevel):
    def __init__(self, master, recipes, on_select_callback):
        super().__init__(master)
        self.title("Select a Recipe"); self.geometry("650x400"); self.configure(bg=ThemeManager.bg()); self.transient(master); self.grab_set()
        self.on_select_callback = on_select_callback; self.recipes = recipes
        ThemedLabel(self, text="Select the best match:", font=("Segoe UI", 12)).pack(pady=(10,5))
        cols = ("Recipe Name", "Calories"); self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Treeview", height=10)
        self.tree.heading("Recipe Name", text="Recipe Name"); self.tree.column("Recipe Name", width=450, anchor="w")
        self.tree.heading("Calories", text="Calories"); self.tree.column("Calories", width=100, anchor="center")
        print(f"[RecipeSelectionWindow] Received {len(recipes)} recipes:")
        if not recipes: ThemedLabel(self, text="No recipes found by API.", foreground="red").pack(pady=20)
        for i, recipe in enumerate(recipes):
            title = recipe.get("title", "Unknown"); cals = recipe.get("calories", "-")
            try: self.tree.insert("", "end", iid=i, values=(title, cals))
            except Exception as e: print(f"ERROR inserting recipe {i}: {e}")
        self.tree.pack(fill="x", expand=True, padx=10, pady=(0, 5)); self.tree.bind("<Double-1>", self.on_select)
        AccentButton(self, text="Use Selected Recipe", command=self.on_select).pack(pady=10)
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width()//2) - (self.winfo_width()//2)
        y = master.winfo_rooty() + (master.winfo_height()//2) - (self.winfo_height()//2)
        self.geometry(f'+{x}+{y}')
    def on_select(self, event=None):
        selected_item_iid = self.tree.selection()
        if not selected_item_iid: messagebox.showwarning("No Selection", "Please select a recipe.", parent=self); return
        try:
            selected_index = int(selected_item_iid[0]); selected_recipe = self.recipes[selected_index] 
            if selected_recipe: self.on_select_callback(selected_recipe); self.destroy()
            else: messagebox.showerror("Error", "Could not retrieve selected recipe data.", parent=self)
        except (ValueError, IndexError) as e: messagebox.showerror("Error", f"Invalid selection index: {e}", parent=self)

# --- Main Meal Log Page Class ---
class MealLogPage(BasePage):
    PAGE_NAME = "Meal Log"
    def __init__(self, master, user):
        self.user = user; self.api_client = ApiClient(); self.meal_data_map = {}; super().__init__(master)

    def build(self):
        # --- Top frame for input fields ---
        top_frame = ttk.Frame(self, style='TFrame'); top_frame.pack(fill="x", padx=20, pady=(10,5))
        
        # --- Input Grid (Left Side) ---
        input_grid = ttk.Frame(top_frame, style='TFrame'); input_grid.pack(side="left", fill="x", expand=True)

        self.entries = {}
        fields = [("meal", "Meal Description"), ("calories", "Calories (kcal)"), ("protein", "Protein"), ("carbs", "Carbs"), ("fat", "Fat"), ("fiber", "Fiber"), ("sugar", "Sugar"), ("sodium", "Sodium")]
        
        # Meal description (spans two columns)
        ThemedLabel(input_grid, text="Meal Description:").grid(row=0, column=0, columnspan=4, sticky="w", pady=2)
        self.entries['meal'] = ThemedEntry(input_grid); self.entries['meal'].grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0,10))

        # Nutrient fields in a 2x3 grid
        row, col = 2, 0
        for key, label in fields[1:]: # Skip 'meal'
            ThemedLabel(input_grid, text=f"{label}:").grid(row=row, column=col, sticky="w", pady=2)
            self.entries[key] = ThemedEntry(input_grid); self.entries[key].grid(row=row+1, column=col, sticky="ew", padx=(0,10))
            col += 1
            if col >= 4: col = 0; row += 2
            
        # --- Button Frame (Right Side) ---
        btn_frame = ttk.Frame(top_frame, style='TFrame'); btn_frame.pack(side="left", padx=(20,0))
        AccentButton(btn_frame, text="Analyze with API", command=self.analyze_meal).pack(fill="x", ipady=5, ipadx=5, pady=5)
        ThemedButton(btn_frame, text="Add to Log", command=self.add_log_entry).pack(fill="x", ipady=5, ipadx=5, pady=5)
        ThemedButton(btn_frame, text="Clear / Manual Entry", command=self.clear_fields).pack(fill="x", ipady=5, ipadx=5, pady=5)

        # --- Data Table Frame ---
        table_frame = ttk.Frame(self, style='TFrame'); table_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))
        columns = ("id", "date_log", "meal", "calories", "protein", "carbs", "fat"); self.table = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        col_map = {"id": "ID", "date_log": "Date", "meal": "Meal", "calories": "Cals", "protein": "Protein", "carbs": "Carbs", "fat": "Fat"}
        for col_id, col_name in col_map.items(): 
            width = 250 if col_id == "meal" else (90 if col_id == "date_log" else (40 if col_id == "id" else 80))
            anchor = "w" if col_id == "meal" else "center"
            self.table.heading(col_id, text=col_name); self.table.column(col_id, width=width, anchor=anchor, stretch=False)
        self.table.pack(side="left", fill="both", expand=True); 
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview); self.table.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        
        # --- Edit/Delete Button Frame ---
        edit_delete_frame = ttk.Frame(self, style='TFrame'); edit_delete_frame.pack(fill="x", padx=20, pady=(0,10))
        AccentButton(edit_delete_frame, text="Edit Selected", command=self.on_edit_selected).pack(side="left", ipadx=5, ipady=5)
        ThemedButton(edit_delete_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=10, ipadx=5, ipady=5)
        ThemedLabel(edit_delete_frame, text=" (or double-click to edit)", font=("Segoe UI", 9, "italic"), foreground=self.theme.muted()).pack(side="left", pady=5)
        self.table.bind("<Double-1>", self.on_edit_selected)

    def analyze_meal(self):
        query = self.entries['meal'].get().strip()
        if not query: messagebox.showwarning("Input Needed", "Please enter a meal description to analyze.", parent=self); return
        api_result = self.api_client.analyze_natural(query)
        if "error" in api_result: messagebox.showerror("API Error", api_result["error"], parent=self)
        elif "recipes" in api_result:
            recipes = api_result["recipes"]
            if not recipes: messagebox.showinfo("No Results", "No matching recipes found.", parent=self)
            elif len(recipes) == 1: self.populate_fields(recipes[0])
            else: RecipeSelectionWindow(self, recipes, self.populate_fields)
        else: messagebox.showerror("API Error", "Unexpected response format from API.", parent=self)

    def populate_fields(self, recipe_data):
        """Populates the entry fields with data from API or for clearing."""
        print(f"Populating fields with: {recipe_data}")
        nutrients = recipe_data.get('nutrients', {})
        def format_val(code, unit):
            n = nutrients.get(code)
            return f"{n['quantity']:.1f}{n['unit']}" if n else ""
            
        data_map = {
            'meal': recipe_data.get('title', ''),
            'calories': f"{recipe_data.get('calories', ''):.0f}",
            'protein': format_val('PROCNT', 'g'),
            'carbs': format_val('CHOCDF', 'g'),
            'fat': format_val('FAT', 'g'),
            'fiber': format_val('FIBTG', 'g'),
            'sugar': format_val('SUGAR', 'g'),
            'sodium': format_val('NA', 'mg')
        }
        for key, widget in self.entries.items():
            widget.delete(0, tk.END)
            widget.insert(0, data_map.get(key, ""))
        
    def add_log_entry(self):
        if self.user["id"] == 0: messagebox.showinfo("Guest Mode", "Please sign up or log in to save.", parent=self); return
        try:
            date = datetime.date.today().isoformat()
            # Get all values directly from the entry fields
            add_meal(self.user["id"], date,
                     self.entries['meal'].get(), self.entries['calories'].get(),
                     self.entries['protein'].get(), self.entries['carbs'].get(),
                     self.entries['fat'].get(), self.entries['fiber'].get(),
                     self.entries['sugar'].get(), self.entries['sodium'].get())
            self.clear_fields()
            self.load_data()
        except Exception as e: messagebox.showerror("Database Error", f"Failed to add meal log: {e}", parent=self)

    def clear_fields(self):
        for widget in self.entries.values(): widget.delete(0, tk.END)
        self.entries['meal'].focus() # Set focus back to meal description
        
    def load_data(self):
        self.table.delete(*self.table.get_children()); self.meal_data_map.clear()
        if self.user["id"] == 0: return
        try:
            rows = get_meals(self.user["id"])
            for row in rows:
                self.meal_data_map[row['id']] = row 
                self.table.insert("", "end", iid=row["id"], values=(
                    row.get("id", ""), row.get("date_log", ""), row.get("meal", ""), 
                    f"{row.get('calories', 0):.0f}", row.get("protein", ""), 
                    row.get("carbs", ""), row.get("fat", "")))
        except Exception as e: messagebox.showerror("Load Error", f"Could not load meal data: {e}", parent=self)
            
    def delete_selected(self):
        if self.user["id"] == 0: messagebox.showinfo("Guest Mode", "No logs to delete.", parent=self); return
        selected_iids = self.table.selection();
        if not selected_iids: messagebox.showwarning("No Selection", "Please select one or more entries.", parent=self); return
        if messagebox.askyesno("Confirm", f"Delete {len(selected_iids)} selected entries?"):
            try:
                for item_id in selected_iids: delete_meal(item_id)
                self.load_data()
            except Exception as e: messagebox.showerror("Delete Error", f"Failed to delete entries: {e}", parent=self)

    def on_edit_selected(self, event=None):
        """Called by button click or double-click."""
        selected_iid = self.table.selection()
        if not selected_iid: messagebox.showwarning("No Selection", "Please select an entry from the log to edit.", parent=self); return
        item_id = int(selected_iid[0])
        meal_data_to_edit = self.meal_data_map.get(item_id)
        if not meal_data_to_edit: messagebox.showerror("Error", "Could not find data for the selected log.", parent=self); return
        EditLogWindow(self, meal_data=meal_data_to_edit, on_save_callback=self.load_data)