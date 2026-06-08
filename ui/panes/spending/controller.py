"""
Spending Controller - Coordinates Model and View
"""
from .model import SpendingModel
from .view import SpendingView


class SpendingController:
    """Controller: Coordinates between Model and View"""

    def __init__(self, data_manager, parent=None):
        self.data_manager = data_manager
        self.model = SpendingModel(data_manager)
        self.view = SpendingView(parent)
        self.parent = parent
        self.current_year = None
        self.current_month = None

        self.view.chart_clicked.connect(self._on_chart_clicked)

    def update_data(self, year, month):
        """Update the display with new data. Called by dashboard when month changes."""
        self.current_year = year
        self.current_month = month

        spending_data = self.model.get_spending_data(year, month)
        self.view.display_spending(spending_data)

    def refresh(self):
        """Refresh with current year/month"""
        if self.current_year and self.current_month:
            self.update_data(self.current_year, self.current_month)

    def _on_chart_clicked(self):
        """Open the spending breakdown dialog."""
        if self.current_year is None or self.current_month is None:
            return

        # Import here to avoid circular imports
        from ui.dialogs.spending_breakdown.controller import SpendingBreakdownController

        dialog = SpendingBreakdownController(
            self.data_manager,
            self.current_year,
            self.current_month,
            parent=self.view
        )

        # Match current theme if dark mode is active
        if hasattr(self.view, 'dark_mode'):
            dialog.set_dark_mode(self.view.dark_mode)

        dialog.exec()

    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)

    def get_widget(self):
        """Return the view widget for adding to layouts"""
        return self.view

    def get_pane_name(self):
        """Return display name for this pane"""
        return "Monthly Spending"