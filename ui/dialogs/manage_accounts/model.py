"""
Manage Accounts Dialog - Model
Handles all account data operations and business logic
"""


class AccountManagementModel:
    """Model: Account CRUD operations, balance calculations, and validation"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_all_accounts(self):
        """Get all accounts from data manager"""
        return self.data_manager.accounts
    
    def get_active_accounts(self):
        """Get only active (non-closed) accounts"""
        return [acc for acc in self.get_all_accounts() if not acc.get('closed', False)]
    
    def get_closed_accounts(self):
        """Get only closed accounts"""
        return [acc for acc in self.get_all_accounts() if acc.get('closed', False)]
    
    def get_account_by_name(self, name):
        """Find an account by name"""
        for account in self.get_all_accounts():
            if account['name'] == name:
                return account
        return None
    
    def get_account_by_id(self, account_id):
        """Find an account by ID"""
        return self.data_manager.get_account_by_id(account_id)
    
    def calculate_account_balance(self, account_name):
        """
        Calculate the current balance for an account across all transactions
        Returns: float
        """
        account = self.get_account_by_name(account_name)
        if not account:
            return 0.0
        return account.get('balance', 0.0)
    
    def get_account_transaction_count(self, account_name):
        """
        Count total transactions for an account
        Returns: int
        """
        count = 0
        
        for month_file in self.data_manager.data_dir.glob("*.json"):
            if month_file.name in ['categories.json', 'accounts.json', 'assets.json',
                                   'liabilities.json', 'recurring_transactions.json',
                                   'deleted_items.json', 'card_order.json']:
                continue
            
            try:
                import json
                with open(month_file, 'r') as f:
                    month_data = json.load(f)
                
                for day_transactions in month_data.values():
                    for transaction in day_transactions:
                        if not isinstance(transaction, dict):
                            continue
                        if transaction.get('account') == account_name:
                            count += 1
                        account = self.get_account_by_name(account_name)
                        if account and transaction.get('account_id') == account.get('id'):
                            count += 1
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        return count
    
    def get_account_summary(self, account_name):
        """
        Get comprehensive account information
        Returns: dict with balance, transaction count, etc.
        """
        account = self.get_account_by_name(account_name)
        if not account:
            return None
        
        summary = {
            'name': account['name'],
            'type': account['type'],
            'starting_balance': account.get('balance', 0.0),
            'current_balance': self.calculate_account_balance(account_name),
            'transaction_count': self.get_account_transaction_count(account_name),
            'closed': account.get('closed', False)
        }
        
        # Add debt fields if credit account
        if account.get('type') == 'credit':
            summary['interest_rate'] = account.get('interest_rate', 0.0)
            summary['minimum_payment'] = account.get('minimum_payment', 0.0)
            summary['original_balance'] = account.get('original_balance', account.get('balance', 0.0))
            summary['credit_limit'] = account.get('credit_limit')
        
        return summary
    
    def validate_credit_limit(self, credit_limit_str):
        """
        Validate credit limit value.
        Returns: (valid: bool, value: float or None, message: str)
        """
        if not credit_limit_str or credit_limit_str.strip() == '':
            return True, None, ""  # Optional field
        try:
            value = float(credit_limit_str)
            if value < 0:
                return False, None, "Credit limit cannot be negative"
            return True, value, ""
        except ValueError:
            return False, None, "Credit limit must be a number"
    
    def validate_starting_balance(self, balance_str):
        """
        Validate starting balance input
        Returns: (valid: bool, value: float, message: str)
        """
        if not balance_str or balance_str.strip() == '':
            return True, 0.0, ""
        
        try:
            balance = float(balance_str)
            return True, balance, ""
        except ValueError:
            return False, 0.0, "Invalid balance amount"
    
    def validate_interest_rate(self, rate_str):
        """
        Validate interest rate input
        Returns: (valid: bool, value: float, message: str)
        """
        if not rate_str or rate_str.strip() == '':
            return True, 0.0, ""
        
        try:
            rate = float(rate_str)
            if rate < 0:
                return False, 0.0, "Interest rate cannot be negative"
            if rate > 100:
                return False, 0.0, "Interest rate seems too high (>100%)"
            return True, rate, ""
        except ValueError:
            return False, 0.0, "Invalid interest rate"
    
    def validate_minimum_payment(self, payment_str):
        """
        Validate minimum payment input
        Returns: (valid: bool, value: float, message: str)
        """
        if not payment_str or payment_str.strip() == '':
            return True, 0.0, ""
        
        try:
            payment = float(payment_str)
            if payment < 0:
                return False, 0.0, "Minimum payment cannot be negative"
            return True, payment, ""
        except ValueError:
            return False, 0.0, "Invalid minimum payment amount"

    def validate_payment_due_day(self, day_str):
        """
        Validate payment due day input
        Returns: (valid: bool, value: int or None, message: str)
        """
        if not day_str or day_str.strip() == '':
            return True, None, ""
        
        try:
            day = int(day_str)
            if day < 1 or day > 31:
                return False, None, "Payment due day must be between 1 and 31"
            return True, day, ""
        except ValueError:
            return False, None, "Invalid day number"
    
    def add_account(self, name, account_type, starting_balance=0.0, interest_rate=None,
                    minimum_payment=None, payment_due_day=None, credit_limit=None):
        """
        Add a new account
        Returns: (success: bool, message: str)
        """
        account_type = account_type.lower()

        if not name or not name.strip():
            return False, "Account name cannot be empty"
        
        if self.get_account_by_name(name):
            return False, f"Account '{name}' already exists"
        
        if account_type not in ['debit', 'credit']:
            return False, "Account type must be 'debit' or 'credit'"
        
        new_account = {
            'name': name.strip(),
            'type': account_type,
            'balance': float(starting_balance) if starting_balance else 0.0,
            'closed': False
        }
        
        # Add debt tracking fields for credit accounts
        if account_type == 'credit':
            new_account['interest_rate'] = float(interest_rate) if interest_rate else 0.0
            new_account['minimum_payment'] = float(minimum_payment) if minimum_payment else 0.0
            new_account['original_balance'] = new_account['balance']
            new_account['payment_due_day'] = payment_due_day  # Already an int or None from validation
            if credit_limit is not None:
                new_account['credit_limit'] = float(credit_limit)
        
        self.data_manager.account_repo.add(new_account)
        self.data_manager.accounts = self.data_manager.account_repo.get_all()
        
        return True, "Account added successfully"

    def update_account(self, old_name, new_name, account_type, starting_balance=0.0,
                       interest_rate=None, minimum_payment=None, payment_due_day=None,
                       credit_limit=None):
        """
        Update an existing account
        Returns: (success: bool, message: str)
        """
        account_type = account_type.lower()
        
        if not new_name or not new_name.strip():
            return False, "Account name cannot be empty"
        
        if old_name != new_name:
            if self.get_account_by_name(new_name):
                return False, f"Account '{new_name}' already exists"
        
        if account_type not in ['debit', 'credit']:
            return False, "Account type must be 'debit' or 'credit'"
        
        old_account = self.get_account_by_name(old_name)
        if not old_account:
            return False, "Account not found"
        
        current_balance = old_account.get('balance', 0.0)
        if abs(starting_balance - current_balance) > 0.01:
            return False, "Balance cannot be manually edited. Account balances are calculated from transactions."
        
        new_account = {
            'name': new_name.strip(),
            'type': account_type,
            'balance': current_balance,
            'closed': old_account.get('closed', False)
        }
        
        # Handle debt tracking fields for credit accounts
        if account_type == 'credit':
            new_account['interest_rate'] = float(interest_rate) if interest_rate else old_account.get('interest_rate', 0.0)
            new_account['minimum_payment'] = float(minimum_payment) if minimum_payment else old_account.get('minimum_payment', 0.0)
            new_account['original_balance'] = old_account.get('original_balance', old_account.get('balance', 0.0))
            new_account['payment_due_day'] = payment_due_day if payment_due_day is not None else old_account.get('payment_due_day')
            new_account['credit_limit'] = float(credit_limit) if credit_limit is not None else old_account.get('credit_limit')
        
        success = self.data_manager.update_account(old_account, new_account)
        
        if success:
            return True, "Account updated successfully"
        else:
            return False, "Failed to update account"
    
    def delete_account(self, name):
        """
        Delete an account
        Returns: (success: bool, message: str)
        """
        transaction_count = self.get_account_transaction_count(name)
        if transaction_count > 0:
            return False, f"Cannot delete account with {transaction_count} transaction(s). You can close the account instead to hide it from view."
        
        account = self.get_account_by_name(name)
        if not account:
            return False, "Account not found"
        
        self.data_manager.delete_account(account)
        
        return True, "Account deleted successfully"
    
    def close_account(self, name):
        """
        Close an account (mark as inactive but keep data)
        Returns: (success: bool, message: str)
        """
        account = self.get_account_by_name(name)
        if not account:
            return False, "Account not found"
        
        if account.get('closed', False):
            return False, "Account is already closed"
        
        updated_account = account.copy()
        updated_account['closed'] = True
        
        success = self.data_manager.update_account(account, updated_account)
        
        if success:
            return True, f"Account '{name}' closed successfully"
        else:
            return False, "Failed to close account"
    
    def reopen_account(self, name):
        """
        Reopen a closed account
        Returns: (success: bool, message: str)
        """
        account = self.get_account_by_name(name)
        if not account:
            return False, "Account not found"
        
        if not account.get('closed', False):
            return False, "Account is not closed"
        
        updated_account = account.copy()
        updated_account['closed'] = False
        
        success = self.data_manager.update_account(account, updated_account)
        
        if success:
            return True, f"Account '{name}' reopened successfully"
        else:
            return False, "Failed to reopen account"
