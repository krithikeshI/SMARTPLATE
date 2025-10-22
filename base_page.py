# smartplate/ui/base_page.py
from tkinter import ttk
from .theme_manager import ThemeManager

class BasePage(ttk.Frame):
    PAGE_NAME = "Base" # Should be overridden by subclasses

    def __init__(self, master, **kwargs):
        # Initialize the ttk.Frame using the 'TFrame' style.
        # This style automatically gets the background color from ThemeManager.
        super().__init__(master, style='TFrame', **kwargs) 
        
        self.theme = ThemeManager # Provide easy access to theme methods
        
        # Build the specific content for the page
        self.build() 

    def build(self):
        """Subclasses must implement this method to create their widgets."""
        raise NotImplementedError("Subclasses must implement the build method")