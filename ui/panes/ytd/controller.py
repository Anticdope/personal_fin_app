"""
YTD Controller - Coordinates Model and View
"""
from .model import YTDModel
from .view import YTDView


class YTDController:
    """
    Controller: Coordinates between Model and View
    """
    
    def __init__(self, data_manager, parent=None):
        self.model = YTDModel(data_manager)
        self.view = YTDView(parent)
        self.current_year = None
        self.current_month = None
    
    def update_data(self, year, month):
        """
        Update the display with new data
        Called by dashboard when month changes
        """
        self.current_year = year
        self.current_month = month
        
        # Get data from model
        data = self.model.get_ytd_data(year, month)
        
        # Update view
        self.view.display_ytd(data)
    
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
        return "Year-to-Date"