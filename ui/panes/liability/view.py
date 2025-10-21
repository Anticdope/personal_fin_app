"""
Liability Pane View - Pure UI for displaying liabilities
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt


class LiabilityView(QWidget):
    """View: Pure UI for displaying liabilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scrollable liability container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.liability_container = QWidget()
        self.liability_layout = QVBoxLayout(self.liability_container)
        self.liability_layout.setSpacing(10)
        self.liability_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.liability_container)
        layout.addWidget(scroll)
    
    def display_liabilities(self, liabilities_data):
        """
        Display all liabilities
        liabilities_data: list of dicts with liability info
        """
        # Clear existing
        self._clear_liabilities()
        
        if not liabilities_data:
            no_liabilities = QLabel("No liabilities")
            no_liabilities.setObjectName("mutedLabel")
            no_liabilities.setAlignment(Qt.AlignCenter)
            self.liability_layout.addWidget(no_liabilities)
            return
        
        for liability in liabilities_data:
            liability_element = self.create_liability_element(liability)
            self.liability_layout.addWidget(liability_element)
    
    def create_liability_element(self, liability):
        """Create a widget for a single liability"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        # Name
        name_label = QLabel(liability['name'])
        name_label.setObjectName("subtitle")
        layout.addWidget(name_label)
        
        # Current balance
        balance_label = QLabel(f"Balance: ${liability['balance']:,.2f}")
        balance_label.setObjectName("negativeLabel")
        layout.addWidget(balance_label)
        
        # Original balance
        original_label = QLabel(f"Original: ${liability['original_balance']:,.2f}")
        original_label.setObjectName("mutedLabel")
        layout.addWidget(original_label)
        
        # Paid off amount
        paid_off = liability['paid_off']
        if paid_off > 0:
            paid_label = QLabel(f"Paid Off: ${paid_off:,.2f} ({liability['percent_paid']:.1f}%)")
            paid_label.setObjectName("positiveLabel")
            layout.addWidget(paid_label)
        
        return frame
    
    def _clear_liabilities(self):
        """Clear all liability widgets"""
        while self.liability_layout.count():
            child = self.liability_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_dark_mode(self, dark_mode):
        """Update theme for this pane"""
        self.dark_mode = dark_mode
    
    def get_widget_name(self):
        """Return pane display name"""
        return "Liabilities"