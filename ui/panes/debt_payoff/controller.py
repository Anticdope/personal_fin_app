"""
Debt Payoff Pane - Controller
Coordinates between Model and View for debt payoff tracking
"""
from .model import DebtPayoffModel
from .view import DebtPayoffView


class DebtPayoffController:
    """Controller: Orchestrates debt payoff display and calculations"""
    
    def __init__(self, data_manager, parent=None):
        self.data_manager = data_manager
        self.model = DebtPayoffModel(data_manager)
        self.view = DebtPayoffView(parent)
        
        self.connect_signals()
        self.load_data()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        self.view.refresh_requested.connect(self.load_data)
    
    def load_data(self):
        """Load and display all debt data"""
        # Get summary
        summary = self.model.get_debt_summary()
        self.view.display_summary(summary)
        
        # Get debts with projections
        debts = self.model.get_all_debts()
        
        if not debts:
            self.view.show_no_debts_message()
            return
        
        # Calculate projections for each debt
        debts_with_projections = []
        for debt in debts:
            projection = self.model.calculate_payoff_projection(
                debt['balance'],
                debt['interest_rate'],
                debt['minimum_payment']
            )
            debts_with_projections.append((debt, projection))
        
        # Display
        self.view.display_debts(debts_with_projections)
    
    def refresh(self):
        """Refresh the debt data (called when data changes)"""
        self.load_data()
    
    def update_data(self, year, month):
        """
        Update the display with new data
        Note: Debt balances don't change by month, but we accept
        year/month for consistency with other panes
        """
        self.current_year = year
        self.current_month = month
        
        # Load current data
        self.load_data()
    
    def get_widget(self):
        """Return the view widget for embedding in main window"""
        return self.view
    
    def get_pane_name(self):
        """Return display name for this pane"""
        return "Debt Payoff"
    
    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)