"""
ui/panes/savings_goal/controller.py

Savings Goals Controller.
Updated: Wires DraggableCardContainer order_changed signal to CardOrderRepository.
"""
from datetime import datetime
from .model import SavingsGoalsModel
from .view import SavingsGoalsView
from data.repositories.card_order_repository import CardOrderRepository

PANE_KEY = "savings_goals"


class SavingsGoalsController:
    """Controller: Orchestrates savings goals pane"""

    def __init__(self, data_manager, parent=None):
        self.data_manager = data_manager
        self.model = SavingsGoalsModel(data_manager)
        self.view = SavingsGoalsView()
        self._order_repo = CardOrderRepository(data_manager.data_dir)

        self.view.card_container.order_changed.connect(self._on_order_changed)

        self.refresh()

    def refresh(self):
        now = datetime.now()
        self.update_data(now.year, now.month)

    def update_data(self, year, month):
        self.view.set_month(year, month)

        goals_data = self.model.get_savings_progress(year, month)
        summary = self.model.get_total_savings_summary(year, month)

        self.view.display_total_summary(summary)
        self.view.display_goals(goals_data)

        saved_order = self._order_repo.get_order(PANE_KEY)
        if saved_order:
            self.view.card_container.set_order(saved_order)

    def _on_order_changed(self, new_order):
        self._order_repo.save_order(PANE_KEY, new_order)

    def set_dark_mode(self, enabled):
        self.view.set_dark_mode(enabled)

    def get_widget(self):
        return self.view

    def get_pane_name(self):
        return "Savings Goals"
