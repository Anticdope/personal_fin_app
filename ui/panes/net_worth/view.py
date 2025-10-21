"""
Net Worth View - Pure UI for net worth display
Clean version with no inline styles
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class NetWorthView(QWidget):
    """View: Pure UI for displaying net worth breakdown"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
    
    def display_net_worth(self, data):
        """
        Display net worth data
        data: dict with cash, assets, liabilities, net_worth
        """
        # Clear existing widgets
        self._clear_layout()
        
        # === ASSETS SECTION ===
        assets_title = QLabel("ASSETS")
        assets_title.setObjectName("subtitle")
        self.layout.addWidget(assets_title)
        
        # Cash
        cash_label = QLabel(f"Cash: ${data['cash']:.2f}")
        cash_label.setObjectName("positiveLabel")
        self.layout.addWidget(cash_label)
        
        # Other assets
        other_assets_label = QLabel(f"Other Assets: ${data['other_assets']:.2f}")
        other_assets_label.setObjectName("positiveLabel")
        self.layout.addWidget(other_assets_label)
        
        # Total assets
        total_assets_label = QLabel(f"Total Assets: ${data['total_assets']:.2f}")
        total_assets_label.setObjectName("positiveLabel")
        # Make it bigger
        total_assets_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(total_assets_label)
        
        self.layout.addSpacing(20)
        
        # === LIABILITIES SECTION ===
        liabilities_title = QLabel("LIABILITIES")
        liabilities_title.setObjectName("subtitle")
        self.layout.addWidget(liabilities_title)
        
        # Credit cards
        credit_label = QLabel(f"Credit Cards: ${data['credit_cards']:.2f}")
        credit_label.setObjectName("negativeLabel")
        self.layout.addWidget(credit_label)
        
        # Other liabilities
        other_liab_label = QLabel(f"Other Liabilities: ${data['other_liabilities']:.2f}")
        other_liab_label.setObjectName("negativeLabel")
        self.layout.addWidget(other_liab_label)
        
        # Total liabilities
        total_liab_label = QLabel(f"Total Liabilities: ${data['total_liabilities']:.2f}")
        total_liab_label.setObjectName("negativeLabel")
        # Make it bigger
        total_liab_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(total_liab_label)
        
        self.layout.addSpacing(20)
        
        # === NET WORTH ===
        net_worth_label = QLabel(f"NET WORTH: ${data['net_worth']:.2f}")
        net_worth_label.setObjectName("titleLabel")
        net_worth_label.setAlignment(Qt.AlignCenter)
        # Dynamic color
        if data['net_worth'] >= 0:
            net_worth_label.setStyleSheet("font-size: 20px; color: #27AE60; font-weight: bold;")
        else:
            net_worth_label.setStyleSheet("font-size: 20px; color: #E74C3C; font-weight: bold;")
        self.layout.addWidget(net_worth_label)
        
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