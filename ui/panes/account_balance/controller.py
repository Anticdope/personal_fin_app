"""
ui/panes/account_balance/controller.py

Account Balance Controller.
Updated: Wires DraggableCardContainer order_changed signal to CardOrderRepository.
"""
from .model import AccountBalanceModel
from .view import AccountBalanceView
from data.repositories.card_order_repository import CardOrderRepository

PANE_KEY = "account_balances"


class AccountBalanceController:
    """Controller: Coordinates between Model and View"""

    def __init__(self, data_manager, parent=None):
        self.model = AccountBalanceModel(data_manager)
        self.view = AccountBalanceView(parent)
        self.current_year = None
        self.current_month = None
        self._order_repo = CardOrderRepository(data_manager.data_dir)

        # Wire order-changed signal
        self.view.card_container.order_changed.connect(self._on_order_changed)

    def update_data(self, year, month):
        self.current_year = year
        self.current_month = month

        accounts_data = self.model.get_accounts_data()
        self.view.display_accounts(accounts_data)

        # Apply saved order after cards are built
        saved_order = self._order_repo.get_order(PANE_KEY)
        if saved_order:
            self.view.card_container.set_order(saved_order)

    def refresh(self):
        if self.current_year and self.current_month:
            self.update_data(self.current_year, self.current_month)

    def _on_order_changed(self, new_order):
        self._order_repo.save_order(PANE_KEY, new_order)

    def set_dark_mode(self, enabled):
        self.view.set_dark_mode(enabled)

    def get_widget(self):
        return self.view

    def get_pane_name(self):
        return "Account Balances"
