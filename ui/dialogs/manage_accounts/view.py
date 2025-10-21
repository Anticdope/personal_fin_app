"""
Manage Accounts Dialog - View (Enhanced with Tabs for Assets & Liabilities)
Pure UI for account, asset, and liability management
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLineEdit, QLabel, QMessageBox, QComboBox, 
                               QFrame, QScrollArea, QWidget, QTabWidget, QCheckBox)
from PySide6.QtCore import Qt, Signal


class AccountManagementView(QDialog):
    """View: Pure UI for managing accounts, assets, and liabilities"""
    
    # Signals for user actions
    add_account_requested = Signal()
    edit_account_requested = Signal(dict)
    delete_account_requested = Signal(dict)
    close_account_requested = Signal(dict)
    reopen_account_requested = Signal(dict)
    show_closed_toggled = Signal(bool)
    
    add_asset_requested = Signal()
    edit_asset_requested = Signal(dict)
    delete_asset_requested = Signal(dict)
    
    add_liability_requested = Signal()
    edit_liability_requested = Signal(dict)
    delete_liability_requested = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Accounts, Assets & Liabilities")
        self.setModal(True)
        self.resize(900, 700)
        self.dark_mode = False
        self.show_closed_accounts = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Manage Accounts, Assets & Liabilities")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.accounts_tab = self.create_accounts_tab()
        self.assets_tab = self.create_assets_tab()
        self.liabilities_tab = self.create_liabilities_tab()
        
        self.tab_widget.addTab(self.accounts_tab, "Accounts")
        self.tab_widget.addTab(self.assets_tab, "Assets")
        self.tab_widget.addTab(self.liabilities_tab, "Liabilities")
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    # ===== ACCOUNTS TAB =====
    
    def create_accounts_tab(self):
        """Create the accounts management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add account form
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        
        form_title = QLabel("Add/Edit Account")
        form_title.setObjectName("subtitle")
        form_layout.addWidget(form_title)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setObjectName("formLabel")
        self.account_name_input = QLineEdit()
        self.account_name_input.setObjectName("formInput")
        self.account_name_input.setPlaceholderText("e.g., Main Checking")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.account_name_input)
        form_layout.addLayout(name_layout)
        
        # Type dropdown
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        type_label.setObjectName("formLabel")
        self.account_type_combo = QComboBox()
        self.account_type_combo.setObjectName("formCombo")
        self.account_type_combo.addItems(["Debit", "Credit"])
        self.account_type_combo.currentTextChanged.connect(self.on_account_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.account_type_combo)
        type_layout.addStretch()
        form_layout.addLayout(type_layout)
        
        # Starting balance
        balance_layout = QHBoxLayout()
        balance_label = QLabel("Starting Balance:")
        balance_label.setObjectName("formLabel")
        self.account_balance_input = QLineEdit()
        self.account_balance_input.setObjectName("formInput")
        self.account_balance_input.setPlaceholderText("0.00")
        balance_layout.addWidget(balance_label)
        balance_layout.addWidget(self.account_balance_input)
        form_layout.addLayout(balance_layout)
        
        # Debt tracking fields (only for credit accounts)
        self.debt_fields_container = QWidget()
        debt_fields_layout = QVBoxLayout(self.debt_fields_container)
        debt_fields_layout.setContentsMargins(0, 0, 0, 0)
        
        # Interest rate
        interest_layout = QHBoxLayout()
        interest_label = QLabel("Interest Rate (%):")
        interest_label.setObjectName("formLabel")
        self.account_interest_input = QLineEdit()
        self.account_interest_input.setObjectName("formInput")
        self.account_interest_input.setPlaceholderText("e.g., 18.99")
        interest_layout.addWidget(interest_label)
        interest_layout.addWidget(self.account_interest_input)
        debt_fields_layout.addLayout(interest_layout)
        
        # Minimum payment
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Minimum Payment:")
        payment_label.setObjectName("formLabel")
        self.account_min_payment_input = QLineEdit()
        self.account_min_payment_input.setObjectName("formInput")
        self.account_min_payment_input.setPlaceholderText("e.g., 25.00")
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.account_min_payment_input)
        debt_fields_layout.addLayout(payment_layout)
        
        # Payment due day
        due_day_layout = QHBoxLayout()
        due_day_label = QLabel("Payment Due Day:")
        due_day_label.setObjectName("formLabel")
        self.account_due_day_input = QLineEdit()
        self.account_due_day_input.setObjectName("formInput")
        self.account_due_day_input.setPlaceholderText("e.g., 15 (day of month)")
        due_day_layout.addWidget(due_day_label)
        due_day_layout.addWidget(self.account_due_day_input)
        debt_fields_layout.addLayout(due_day_layout)
        
        self.debt_fields_container.setVisible(False)  # Hidden by default
        form_layout.addWidget(self.debt_fields_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.account_add_btn = QPushButton("Add Account")
        self.account_add_btn.setObjectName("primaryButton")
        self.account_update_btn = QPushButton("Update Account")
        self.account_update_btn.setObjectName("successButton")
        self.account_update_btn.setVisible(False)
        self.account_clear_btn = QPushButton("Clear")
        self.account_clear_btn.setObjectName("secondaryButton")
        
        button_layout.addWidget(self.account_add_btn)
        button_layout.addWidget(self.account_update_btn)
        button_layout.addWidget(self.account_clear_btn)
        button_layout.addStretch()
        form_layout.addLayout(button_layout)
        
        layout.addWidget(form_frame)
        
        # Show closed accounts checkbox
        self.show_closed_checkbox = QPushButton("Show Closed Accounts")
        self.show_closed_checkbox.setCheckable(True)
        self.show_closed_checkbox.setObjectName("secondaryButton")
        layout.addWidget(self.show_closed_checkbox)
        
        # Accounts list (scrollable cards)
        list_label = QLabel("Your Accounts:")
        list_label.setObjectName("sectionLabel")
        layout.addWidget(list_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.accounts_container = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_container)
        self.accounts_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.accounts_container)
        layout.addWidget(scroll)
        
        return widget
    
    def on_account_type_changed(self, account_type):
        """Show/hide debt tracking fields based on account type"""
        is_credit = account_type.lower() == "credit"
        self.debt_fields_container.setVisible(is_credit)
    
    # ===== ASSETS TAB =====
    
    def create_assets_tab(self):
        """Create the assets management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add asset form
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        
        form_title = QLabel("Add/Edit Asset")
        form_title.setObjectName("subtitle")
        form_layout.addWidget(form_title)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setObjectName("formLabel")
        self.asset_name_input = QLineEdit()
        self.asset_name_input.setObjectName("formInput")
        self.asset_name_input.setPlaceholderText("e.g., House, Car")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.asset_name_input)
        form_layout.addLayout(name_layout)
        
        # Value input
        value_layout = QHBoxLayout()
        value_label = QLabel("Current Value:")
        value_label.setObjectName("formLabel")
        self.asset_value_input = QLineEdit()
        self.asset_value_input.setObjectName("formInput")
        self.asset_value_input.setPlaceholderText("0.00")
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.asset_value_input)
        form_layout.addLayout(value_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.asset_add_btn = QPushButton("Add Asset")
        self.asset_add_btn.setObjectName("primaryButton")
        self.asset_update_btn = QPushButton("Update Asset")
        self.asset_update_btn.setObjectName("successButton")
        self.asset_update_btn.setVisible(False)
        self.asset_clear_btn = QPushButton("Clear")
        self.asset_clear_btn.setObjectName("secondaryButton")
        
        button_layout.addWidget(self.asset_add_btn)
        button_layout.addWidget(self.asset_update_btn)
        button_layout.addWidget(self.asset_clear_btn)
        button_layout.addStretch()
        form_layout.addLayout(button_layout)
        
        layout.addWidget(form_frame)
        
        # Assets list
        list_label = QLabel("Your Assets:")
        list_label.setObjectName("sectionLabel")
        layout.addWidget(list_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.assets_container = QWidget()
        self.assets_layout = QVBoxLayout(self.assets_container)
        self.assets_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.assets_container)
        layout.addWidget(scroll)
        
        return widget
    
    # ===== LIABILITIES TAB =====
    
    def create_liabilities_tab(self):
        """Create the liabilities management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add liability form
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        
        form_title = QLabel("Add/Edit Liability")
        form_title.setObjectName("subtitle")
        form_layout.addWidget(form_title)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setObjectName("formLabel")
        self.liability_name_input = QLineEdit()
        self.liability_name_input.setObjectName("formInput")
        self.liability_name_input.setPlaceholderText("e.g., Mortgage, Student Loan")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.liability_name_input)
        form_layout.addLayout(name_layout)
        
        # Balance input
        balance_layout = QHBoxLayout()
        balance_label = QLabel("Current Balance:")
        balance_label.setObjectName("formLabel")
        self.liability_balance_input = QLineEdit()
        self.liability_balance_input.setObjectName("formInput")
        self.liability_balance_input.setPlaceholderText("0.00")
        balance_layout.addWidget(balance_label)
        balance_layout.addWidget(self.liability_balance_input)
        form_layout.addLayout(balance_layout)
        
        # Interest rate
        interest_layout = QHBoxLayout()
        interest_label = QLabel("Interest Rate (%):")
        interest_label.setObjectName("formLabel")
        self.liability_interest_input = QLineEdit()
        self.liability_interest_input.setObjectName("formInput")
        self.liability_interest_input.setPlaceholderText("e.g., 3.5")
        interest_layout.addWidget(interest_label)
        interest_layout.addWidget(self.liability_interest_input)
        form_layout.addLayout(interest_layout)
        
        # Minimum payment
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Minimum Payment:")
        payment_label.setObjectName("formLabel")
        self.liability_min_payment_input = QLineEdit()
        self.liability_min_payment_input.setObjectName("formInput")
        self.liability_min_payment_input.setPlaceholderText("e.g., 500.00")
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.liability_min_payment_input)
        form_layout.addLayout(payment_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.liability_add_btn = QPushButton("Add Liability")
        self.liability_add_btn.setObjectName("primaryButton")
        self.liability_update_btn = QPushButton("Update Liability")
        self.liability_update_btn.setObjectName("successButton")
        self.liability_update_btn.setVisible(False)
        self.liability_clear_btn = QPushButton("Clear")
        self.liability_clear_btn.setObjectName("secondaryButton")
        
        button_layout.addWidget(self.liability_add_btn)
        button_layout.addWidget(self.liability_update_btn)
        button_layout.addWidget(self.liability_clear_btn)
        button_layout.addStretch()
        form_layout.addLayout(button_layout)
        
        layout.addWidget(form_frame)
        
        # Liabilities list
        list_label = QLabel("Your Liabilities:")
        list_label.setObjectName("sectionLabel")
        layout.addWidget(list_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.liabilities_container = QWidget()
        self.liabilities_layout = QVBoxLayout(self.liabilities_container)
        self.liabilities_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.liabilities_container)
        layout.addWidget(scroll)
        
        return widget
    
    # ===== DISPLAY METHODS =====
    
    def display_accounts(self, accounts_data):
        """Display accounts as cards"""
        # Clear existing
        while self.accounts_layout.count():
            child = self.accounts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not accounts_data:
            no_accounts = QLabel("No accounts yet")
            no_accounts.setObjectName("mutedLabel")
            no_accounts.setAlignment(Qt.AlignCenter)
            self.accounts_layout.addWidget(no_accounts)
            return
        
        for account_data in accounts_data:
            card = self.create_account_card(account_data)
            self.accounts_layout.addWidget(card)
    
    def create_account_card(self, account_data):
        """Create a card widget for an account"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        is_closed = account_data.get('closed', False)
        
        # Header
        header = QHBoxLayout()
        
        if is_closed:
            closed_badge = QLabel("CLOSED")
            closed_badge.setObjectName("negativeLabel")
            closed_badge.setStyleSheet("font-weight: bold; padding: 2px 8px; border-radius: 3px;")
            header.addWidget(closed_badge)
        
        name_label = QLabel(account_data['name'])
        name_label.setObjectName("subtitle")
        
        type_label = QLabel(f"({account_data['type'].upper()})")
        type_label.setObjectName("mutedLabel")
        
        header.addWidget(name_label)
        header.addWidget(type_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Balance info
        info = QHBoxLayout()
        balance = account_data['current_balance']
        balance_label = QLabel(f"Balance: ${balance:,.2f}")
        if balance >= 0:
            balance_label.setObjectName("positiveLabel")
        else:
            balance_label.setObjectName("negativeLabel")
        
        tx_count = QLabel(f"{account_data['transaction_count']} transaction(s)")
        tx_count.setObjectName("mutedLabel")
        
        info.addWidget(balance_label)
        info.addWidget(tx_count)
        info.addStretch()
        layout.addLayout(info)
        
        # Buttons
        buttons = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_account_requested.emit(account_data))
        buttons.addWidget(edit_btn)
        
        if is_closed:
            reopen_btn = QPushButton("Reopen")
            reopen_btn.setObjectName("successButton")
            reopen_btn.clicked.connect(lambda: self.reopen_account_requested.emit(account_data))
            buttons.addWidget(reopen_btn)
        else:
            if account_data['transaction_count'] > 0:
                close_btn = QPushButton("Close")
                close_btn.setObjectName("warningButton")
                close_btn.clicked.connect(lambda: self.close_account_requested.emit(account_data))
                buttons.addWidget(close_btn)
            else:
                delete_btn = QPushButton("Delete")
                delete_btn.setObjectName("dangerButton")
                delete_btn.clicked.connect(lambda: self.delete_account_requested.emit(account_data))
                buttons.addWidget(delete_btn)
        
        buttons.addStretch()
        layout.addLayout(buttons)
        
        return frame
    
    def display_assets(self, assets):
        """Display assets as cards"""
        while self.assets_layout.count():
            child = self.assets_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not assets:
            no_assets = QLabel("No assets yet")
            no_assets.setObjectName("mutedLabel")
            no_assets.setAlignment(Qt.AlignCenter)
            self.assets_layout.addWidget(no_assets)
            return
        
        for asset in assets:
            card = self.create_asset_card(asset)
            self.assets_layout.addWidget(card)
    
    def create_asset_card(self, asset):
        """Create a card widget for an asset"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        header = QHBoxLayout()
        name_label = QLabel(asset['name'])
        name_label.setObjectName("subtitle")
        header.addWidget(name_label)
        header.addStretch()
        layout.addLayout(header)
        
        info = QHBoxLayout()
        value = asset.get('value', 0)
        original_value = asset.get('original_value', value)
        
        value_label = QLabel(f"Value: ${value:,.2f}")
        value_label.setObjectName("positiveLabel")
        
        original_label = QLabel(f"Original: ${original_value:,.2f}")
        original_label.setObjectName("mutedLabel")
        
        change = value - original_value
        if change != 0:
            change_label = QLabel(f"Change: ${change:+,.2f}")
            if change >= 0:
                change_label.setObjectName("positiveLabel")
            else:
                change_label.setObjectName("negativeLabel")
            info.addWidget(change_label)
        
        info.addWidget(value_label)
        info.addWidget(original_label)
        info.addStretch()
        layout.addLayout(info)
        
        buttons = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_asset_requested.emit(asset))
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_asset_requested.emit(asset))
        
        buttons.addWidget(edit_btn)
        buttons.addWidget(delete_btn)
        buttons.addStretch()
        layout.addLayout(buttons)
        
        return frame
    
    def display_liabilities(self, liabilities):
        """Display liabilities as cards"""
        while self.liabilities_layout.count():
            child = self.liabilities_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not liabilities:
            no_liabilities = QLabel("No liabilities yet")
            no_liabilities.setObjectName("mutedLabel")
            no_liabilities.setAlignment(Qt.AlignCenter)
            self.liabilities_layout.addWidget(no_liabilities)
            return
        
        for liability in liabilities:
            card = self.create_liability_card(liability)
            self.liabilities_layout.addWidget(card)
    
    def create_liability_card(self, liability):
        """Create a card widget for a liability"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        header = QHBoxLayout()
        name_label = QLabel(liability['name'])
        name_label.setObjectName("subtitle")
        header.addWidget(name_label)
        header.addStretch()
        layout.addLayout(header)
        
        info = QHBoxLayout()
        balance = liability.get('balance', 0)
        original_balance = liability.get('original_balance', balance)
        
        balance_label = QLabel(f"Balance: ${balance:,.2f}")
        balance_label.setObjectName("negativeLabel")
        
        original_label = QLabel(f"Original: ${original_balance:,.2f}")
        original_label.setObjectName("mutedLabel")
        
        paid_off = original_balance - balance
        if paid_off > 0:
            paid_label = QLabel(f"Paid Off: ${paid_off:,.2f}")
            paid_label.setObjectName("positiveLabel")
            info.addWidget(paid_label)
        
        info.addWidget(balance_label)
        info.addWidget(original_label)
        info.addStretch()
        layout.addLayout(info)
        
        buttons = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_liability_requested.emit(liability))
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_liability_requested.emit(liability))
        
        buttons.addWidget(edit_btn)
        buttons.addWidget(delete_btn)
        buttons.addStretch()
        layout.addLayout(buttons)
        
        return frame
    
    # ===== HELPER METHODS =====
    
    def get_account_form_data(self):
        """Get current account form values"""
        data = {
            'name': self.account_name_input.text().strip(),
            'type': self.account_type_combo.currentText(),
            'balance': self.account_balance_input.text().strip()
        }
        
        # Add debt fields if credit account
        if self.account_type_combo.currentText().lower() == 'credit':
            data['interest_rate'] = self.account_interest_input.text().strip()
            data['minimum_payment'] = self.account_min_payment_input.text().strip()
            data['payment_due_day'] = self.account_due_day_input.text().strip()
        
        return data
    
    def set_account_form_data(self, account_data):
        """Populate account form"""
        self.account_name_input.setText(account_data['name'])
        self.account_type_combo.setCurrentText(account_data['type'])
        self.account_balance_input.setText(str(account_data.get('starting_balance', 0)))
        
        # Set debt fields if they exist
        if account_data.get('type', '').lower() == 'credit':
            self.account_interest_input.setText(str(account_data.get('interest_rate', '')))
            self.account_min_payment_input.setText(str(account_data.get('minimum_payment', '')))
        
        self.account_add_btn.setVisible(False)
        self.account_update_btn.setVisible(True)
    
    def clear_account_form(self):
        """Clear account form"""
        self.account_name_input.clear()
        self.account_type_combo.setCurrentIndex(0)
        self.account_balance_input.clear()
        self.account_interest_input.clear()
        self.account_min_payment_input.clear()
        
        self.account_add_btn.setVisible(True)
        self.account_update_btn.setVisible(False)
    
    def get_asset_form_data(self):
        """Get current asset form values"""
        return {
            'name': self.asset_name_input.text().strip(),
            'value': self.asset_value_input.text().strip()
        }
    
    def set_asset_form_data(self, asset):
        """Populate asset form"""
        self.asset_name_input.setText(asset['name'])
        self.asset_value_input.setText(str(asset.get('value', 0)))
        
        self.asset_add_btn.setVisible(False)
        self.asset_update_btn.setVisible(True)
    
    def clear_asset_form(self):
        """Clear asset form"""
        self.asset_name_input.clear()
        self.asset_value_input.clear()
        
        self.asset_add_btn.setVisible(True)
        self.asset_update_btn.setVisible(False)
    
    def get_liability_form_data(self):
        """Get current liability form values"""
        return {
            'name': self.liability_name_input.text().strip(),
            'balance': self.liability_balance_input.text().strip(),
            'interest_rate': self.liability_interest_input.text().strip(),
            'minimum_payment': self.liability_min_payment_input.text().strip()
        }
    
    def set_liability_form_data(self, liability):
        """Populate liability form"""
        self.liability_name_input.setText(liability['name'])
        self.liability_balance_input.setText(str(liability.get('balance', 0)))
        self.liability_interest_input.setText(str(liability.get('interest_rate', '')))
        self.liability_min_payment_input.setText(str(liability.get('minimum_payment', '')))
        
        self.liability_add_btn.setVisible(False)
        self.liability_update_btn.setVisible(True)
    
    def clear_liability_form(self):
        """Clear liability form"""
        self.liability_name_input.clear()
        self.liability_balance_input.clear()
        self.liability_interest_input.clear()
        self.liability_min_payment_input.clear()
        
        self.liability_add_btn.setVisible(True)
        self.liability_update_btn.setVisible(False)
    
    def show_error(self, message):
        """Display error message"""
        QMessageBox.warning(self, "Error", message)
    
    def show_success(self, message):
        """Display success message"""
        QMessageBox.information(self, "Success", message)
    
    def confirm_delete(self, item_type, item_name):
        """Ask user to confirm deletion"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {item_type} '{item_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def confirm_close(self, account_name):
        """Ask user to confirm closing an account"""
        reply = QMessageBox.question(
            self,
            "Confirm Close Account",
            f"Are you sure you want to close account '{account_name}'?\n\n"
            f"The account will be hidden from view but all transaction history will be preserved.\n"
            f"You can reopen it later if needed.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def on_show_closed_toggled(self, checked):
        """Handle show/hide closed accounts toggle"""
        self.show_closed_accounts = checked
        
        if checked:
            self.show_closed_checkbox.setText("Hide Closed Accounts")
        else:
            self.show_closed_checkbox.setText("Show Closed Accounts")
        
        self.show_closed_toggled.emit(checked)
    
    def set_dark_mode(self, enabled):
        """Update theme"""
        self.dark_mode = enabled