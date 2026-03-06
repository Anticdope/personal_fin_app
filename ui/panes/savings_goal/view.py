"""
ui/panes/savings_goal/view.py

Savings Goals Pane View.
Updated: DraggableCardContainer for individual goal cards.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QProgressBar)
from PySide6.QtCore import Qt
from ui.shared.draggable_card_container import DraggableCardContainer


class SavingsGoalsView(QWidget):
    """View: Pure UI for savings goals tracking"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Savings Goals")
        title.setObjectName("paneTitle")
        layout.addWidget(title)

        self.month_label = QLabel()
        self.month_label.setObjectName("subtitle")
        layout.addWidget(self.month_label)

        # Total summary (not draggable — always at top)
        summary_frame = QFrame()
        summary_frame.setObjectName("cardFrame")
        summary_layout = QVBoxLayout(summary_frame)

        self.total_label = QLabel()
        self.total_label.setObjectName("subtitle")

        self.total_progress = QProgressBar()
        self.total_progress.setObjectName("totalProgress")
        self.total_progress.setMinimum(0)
        self.total_progress.setMaximum(100)
        self.total_progress.setTextVisible(True)

        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.total_progress)
        layout.addWidget(summary_frame)

        # Individual goal cards
        self.card_container = DraggableCardContainer()
        layout.addWidget(self.card_container)

    def set_month(self, year, month):
        from datetime import datetime
        month_name = datetime(year, month, 1).strftime('%B %Y')
        self.month_label.setText(month_name)

    def display_total_summary(self, summary):
        self.total_label.setText(
            f"Total: ${summary['total_saved']:,.2f} of ${summary['total_goal']:,.2f} saved"
        )
        self.total_progress.setValue(int(summary['percentage']))
        self.total_progress.setFormat(f"{summary['percentage']:.1f}%")

    def display_goals(self, goals_data):
        self.card_container.clear_cards()

        if not goals_data:
            empty = QLabel("No savings goals set.\nAdd goals in Manage Categories.")
            empty.setObjectName("mutedLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.card_container.add_card("__empty__", empty)
            return

        for goal in goals_data:
            card = self._build_goal_card(goal)
            card_id = goal.get('id', goal['name'])
            self.card_container.add_card(card_id, card)

    def _build_goal_card(self, goal):
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)

        header = QHBoxLayout()
        color_indicator = QLabel("●")
        color_indicator.setStyleSheet(f"color: {goal['color']}; font-size: 40px;")
        name_label = QLabel(goal['name'])
        name_label.setObjectName("subtitle")
        header.addWidget(color_indicator)
        header.addWidget(name_label)
        header.addStretch()
        layout.addLayout(header)

        goal_amount = QLabel(f"Goal: ${goal['goal']:,.2f}/month")
        goal_amount.setObjectName("mutedLabel")
        layout.addWidget(goal_amount)

        saved = goal['saved']
        saved_label = QLabel(f"Saved: ${saved:,.2f}")
        saved_label.setObjectName("positiveLabel" if saved >= goal['goal'] else "mutedLabel")
        layout.addWidget(saved_label)

        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(int(goal['percentage']))
        progress.setFormat(f"{goal['percentage']:.1f}%")
        pct = goal['percentage']
        progress.setObjectName(
            "successProgress" if pct >= 100 else
            "warningProgress" if pct >= 75 else
            "normalProgress"
        )
        layout.addWidget(progress)

        remaining = goal['remaining']
        if remaining > 0:
            rem_label = QLabel(f"${remaining:,.2f} remaining")
            rem_label.setObjectName("mutedLabel")
            layout.addWidget(rem_label)
        else:
            ach_label = QLabel("✓ Goal achieved!")
            ach_label.setObjectName("positiveLabel")
            layout.addWidget(ach_label)

        return frame

    # Keep old method name for backward compat
    def create_goal_card(self, goal):
        return self._build_goal_card(goal)

    def set_dark_mode(self, enabled):
        self.dark_mode = enabled
