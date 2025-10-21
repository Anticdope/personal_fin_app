"""
Theme Editor Controller
"""
from .view import ThemeEditorView
from themes.presets import THEME_PRESETS


class ThemeEditorController:
    """Controller: Manages theme editor dialog"""
    
    def __init__(self, theme_manager, parent=None):
        self.theme_manager = theme_manager
        self.view = ThemeEditorView(parent)
        self.current_preset = "Light (Default)"
        
        self.connect_signals()
        self.load_initial_preset()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        self.view.preset_changed.connect(self.on_preset_changed)
        self.view.apply_theme.connect(self.on_apply_theme)
    
    def load_initial_preset(self):
        """Load the first preset on startup"""
        self.on_preset_changed("Light (Default)")
    
    def on_preset_changed(self, preset_name):
        """Handle preset selection change"""
        self.current_preset = preset_name
        
        # Get QSS content for this preset
        if preset_name in THEME_PRESETS:
            qss_content = THEME_PRESETS[preset_name]
            
            # Show QSS code
            self.view.set_qss_preview(qss_content)
            
            # Apply to preview
            self.view.apply_preview_style(qss_content)
    
    def on_apply_theme(self, preset_name):
        """Apply the selected theme to the main application"""
        if preset_name in THEME_PRESETS:
            qss_content = THEME_PRESETS[preset_name]
            
            # Apply through theme manager
            try:
                self.theme_manager.apply_custom_theme(qss_content)
                self.view.show_success(f"Applied theme: {preset_name}")
                self.view.accept()
            except Exception as e:
                self.view.show_error(f"Failed to apply theme: {str(e)}")
    
    def exec(self):
        """Show the dialog"""
        return self.view.exec()