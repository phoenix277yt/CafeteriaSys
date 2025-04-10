import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import json

class ThemeManager:
    """Theme manager for the cafeteria management system"""
    
    def __init__(self, theme_file=None):
        """Initialize the theme manager"""
        self.theme_file = theme_file or "blueberry.css"
        self.themes = ["default.css", "blueberry.css", "dark.css", "light.css"]
        self.provider = Gtk.CssProvider()
        
        # Create css directory if it doesn't exist
        if not os.path.exists("css"):
            os.makedirs("css")
            self.create_default_themes()
    
    def create_default_themes(self):
        """Create default theme files if they don't exist"""
        themes = {
            "default.css": """
                .sub-header {
                    font-size: 18px;
                    font-weight: bold;
                }
                .card {
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #f5f5f5;
                }
                .success { background-color: #8BC34A; }
                .warning { background-color: #FF9800; }
                .error { background-color: #F44336; }
            """,
            "blueberry.css": """
                .sub-header {
                    font-size: 18px;
                    font-weight: bold;
                    color: #3F51B5;
                }
                .card {
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #E8EAF6;
                    border: 1px solid #C5CAE9;
                }
                .success { background-color: #8BC34A; }
                .warning { background-color: #FF9800; }
                .error { background-color: #F44336; }
            """,
            "dark.css": """
                window { background-color: #2D2D2D; }
                label { color: #E0E0E0; }
                .sub-header {
                    font-size: 18px;
                    font-weight: bold;
                    color: #90CAF9;
                }
                .card {
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #424242;
                    border: 1px solid #616161;
                }
                .success { background-color: #558B2F; }
                .warning { background-color: #EF6C00; }
                .error { background-color: #D32F2F; }
            """,
            "light.css": """
                window { background-color: #FFFFFF; }
                label { color: #212121; }
                .sub-header {
                    font-size: 18px;
                    font-weight: bold;
                    color: #1976D2;
                }
                .card {
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #F5F5F5;
                    border: 1px solid #E0E0E0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
                }
                .success { background-color: #8BC34A; }
                .warning { background-color: #FF9800; }
                .error { background-color: #F44336; }
            """
        }
        
        for theme_name, css in themes.items():
            path = os.path.join("css", theme_name)
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write(css)
    
    def apply_theme(self):
        """Apply the selected theme to the application"""
        # Try loading the theme file
        try:
            path = os.path.join("css", self.theme_file)
            if not os.path.exists(path):
                # If file doesn't exist, create default themes and retry
                self.create_default_themes()
            
            # Load CSS from file
            self.provider.load_from_path(path)
            
            # Add CSS provider to default screen
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                self.provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            
            print(f"Applied theme: {self.theme_file}")
            return True
        except Exception as e:
            print(f"Error applying theme: {e}")
            return False
    
    def create_theme_selector(self, parent_box):
        """Create theme selection dropdown"""
        theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        theme_label = Gtk.Label(label="Select Theme:")
        theme_box.pack_start(theme_label, False, False, 0)
        
        theme_combo = Gtk.ComboBoxText()
        for theme in self.themes:
            theme_combo.append_text(theme)
        
        # Set active theme
        try:
            active = self.themes.index(self.theme_file)
            theme_combo.set_active(active)
        except ValueError:
            theme_combo.set_active(0)
        
        theme_combo.connect("changed", self.on_theme_changed)
        theme_box.pack_start(theme_combo, True, True, 0)
        
        parent_box.pack_start(theme_box, False, False, 0)
    
    def on_theme_changed(self, combo):
        """Handle theme selection change"""
        active = combo.get_active()
        if active >= 0:
            self.theme_file = self.themes[active]
            self.apply_theme()