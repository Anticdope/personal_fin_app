"""
YTD View - Pure UI for year-to-date display
Clean version with no inline styles
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class YTDView(QWidget):
    """View: Pure UI for displaying year-to-date summary"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
    
    def display_ytd(self, data):
        """
        Display year-to-date data
        data: dict with year, income, expenses, net
        """
        # Clear existing widgets
        self._clear_layout()
        
        # Title
        title = QLabel(f"Year-to-Date Summary ({data['year']})")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)
        
        # === INCOME ===
        income_label = QLabel("INCOME")
        income_label.setObjectName("subtitle")
        self.layout.addWidget(income_label)
        
        income_value = QLabel(f"${data['income']:.2f}")
        income_value.setObjectName("positiveLabel")
        income_value.setStyleSheet("font-size: 24px;")
        income_value.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(income_value)
        
        self.layout.addSpacing(10)
        
        # === EXPENSES ===
        expenses_label = QLabel("EXPENSES")
        expenses_label.setObjectName("subtitle")
        self.layout.addWidget(expenses_label)
        
        expenses_value = QLabel(f"${data['expenses']:.2f}")
        expenses_value.setObjectName("negativeLabel")
        expenses_value.setStyleSheet("font-size: 24px;")
        expenses_value.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(expenses_value)
        
        self.layout.addSpacing(10)
        
        # === NET ===
        net_label = QLabel("NET")
        net_label.setObjectName("subtitle")
        self.layout.addWidget(net_label)
        
        net_value = QLabel(f"${data['net']:.2f}")
        net_value.setAlignment(Qt.AlignCenter)
        # Dynamic color and size
        if data['net'] >= 0:
            net_value.setStyleSheet("font-size: 28px; font-weight: bold; color: #27AE60;")
        else:
            net_value.setStyleSheet("font-size: 28px; font-weight: bold; color: #E74C3C;")
        self.layout.addWidget(net_value)
        
        self.layout.addStretch()
    
    def _clear_layout(self):
        """Remove all widgets from layout"""
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_dark_mode(self, dark_mode):
        """Update theme"""
        self.dark_mode = dark_mode