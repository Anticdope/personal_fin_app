"""
Manage Accounts Dialog - Controller
Coordinates between Model and View for accounts, assets, and liabilities
"""
from PySide6.QtCore import Qt
from .model import AccountManagementModel
from .view import AccountManagementView


class AccountManagementController:
    """Controller: Orchestrates account, asset, and liability management"""
    
    def __init__(self, data_manager, parent=None):
        self.data_manager = data_manager
        self.model = AccountManagementModel(data_manager)
        self.view = AccountManagementView(parent)
        
        # Track currently editing items
        self.editing_account = None
        self.editing_asset = None
        self.editing_liability = None
        
        self.connect_signals()
        self.load_all_data()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        # Account signals
        self.view.account_add_btn.clicked.connect(self.on_add_account)
        self.view.account_update_btn.clicked.connect(self.on_update_account)
        self.view.account_clear_btn.clicked.connect(self.view.clear_account_form)
        self.view.edit_account_requested.connect(self.on_edit_account_requested)
        self.view.delete_account_requested.connect(self.on_delete_account_requested)
        self.view.close_account_requested.connect(self.on_close_account_requested)
        self.view.reopen_account_requested.connect(self.on_reopen_account_requested)
        
        # Connect show closed toggle directly to button
        self.view.show_closed_checkbox.toggled.connect(self.on_show_closed_toggled)
        
        # Asset signals
        self.view.asset_add_btn.clicked.connect(self.on_add_asset)
        self.view.asset_update_btn.clicked.connect(self.on_update_asset)
        self.view.asset_clear_btn.clicked.connect(self.view.clear_asset_form)
        self.view.edit_asset_requested.connect(self.on_edit_asset_requested)
        self.view.delete_asset_requested.connect(self.on_delete_asset_requested)
        
        # Liability signals
        self.view.liability_add_btn.clicked.connect(self.on_add_liability)
        self.view.liability_update_btn.clicked.connect(self.on_update_liability)
        self.view.liability_clear_btn.clicked.connect(self.view.clear_liability_form)
        self.view.edit_liability_requested.connect(self.on_edit_liability_requested)
        self.view.delete_liability_requested.connect(self.on_delete_liability_requested)
    
    def load_all_data(self):
        """Load accounts, assets, and liabilities"""
        self.load_accounts()
        self.load_assets()
        self.load_liabilities()
    
    # ===== ACCOUNT METHODS =====
    
    def load_accounts(self):
        """Load and display all accounts"""
        if self.view.show_closed_accounts:
            accounts = self.model.get_all_accounts()
        else:
            accounts = self.model.get_active_accounts()
        
        accounts_data = []
        for account in accounts:
            summary = self.model.get_account_summary(account['name'])
            if summary:
                accounts_data.append(summary)
        
        self.view.display_accounts(accounts_data)
    
    def on_add_account(self):
        """Handle add account button"""
        data = self.view.get_account_form_data()
        
        # Validate balance
        valid, balance_value, error_msg = self.model.validate_starting_balance(data['balance'])
        if not valid:
            self.view.show_error(error_msg)
            return
        
        # Validate debt fields for credit accounts
        interest_rate = None
        minimum_payment = None
        payment_due_day = None
        credit_limit = None
        
        if data['type'].lower() == 'credit':
            valid, interest_rate, error_msg = self.model.validate_interest_rate(data.get('interest_rate', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
            
            valid, minimum_payment, error_msg = self.model.validate_minimum_payment(data.get('minimum_payment', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
            
            valid, payment_due_day, error_msg = self.model.validate_payment_due_day(data.get('payment_due_day', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
            
            valid, credit_limit, error_msg = self.model.validate_credit_limit(data.get('credit_limit', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
        
        # Add account
        success, message = self.model.add_account(
            data['name'],
            data['type'],
            balance_value,
            interest_rate,
            minimum_payment,
            payment_due_day,
            credit_limit
        )
        
        if success:
            self.view.show_success(message)
            self.load_accounts()
            self.view.clear_account_form()
        else:
            self.view.show_error(message)
    
    def on_edit_account_requested(self, account_data):
        """Handle edit request from account card"""
        self.editing_account = account_data
        self.view.set_account_form_data(account_data)
        self.view.tab_widget.setCurrentIndex(0)  # Switch to accounts tab
    
    def on_update_account(self):
        """Handle update account button"""
        if not self.editing_account:
            self.view.show_error("No account selected")
            return
        
        old_name = self.editing_account['name']
        
        # Get form data
        data = self.view.get_account_form_data()
        
        # Validate balance
        valid, balance_value, error_msg = self.model.validate_starting_balance(data['balance'])
        if not valid:
            self.view.show_error(error_msg)
            return
        
        # Validate debt fields for credit accounts
        interest_rate = None
        minimum_payment = None
        payment_due_day = None
        credit_limit = None
        
        if data['type'].lower() == 'credit':
            valid, interest_rate, error_msg = self.model.validate_interest_rate(data.get('interest_rate', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
            
            valid, minimum_payment, error_msg = self.model.validate_minimum_payment(data.get('minimum_payment', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
            
            valid, payment_due_day, error_msg = self.model.validate_payment_due_day(data.get('payment_due_day', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
            
            valid, credit_limit, error_msg = self.model.validate_credit_limit(data.get('credit_limit', ''))
            if not valid:
                self.view.show_error(error_msg)
                return
        
        # Update account
        success, message = self.model.update_account(
            old_name,
            data['name'],
            data['type'],
            balance_value,
            interest_rate,
            minimum_payment,
            payment_due_day,
            credit_limit
        )
        
        if success:
            self.view.show_success(message)
            self.editing_account = None
            self.load_accounts()
            self.view.clear_account_form()
        else:
            self.view.show_error(message)
    
    def on_delete_account_requested(self, account_data):
        """Handle delete request from account card"""
        account_name = account_data['name']
        
        if not self.view.confirm_delete("account", account_name):
            return
        
        success, message = self.model.delete_account(account_name)
        
        if success:
            self.view.show_success(message)
            self.load_accounts()
        else:
            self.view.show_error(message)
    
    def on_close_account_requested(self, account_data):
        """Handle close account request"""
        account_name = account_data['name']
        
        if not self.view.confirm_close(account_name):
            return
        
        success, message = self.model.close_account(account_name)
        
        if success:
            self.view.show_success(message)
            self.load_accounts()
        else:
            self.view.show_error(message)
    
    def on_reopen_account_requested(self, account_data):
        """Handle reopen account request"""
        account_name = account_data['name']
        
        success, message = self.model.reopen_account(account_name)
        
        if success:
            self.view.show_success(message)
            self.load_accounts()
        else:
            self.view.show_error(message)
    
    def on_show_closed_toggled(self, checked):
        """Handle show/hide closed accounts toggle"""
        self.view.show_closed_accounts = checked
        
        if checked:
            self.view.show_closed_checkbox.setText("Hide Closed Accounts")
        else:
            self.view.show_closed_checkbox.setText("Show Closed Accounts")
        
        self.load_accounts()
    
    # ===== ASSET METHODS =====
    
    def load_assets(self):
        """Load and display all assets"""
        assets = self.data_manager.assets
        self.view.display_assets(assets)
    
    def on_add_asset(self):
        """Handle add asset button"""
        data = self.view.get_asset_form_data()
        
        if not data['name']:
            self.view.show_error("Asset name is required")
            return
        
        try:
            value = float(data['value']) if data['value'] else 0.0
        except ValueError:
            self.view.show_error("Invalid value amount")
            return
        
        new_asset = {
            'name': data['name'],
            'value': value,
            'original_value': value
        }
        
        self.data_manager.asset_repo.add(new_asset)
        self.data_manager.assets = self.data_manager.asset_repo.get_all()
        
        self.view.show_success("Asset added successfully")
        self.load_assets()
        self.view.clear_asset_form()
    
    def on_edit_asset_requested(self, asset):
        """Handle edit request from asset card"""
        self.editing_asset = asset
        self.view.set_asset_form_data(asset)
        self.view.tab_widget.setCurrentIndex(1)  # Switch to assets tab
    
    def on_update_asset(self):
        """Handle update asset button"""
        if not self.editing_asset:
            self.view.show_error("No asset selected")
            return
        
        data = self.view.get_asset_form_data()
        
        if not data['name']:
            self.view.show_error("Asset name is required")
            return
        
        try:
            value = float(data['value']) if data['value'] else 0.0
        except ValueError:
            self.view.show_error("Invalid value amount")
            return
        
        old_asset = self.editing_asset
        new_asset = {
            'name': data['name'],
            'value': value,
            'original_value': old_asset.get('original_value', value)
        }
        
        success = self.data_manager.update_asset(old_asset, new_asset)
        
        if success:
            self.view.show_success("Asset updated successfully")
            self.editing_asset = None
            self.load_assets()
            self.view.clear_asset_form()
        else:
            self.view.show_error("Failed to update asset")
    
    def on_delete_asset_requested(self, asset):
        """Handle delete request from asset card"""
        if not self.view.confirm_delete("asset", asset['name']):
            return
        
        self.data_manager.delete_asset(asset)
        self.view.show_success("Asset deleted successfully")
        self.load_assets()
    
    # ===== LIABILITY METHODS =====
    
    def load_liabilities(self):
        """Load and display all liabilities"""
        liabilities = self.data_manager.liabilities
        self.view.display_liabilities(liabilities)
    
    def on_add_liability(self):
        """Handle add liability button"""
        data = self.view.get_liability_form_data()
        
        if not data['name']:
            self.view.show_error("Liability name is required")
            return
        
        try:
            balance = float(data['balance']) if data['balance'] else 0.0
        except ValueError:
            self.view.show_error("Invalid balance amount")
            return
        
        try:
            interest_rate = float(data['interest_rate']) if data['interest_rate'] else 0.0
            if interest_rate < 0:
                self.view.show_error("Interest rate cannot be negative")
                return
        except ValueError:
            self.view.show_error("Invalid interest rate")
            return
        
        try:
            minimum_payment = float(data['minimum_payment']) if data['minimum_payment'] else 0.0
            if minimum_payment < 0:
                self.view.show_error("Minimum payment cannot be negative")
                return
        except ValueError:
            self.view.show_error("Invalid minimum payment amount")
            return
        
        valid, payment_due_day, error_msg = self.model.validate_payment_due_day(data.get('payment_due_day', ''))
        if not valid:
            self.view.show_error(error_msg)
            return
        
        new_liability = {
            'name': data['name'],
            'balance': balance,
            'original_balance': balance,
            'interest_rate': interest_rate,
            'minimum_payment': minimum_payment,
            'payment_due_day': payment_due_day
        }
        
        self.data_manager.liability_repo.add(new_liability)
        self.data_manager.liabilities = self.data_manager.liability_repo.get_all()
        
        self.view.show_success("Liability added successfully")
        self.load_liabilities()
        self.view.clear_liability_form()
    
    def on_edit_liability_requested(self, liability):
        """Handle edit request from liability card"""
        self.editing_liability = liability
        self.view.set_liability_form_data(liability)
        self.view.tab_widget.setCurrentIndex(2)  # Switch to liabilities tab
    
    def on_update_liability(self):
        """Handle update liability button"""
        if not self.editing_liability:
            self.view.show_error("No liability selected")
            return
        
        old_name = self.editing_liability['name']
        data = self.view.get_liability_form_data()
        
        if not data['name']:
            self.view.show_error("Liability name is required")
            return
        
        try:
            balance = float(data['balance']) if data['balance'] else 0.0
        except ValueError:
            self.view.show_error("Invalid balance amount")
            return
        
        try:
            interest_rate = float(data['interest_rate']) if data['interest_rate'] else 0.0
        except ValueError:
            self.view.show_error("Invalid interest rate")
            return
        
        try:
            minimum_payment = float(data['minimum_payment']) if data['minimum_payment'] else 0.0
        except ValueError:
            self.view.show_error("Invalid minimum payment amount")
            return
        
        old_liability = self.editing_liability
        new_liability = {
            'name': data['name'],
            'balance': balance,
            'original_balance': old_liability.get('original_balance', balance),
            'interest_rate': interest_rate,
            'minimum_payment': minimum_payment,
            'payment_due_day': old_liability.get('payment_due_day')
        }
        
        success = self.data_manager.update_liability(old_liability, new_liability)
        
        if success:
            self.view.show_success("Liability updated successfully")
            self.editing_liability = None
            self.load_liabilities()
            self.view.clear_liability_form()
        else:
            self.view.show_error("Failed to update liability")
    
    def on_delete_liability_requested(self, liability):
        """Handle delete request from liability card"""
        if not self.view.confirm_delete("liability", liability['name']):
            return
        
        self.data_manager.delete_liability(liability)
        self.view.show_success("Liability deleted successfully")
        self.load_liabilities()
    
    def exec(self):
        """Show the dialog"""
        return self.view.exec()
    
    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)
