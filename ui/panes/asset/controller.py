"""
Asset Controller - Coordinates Model and View
"""
from .model import AssetModel
from .view import AssetView


class AssetController:
    """
    Controller: Coordinates between Model and View
    """
    
    def __init__(self, data_manager, parent=None):
        self.model = AssetModel(data_manager)
        self.view = AssetView(parent)
        self.current_year = None
        self.current_month = None
    
    def update_data(self, year, month):
        """
        Update the display with new data
        Note: Asset values don't change by month, but we accept
        year/month for consistency with other panes
        """
        self.current_year = year
        self.current_month = month
        
        # Get data from model
        assets_data = self.model.get_assets_data()
        
        # Update view
        self.view.display_assets(assets_data)
    
    def refresh(self):
        """Refresh with current year/month"""
        if self.current_year and self.current_month:
            self.update_data(self.current_year, self.current_month)
    
    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)
    
    def get_widget(self):
        """Return the view widget for adding to layouts"""
        return self.view
    
    def get_pane_name(self):
        """Return display name for this pane"""
        return "Assets"