"""
Spending Breakdown Dialog - Controller
"""
from .model import SpendingBreakdownModel
from .view import SpendingBreakdownView


class SpendingBreakdownController:
    """Controller: Wires model → view for the spending breakdown dialog"""

    def __init__(self, data_manager, year, month, parent=None):
        self.model = SpendingBreakdownModel(data_manager)
        self.view = SpendingBreakdownView(parent)
        self._load(year, month)

    def _load(self, year, month):
        data = self.model.get_breakdown(year, month)
        self.view.display_breakdown(data)

    def exec(self):
        return self.view.exec()

    def set_dark_mode(self, enabled):
        self.view.set_dark_mode(enabled)