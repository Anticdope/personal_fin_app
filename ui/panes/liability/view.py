"""
ui/panes/liability/view.py

Liability Pane View - Pure UI for displaying liabilities.
Updated: DraggableCardContainer replaces plain scroll area.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from ui.shared.draggable_card_container import DraggableCardContainer


class LiabilityView(QWidget):
    """View: Pure UI for displaying liabilities"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self._current_data = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.card_container = DraggableCardContainer()
        layout.addWidget(self.card_container)

    def display_liabilities(self, liabilities_data):
        self._current_data = liabilities_data
        self.card_container.clear_cards()

        if not liabilities_data:
            empty = QLabel("No liabilities")
            empty.setObjectName("mutedLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.card_container.add_card("__empty__", empty)
            return

        for liability in liabilities_data:
            card_widget = self._build_card_widget(liability)
            card_id = liability.get('id', liability['name'])
            self.card_container.add_card(card_id, card_widget)

    def _build_card_widget(self, liability):
        inner = QFrame()
        inner.setObjectName("cardFrame")
        layout = QVBoxLayout(inner)

        name_label = QLabel(liability['name'])
        name_label.setObjectName("subtitle")
        layout.addWidget(name_label)

        balance_label = QLabel(f"Balance: ${liability['balance']:,.2f}")
        balance_label.setObjectName("negativeLabel")
        layout.addWidget(balance_label)

        if liability.get('original_balance'):
            orig = liability['original_balance']
            paid = orig - liability['balance']
            pct = (paid / orig * 100) if orig > 0 else 0
            progress_label = QLabel(f"Paid off: {pct:.1f}%")
            progress_label.setObjectName("mutedLabel")
            layout.addWidget(progress_label)

        if liability.get('minimum_payment'):
            min_pay_label = QLabel(f"Min Payment: ${liability['minimum_payment']:,.2f}")
            min_pay_label.setObjectName("mutedLabel")
            layout.addWidget(min_pay_label)

        return inner

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
