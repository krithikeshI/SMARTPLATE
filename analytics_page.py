# smartplate/ui/analytics_page.py
import tkinter as tk
from .base_page import BasePage
from .widgets import ThemedLabel
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class AnalyticsPage(BasePage):
    PAGE_NAME = "Analytics"
    # ... (__init__) ...
    def __init__(self, master, user):
        self.user = user; super().__init__(master)

    def build(self):
        title_frame = tk.Frame(self, bg=self.theme.bg())
        title_frame.pack(fill="x", padx=20, pady=(10, 0))
        ThemedLabel(title_frame, text="Today's Nutritional Summary", font=("Segoe UI", 18, "bold"), foreground=self.theme.accent()).pack(side="left")

        chart_frame = tk.Frame(self, bg=self.theme.bg())
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_chart(self):
        from ..db import get_all_nutrition_for_today
        self.ax.clear(); p = self.theme.palette(); self.fig.patch.set_facecolor(p['bg'])
        text_props = {'color': p['text'], 'fontsize': 10}

        if self.user['id'] == 0:
            self.ax.text(0.5, 0.5, "Please log in to track analytics", ha='center', va='center', fontsize=12, color=p['text'])
            self.ax.set_axis_off(); self.canvas.draw(); return

        data = get_all_nutrition_for_today(self.user['id'])

        if not data or data.get('total_calories', 0) == 0:
            self.ax.text(0.5, 0.5, "No data logged for today", ha='center', va='center', fontsize=12, color=p['text'])
            self.ax.set_axis_off(); self.canvas.draw(); return

        # --- ✅ Update Labels with Units ---
        labels = ['Sodium (mg)', 'Sugar (g)', 'Fiber (g)', 'Fat (g)', 'Carbs (g)', 'Protein (g)', 'Calories (kcal)']
        # --- End Update ---
        values = [
            data.get('total_sodium', 0), data.get('total_sugar', 0), data.get('total_fiber', 0),
            data.get('total_fat', 0), data.get('total_carbs', 0), data.get('total_protein', 0),
            data.get('total_calories', 0)
        ]

        y_pos = range(len(labels))
        bars = self.ax.barh(y_pos, values, align='center', color=p['accent'])
        self.ax.set_yticks(y_pos, labels=labels, **text_props, weight='bold')
        self.ax.invert_yaxis()
        self.ax.set_xlabel('Total Amount', **text_props)
        self.ax.set_title("Today's Nutrient Totals", **text_props, weight='bold', size=14)

        self.ax.set_facecolor(p['panel'])
        self.ax.tick_params(axis='x', colors=p['text'])
        self.ax.tick_params(axis='y', colors=p['text'])
        self.ax.spines['top'].set_visible(False); self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color(p['muted']); self.ax.spines['bottom'].set_color(p['muted'])

        self.ax.bar_label(bars, fmt='%.1f', padding=5, color=p['text'], fontsize=9)
        if values: # Avoid error if values list is empty
            self.ax.set_xlim(right=max(values or [0]) * 1.15) # Ensure right limit is valid

        self.canvas.draw()