"""
Account Balance View - Pure UI for account balance display
Clean version with no inline styles
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt


class AccountBalanceView(QWidget):
    """View: Pure UI for displaying account balances"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Scrollable accounts container
        accounts_scroll = QScrollArea()
        accounts_scroll.setWidgetResizable(True)
        accounts_scroll.setFixedHeight(400)
        
        self.accounts_container = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_container)
        self.accounts_layout.setSpacing(10)
        self.accounts_layout.setAlignment(Qt.AlignTop)
        
        accounts_scroll.setWidget(self.accounts_container)
        layout.addWidget(accounts_scroll)
    
    def display_accounts(self, accounts_data):
        """Display list of accounts"""
        self._current_data = accounts_data
        self._clear_accounts()
        
        for account in accounts_data:
            acc_element = QFrame()
            acc_element.setObjectName("cardFrame")
            acc_layout = QHBoxLayout(acc_element)
            
            name_label = QLabel(account['name'])
            name_label.setObjectName("sectionTitle")
            
            type_label = QLabel(f"({account['type'].title()})")
            type_label.setObjectName("mutedLabel")
            
            balance = account['balance']
            balance_label = QLabel(f"${balance:.2f}")
            # Dynamic color: credit is always red (debt), debit based on value
            if account['is_credit'] or balance < 0:
                balance_label.setObjectName("negativeLabel")
            else:
                balance_label.setObjectName("positiveLabel")
            
            acc_layout.addWidget(name_label)
            acc_layout.addWidget(type_label)
            acc_layout.addStretch()
            acc_layout.addWidget(balance_label)
            
            self.accounts_layout.addWidget(acc_element)
    
    def _clear_accounts(self):
        """Remove all account widgets"""
        while self.accounts_layout.count():
            child = self.accounts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_dark_mode(self, dark_mode):
        """Update theme"""
        self.dark_mode = dark_mode
        if hasattr(self, '_current_data'):
            self.display_accounts(self._current_data)