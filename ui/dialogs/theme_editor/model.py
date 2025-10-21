"""
Theme Editor Model
Handles theme data and validation
"""
from themes.presets import THEME_PRESETS


class ThemeEditorModel:
    """Model: Theme data management and validation"""
    
    def __init__(self):
        self.available_presets = list(THEME_PRESETS.keys())
        self.current_preset = None
        self.current_qss = None
    
    def get_available_presets(self):
        """Get list of available theme preset names"""
        return self.available_presets
    
    def get_preset_qss(self, preset_name):
        """
        Get QSS content for a specific preset
        Returns: (success: bool, qss_content: str or error_message: str)
        """
        if preset_name in THEME_PRESETS:
            return True, THEME_PRESETS[preset_name]
        else:
            return False, f"Preset '{preset_name}' not found"
    
    def set_current_preset(self, preset_name):
        """Set the currently selected preset"""
        success, result = self.get_preset_qss(preset_name)
        if success:
            self.current_preset = preset_name
            self.current_qss = result
            return True
        return False
    
    def get_current_preset(self):
        """Get the currently selected preset name"""
        return self.current_preset
    
    def get_current_qss(self):
        """Get the QSS content of the current preset"""
        return self.current_qss
    
    def validate_qss(self, qss_content):
        """
        Validate QSS content (basic validation)
        Returns: (valid: bool, error_message: str or None)
        """
        if not qss_content or qss_content.strip() == "":
            return False, "QSS content cannot be empty"
        
        # Basic syntax check - ensure it has at least one selector
        if '{' not in qss_content or '}' not in qss_content:
            return False, "Invalid QSS syntax - missing selectors"
        
        return True, None
    
    def get_preset_description(self, preset_name):
        """Get a description of what makes each preset unique"""
        descriptions = {
            "Light (Default)": "Clean and simple light theme with subtle borders",
            "Dark (Default)": "Clean and simple dark theme with subtle borders",
            "Card Style - Light": "Elevated cards with rounded corners and no borders - modern look",
            "Card Style - Dark": "Elevated dark cards with rounded corners - modern dark look",
            "Panel Style - Light": "Clear borders and distinct panels - traditional interface",
            "Panel Style - Dark": "Clear borders and distinct dark panels - traditional dark interface",
            "Material Style - Light": "Soft shadows and minimal borders - Google Material Design inspired",
            "Material Style - Dark": "Soft shadows and minimal borders - Material Design dark theme"
        }
        return descriptions.get(preset_name, "No description available")