"""
Budget View - Pure UI for budget display
Clean version with no inline styles
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QProgressBar
from PySide6.QtCore import Qt


class BudgetView(QWidget):
    """View: Pure UI for displaying budget vs actual spending"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scrollable budget container
        budget_scroll = QScrollArea()
        budget_scroll.setWidgetResizable(True)
        
        self.budget_container = QWidget()
        self.budget_layout = QVBoxLayout(self.budget_container)
        self.budget_layout.setSpacing(10)
        self.budget_layout.setAlignment(Qt.AlignTop)
        
        budget_scroll.setWidget(self.budget_container)
        layout.addWidget(budget_scroll)
    
    def display_budgets(self, budget_data):
        """
        Display budget status for all categories
        budget_data: list of dicts with budget info
        """
        # Clear existing
        self._clear_budgets()
        
        if not budget_data:
            no_budget = QLabel("No budgets set")
            no_budget.setObjectName("mutedLabel")
            no_budget.setAlignment(Qt.AlignCenter)
            self.budget_layout.addWidget(no_budget)
            return
        
        for item in budget_data:
            budget_element = self.create_budget_element(item)
            self.budget_layout.addWidget(budget_element)
    
    def create_budget_element(self, item):
        """Create a widget for a single budget item"""
        element = QFrame()
        element.setObjectName("cardFrame")
        layout = QVBoxLayout(element)
        layout.setSpacing(5)
        
        # Header row: color indicator and name
        header_row = QHBoxLayout()
        
        # Color indicator (dynamic - keep inline)
        color_indicator = QLabel("●")
        color_indicator.setStyleSheet(f"color: {item['color']}; font-size: 60px;")
        
        name_label = QLabel(item['name'])
        name_label.setObjectName("subtitle")
        
        header_row.addWidget(color_indicator)
        header_row.addWidget(name_label)
        header_row.addStretch()
        
        layout.addLayout(header_row)
        
        # Budget amounts row
        amounts_row = QHBoxLayout()
        
        budget_label = QLabel(f"Budget: ${item['budget']:.2f}")
        
        spent_label = QLabel(f"Spent: ${item['spent']:.2f}")
        spent_label.setObjectName("negativeLabel")
        
        remaining = item['remaining']
        remaining_label = QLabel(f"Remaining: ${abs(remaining):.2f}")
        # Dynamic object name based on remaining
        if remaining < 0:
            remaining_label.setObjectName("negativeLabel")
        else:
            remaining_label.setObjectName("positiveLabel")
        
        amounts_row.addWidget(budget_label)
        amounts_row.addWidget(spent_label)
        amounts_row.addWidget(remaining_label)
        amounts_row.addStretch()
        
        layout.addLayout(amounts_row)
        
        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(int(item['percentage']))
        progress.setTextVisible(True)
        progress.setFormat(f"{item['percentage']:.1f}%")
        
        # Dynamic object name based on percentage
        if item['over_budget']:
            progress.setObjectName("dangerProgress")
        elif item['percentage'] > 80:
            progress.setObjectName("warningProgress")
        # else: default green
        
        layout.addWidget(progress)
        
        return element
    
    def _clear_budgets(self):
        """Remove all budget widgets"""
        while self.budget_layout.count():
            child = self.budget_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_dark_mode(self, dark_mode):
        """Update theme"""
        self.dark_mode = dark_mode