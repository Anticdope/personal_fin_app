"""
Theme Manager - Handles application themes
Updated to support custom theme presets
"""
from pathlib import Path
from PySide6.QtWidgets import QApplication


class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        self.themes_dir = Path("themes")
        self.themes_dir.mkdir(exist_ok=True)
        self.current_theme = "light"
        self.custom_qss = None
    
    def apply_theme(self, theme_name):
        """Apply a built-in theme (light or dark)"""
        self.current_theme = theme_name
        theme_file = self.themes_dir / f"{theme_name}.qss"
        
        if theme_file.exists():
            with open(theme_file, 'r') as f:
                qss = f.read()
            
            self.apply_stylesheet(qss)
            print(f"✅ Theme '{theme_name}' applied successfully")
        else:
            print(f"❌ Theme file not found: {theme_file}")
    
    # Alias for backward compatibility
    def load_theme(self, theme_name):
        """Alias for apply_theme() for backward compatibility"""
        return self.apply_theme(theme_name)
    
    def apply_custom_theme(self, qss_content):
        """Apply a custom theme from QSS string"""
        self.custom_qss = qss_content
        self.apply_stylesheet(qss_content)
        print("✅ Custom theme applied successfully")
    
    def apply_stylesheet(self, qss):
        """Apply QSS stylesheet to the application"""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "light":
            self.apply_theme("dark")
        else:
            self.apply_theme("light")
    
    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme
    
    def is_dark_mode(self):
        """Check if dark mode is active"""
        return self.current_theme == "dark"