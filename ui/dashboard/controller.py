"""
Dashboard Controller - Coordinates Model and View
"""
from PySide6.QtCore import QObject, Signal
from .model import DashboardModel
from .view import DashboardView


class DashboardController(QObject):
    """
    Controller: Coordinates dashboard model and view
    Manages pane navigation and updates
    """
    
    # Signals for communication with main window
    manage_categories_clicked = Signal()
    manage_accounts_clicked = Signal()
    dark_mode_toggled = Signal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.model = DashboardModel()
        self.view = DashboardView(parent)
        
        # Connect view signals
        self.view.manage_categories_clicked.connect(self.manage_categories_clicked.emit)
        self.view.manage_accounts_clicked.connect(self.manage_accounts_clicked.emit)
        self.view.dark_mode_toggled.connect(self.dark_mode_toggled.emit)
        self.view.prev_top_clicked.connect(self._on_prev_top)
        self.view.next_top_clicked.connect(self._on_next_top)
        self.view.prev_bottom_clicked.connect(self._on_prev_bottom)
        self.view.next_bottom_clicked.connect(self._on_next_bottom)
    
    def load_panes(self):
        """Load all panes into the dashboard"""
        # Import pane controllers
        from ui.panes.budget.controller import BudgetController
        from ui.panes.net_worth.controller import NetWorthController
        from ui.panes.ytd.controller import YTDController
        from ui.panes.account_balance.controller import AccountBalanceController
        from ui.panes.asset.controller import AssetController
        from ui.panes.liability.controller import LiabilityController
        from ui.panes.spending.controller import SpendingController
        from ui.panes.savings_goal import SavingsGoalsController
        from ui.panes.debt_payoff.controller import DebtPayoffController
        
        # TOP PANES (Input)
        top_panes = [
            AccountBalanceController(self.data_manager, self.view),
            AssetController(self.data_manager, self.view),
            LiabilityController(self.data_manager, self.view),
        ]
        
        # BOTTOM PANES (Summaries)
        bottom_panes = [
            SpendingController(self.data_manager, self.view),
            BudgetController(self.data_manager, self.view),
            SavingsGoalsController(self.data_manager, self),
            NetWorthController(self.data_manager, self.view),
            YTDController(self.data_manager, self.view),
            DebtPayoffController(self.data_manager, self.view)
        ]
        
        # Set panes in model
        self.model.set_panes(top_panes, bottom_panes)
        
        # Add pane widgets to view
        for pane in top_panes:
            if hasattr(pane, 'get_widget'):
                self.view.add_top_pane(pane.get_widget())
            else:
                self.view.add_top_pane(pane)
        
        for pane in bottom_panes:
            if hasattr(pane, 'get_widget'):
                self.view.add_bottom_pane(pane.get_widget())
            else:
                self.view.add_bottom_pane(pane)
        
        # Update labels
        self._update_pane_labels()
    
    def update_dashboard(self, year, month):
        """Update all panes with data for the given year/month"""
        self.model.set_current_period(year, month)
        
        # Update all panes
        for pane in self.model.top_panes + self.model.bottom_panes:
            if hasattr(pane, 'update_data'):
                pane.update_data(year, month)
    
    def _on_prev_top(self):
        """Handle previous top pane button"""
        if self.model.go_prev_top():
            self.view.set_top_pane_index(self.model.current_top_index)
            self._update_pane_labels()
    
    def _on_next_top(self):
        """Handle next top pane button"""
        if self.model.go_next_top():
            self.view.set_top_pane_index(self.model.current_top_index)
            self._update_pane_labels()
    
    def _on_prev_bottom(self):
        """Handle previous bottom pane button"""
        if self.model.go_prev_bottom():
            self.view.set_bottom_pane_index(self.model.current_bottom_index)
            self._update_pane_labels()
    
    def _on_next_bottom(self):
        """Handle next bottom pane button"""
        if self.model.go_next_bottom():
            self.view.set_bottom_pane_index(self.model.current_bottom_index)
            self._update_pane_labels()
    
    def _update_pane_labels(self):
        """Update pane name labels"""
        top_pane = self.model.get_top_pane()
        if top_pane:
            name = self.model.get_pane_name(top_pane)
            self.view.update_top_pane_label(name)
        
        bottom_pane = self.model.get_bottom_pane()
        if bottom_pane:
            name = self.model.get_pane_name(bottom_pane)
            self.view.update_bottom_pane_label(name)
    
    def set_dark_mode(self, dark_mode):
        """Update theme for dashboard and all panes"""
        self.view.set_dark_mode(dark_mode)
        self.view.update_dark_mode_button(dark_mode)
        
        # Update all panes
        for pane in self.model.top_panes + self.model.bottom_panes:
            if hasattr(pane, 'set_dark_mode'):
                pane.set_dark_mode(dark_mode)
    
    def get_widget(self):
        """Return the view widget for adding to layouts"""
        return self.view