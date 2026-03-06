"""
ui/panes/account_balance/view.py

Account Balance View - Pure UI for account balance display.
Updated: DraggableCardContainer replaces fixed-height scroll area.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from ui.shared.draggable_card_container import DraggableCardContainer


class AccountBalanceView(QWidget):
    """View: Pure UI for displaying account balances"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self._current_data = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.card_container = DraggableCardContainer()
        layout.addWidget(self.card_container)

    def display_accounts(self, accounts_data):
        """Display list of accounts. Preserves externally applied order."""
        self._current_data = accounts_data
        self.card_container.clear_cards()

        if not accounts_data:
            empty = QLabel("No accounts yet")
            empty.setObjectName("mutedLabel")
            empty.setAlignment(Qt.AlignCenter)
            # Add as a plain (non-draggable) label
            self.card_container.add_card("__empty__", empty)
            return

        for account in accounts_data:
            card_widget = self._build_card_widget(account)
            card_id = account.get('id', account['name'])
            self.card_container.add_card(card_id, card_widget)

    def _build_card_widget(self, account):
        inner = QFrame()
        inner.setObjectName("cardFrame")
        inner_layout = QHBoxLayout(inner)

        name_label = QLabel(account['name'])
        name_label.setObjectName("sectionTitle")

        type_label = QLabel(f"({account['type'].title()})")
        type_label.setObjectName("mutedLabel")

        balance = account['balance']
        balance_label = QLabel(f"${balance:.2f}")
        if account.get('is_credit') or balance < 0:
            balance_label.setObjectName("negativeLabel")
        else:
            balance_label.setObjectName("positiveLabel")

        inner_layout.addWidget(name_label)
        inner_layout.addWidget(type_label)
        inner_layout.addStretch()
        inner_layout.addWidget(balance_label)
        return inner

    def _clear_accounts(self):
        self.card_container.clear_cards()

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        if self._current_data:
            self.display_accounts(self._current_data)
