"""
Savings Goals Pane - Controller
Coordinates between Model and View
"""
from datetime import datetime
from .model import SavingsGoalsModel
from .view import SavingsGoalsView


class SavingsGoalsController:
    """Controller: Orchestrates savings goals pane"""
    
    def __init__(self, data_manager, parent=None):
        self.data_manager = data_manager
        self.model = SavingsGoalsModel(data_manager)
        self.view = SavingsGoalsView()  # Don't pass parent - it's not a QWidget
        
        self.refresh()
    
    def refresh(self):
        """Refresh the pane data"""
        # Get current month
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Update view
        self.view.set_month(year, month)
        
        # Get progress data
        goals_data = self.model.get_savings_progress(year, month)
        summary = self.model.get_total_savings_summary(year, month)
        
        # Display
        self.view.display_total_summary(summary)
        self.view.display_goals(goals_data)
    
    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)
    
    def get_widget(self):
        """Return the view widget for adding to layouts"""
        return self.view
    
    def get_pane_name(self):
        """Return the display name for this pane"""
        return "Savings Goals"
    
    def update_data(self, year, month):
        """Update data for a specific year/month"""
        # Update view
        self.view.set_month(year, month)
        
        # Get progress data
        goals_data = self.model.get_savings_progress(year, month)
        summary = self.model.get_total_savings_summary(year, month)
        
        # Display
        self.view.display_total_summary(summary)
        self.view.display_goals(goals_data)