"""
ui/panes/budget/view.py

Budget View - Pure UI for budget display.
Updated: DraggableCardContainer replaces plain scroll area.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QProgressBar)
from PySide6.QtCore import Qt
from ui.shared.draggable_card_container import DraggableCardContainer


class BudgetView(QWidget):
    """View: Pure UI for displaying budget vs actual spending"""

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

    def display_budgets(self, budget_data):
        self._current_data = budget_data
        self.card_container.clear_cards()

        if not budget_data:
            empty = QLabel("No budgets set")
            empty.setObjectName("mutedLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.card_container.add_card("__empty__", empty)
            return

        for item in budget_data:
            card_widget = self._build_card_widget(item)
            card_id = item.get('id', item['name'])
            self.card_container.add_card(card_id, card_widget)

    def _build_card_widget(self, item):
        element = QFrame()
        element.setObjectName("cardFrame")
        layout = QVBoxLayout(element)
        layout.setSpacing(5)

        # Header: color dot + name
        header_row = QHBoxLayout()
        color_indicator = QLabel("●")
        color_indicator.setStyleSheet(f"color: {item['color']}; font-size: 60px;")
        name_label = QLabel(item['name'])
        name_label.setObjectName("subtitle")
        header_row.addWidget(color_indicator)
        header_row.addWidget(name_label)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Amounts
        amounts_row = QHBoxLayout()
        budget_label = QLabel(f"Budget: ${item['budget']:.2f}")
        spent_label = QLabel(f"Spent: ${item['spent']:.2f}")
        spent_label.setObjectName("negativeLabel")

        remaining = item['remaining']
        remaining_label = QLabel(f"Remaining: ${remaining:.2f}")
        remaining_label.setObjectName("positiveLabel" if remaining >= 0 else "negativeLabel")

        amounts_row.addWidget(budget_label)
        amounts_row.addWidget(spent_label)
        amounts_row.addWidget(remaining_label)
        amounts_row.addStretch()
        layout.addLayout(amounts_row)

        # Progress bar
        if item['budget'] > 0:
            progress = QProgressBar()
            progress.setObjectName("budgetProgress")
            progress.setMinimum(0)
            progress.setMaximum(100)
            pct = min(int(item['percentage']), 100)
            progress.setValue(pct)
            progress.setTextVisible(False)
            progress.setFixedHeight(8)
            if item.get('over_budget'):
                progress.setObjectName("budgetProgressOver")
            layout.addWidget(progress)

        return element

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        if self._current_data:
            self.display_budgets(self._current_data)
