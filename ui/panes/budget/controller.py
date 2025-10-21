from .model import BudgetModel
from .view import BudgetView

class BudgetController:
    """
    Controller: Coordinates between Model and View
    Handles user interactions and updates
    """
    
    def __init__(self, data_manager, parent=None):
        self.model = BudgetModel(data_manager)
        self.view = BudgetView(parent)
        self.current_year = None
        self.current_month = None
    
    def update_data(self, year, month):
        """
        Update the display with new data
        This is the main entry point called by the dashboard
        """
        self.current_year = year
        self.current_month = month
        
        # Get data from model
        data = self.model.get_budget_data(year, month)
        
        # Update view
        self.view.display_budgets(data['budget_status'])
    
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
        return "Budget Tracker"
