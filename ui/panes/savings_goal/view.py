"""
Savings Goals Pane - View
Pure UI for displaying savings goals progress
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QProgressBar, QScrollArea)
from PySide6.QtCore import Qt


class SavingsGoalsView(QWidget):
    """View: Pure UI for savings goals tracking"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Savings Goals")
        title.setObjectName("paneTitle")
        layout.addWidget(title)
        
        # Month label
        self.month_label = QLabel()
        self.month_label.setObjectName("subtitle")
        layout.addWidget(self.month_label)
        
        # Total summary
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
        
        # Individual goals (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.goals_container = QWidget()
        self.goals_layout = QVBoxLayout(self.goals_container)
        self.goals_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.goals_container)
        layout.addWidget(scroll)
    
    def set_month(self, year, month):
        """Set the displayed month"""
        from datetime import datetime
        month_name = datetime(year, month, 1).strftime('%B %Y')
        self.month_label.setText(month_name)
    
    def display_total_summary(self, summary):
        """Display total savings summary"""
        total_goal = summary['total_goal']
        total_saved = summary['total_saved']
        percentage = summary['percentage']
        
        self.total_label.setText(
            f"Total: ${total_saved:,.2f} of ${total_goal:,.2f} saved"
        )
        self.total_progress.setValue(int(percentage))
        self.total_progress.setFormat(f"{percentage:.1f}%")
    
    def display_goals(self, goals_data):
        """Display individual savings goals"""
        # Clear existing
        while self.goals_layout.count():
            child = self.goals_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not goals_data:
            no_goals = QLabel("No savings goals set.\nAdd goals in Manage Categories.")
            no_goals.setObjectName("mutedLabel")
            no_goals.setAlignment(Qt.AlignCenter)
            self.goals_layout.addWidget(no_goals)
            return
        
        for goal in goals_data:
            card = self.create_goal_card(goal)
            self.goals_layout.addWidget(card)
    
    def create_goal_card(self, goal):
        """Create a card widget for a savings goal"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        # Header with color indicator and name
        header = QHBoxLayout()
        
        color_indicator = QLabel("●")
        color_indicator.setStyleSheet(f"color: {goal['color']}; font-size: 40px;")
        
        name_label = QLabel(goal['name'])
        name_label.setObjectName("subtitle")
        
        header.addWidget(color_indicator)
        header.addWidget(name_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Goal amount
        goal_amount = QLabel(f"Goal: ${goal['goal']:,.2f}/month")
        goal_amount.setObjectName("mutedLabel")
        layout.addWidget(goal_amount)
        
        # Saved amount
        saved = goal['saved']
        saved_label = QLabel(f"Saved: ${saved:,.2f}")
        if saved >= goal['goal']:
            saved_label.setObjectName("positiveLabel")
        else:
            saved_label.setObjectName("mutedLabel")
        layout.addWidget(saved_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(int(goal['percentage']))
        progress.setFormat(f"{goal['percentage']:.1f}%")
        
        # Color progress bar based on achievement
        if goal['percentage'] >= 100:
            progress.setObjectName("successProgress")
        elif goal['percentage'] >= 75:
            progress.setObjectName("warningProgress")
        else:
            progress.setObjectName("normalProgress")
        
        layout.addWidget(progress)
        
        # Remaining amount
        remaining = goal['remaining']
        if remaining > 0:
            remaining_label = QLabel(f"${remaining:,.2f} remaining")
            remaining_label.setObjectName("mutedLabel")
            layout.addWidget(remaining_label)
        else:
            achieved_label = QLabel("✓ Goal achieved!")
            achieved_label.setObjectName("positiveLabel")
            layout.addWidget(achieved_label)
        
        return frame
    
    def set_dark_mode(self, enabled):
        """Update theme"""
        self.dark_mode = enabled