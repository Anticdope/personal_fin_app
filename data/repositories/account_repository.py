"""
Account Repository - Handles account data persistence with validation
"""
import json
import uuid
from pathlib import Path


class AccountRepository:
    """Repository: Manages account data persistence with validation"""
    
    def __init__(self, data_dir, validation_service=None):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "accounts.json"
        self.validation_service = validation_service
    
    def get_all(self):
        """Load all accounts from file"""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return []
    
    def save_all(self, accounts):
        """Save all accounts to file with validation"""
        # Validate all accounts before saving
        if self.validation_service:
            all_valid, errors_by_index = self.validation_service.validate_accounts_batch(accounts)
            if not all_valid:
                error_details = []
                for idx, errors in errors_by_index.items():
                    account_name = accounts[idx].get('name', f'Account {idx}')
                    error_details.append(f"{account_name}: {', '.join(errors)}")
                raise ValueError(f"Account validation failed:\n" + "\n".join(error_details))
        
        with open(self.file_path, 'w') as f:
            json.dump(accounts, f, indent=2)
    
    def get_by_id(self, account_id):
        """Get an account by ID"""
        accounts = self.get_all()
        for account in accounts:
            if account.get('id') == account_id:
                return account
        return None
    
    def get_by_name(self, name):
        """Get an account by name"""
        accounts = self.get_all()
        for account in accounts:
            if account.get('name') == name:
                return account
        return None
    
    def add(self, account):
        """Add a new account with validation"""
        accounts = self.get_all()
        
        # Ensure ID exists
        if 'id' not in account:
            account['id'] = f"acc-{str(uuid.uuid4())[:8]}"
        
        # Ensure required fields with defaults
        if 'type' not in account:
            account['type'] = 'debit'
        if 'balance' not in account:
            account['balance'] = 0.0
        
        # Add debt tracking fields for credit accounts (optional, default to None/0)
        if account.get('type') == 'credit':
            if 'interest_rate' not in account:
                account['interest_rate'] = 0.0
            if 'minimum_payment' not in account:
                account['minimum_payment'] = 0.0
            if 'original_balance' not in account:
                account['original_balance'] = account.get('balance', 0.0)
            if 'payment_due_day' not in account:
                account['payment_due_day'] = None  # Day of month (1-31)
        
        # Sanitize and validate
        if self.validation_service:
            account = self.validation_service.sanitize_account(account)
            valid, errors = self.validation_service.validate_account(account)
            if not valid:
                raise ValueError(f"Account validation failed: {', '.join(errors)}")
        
        accounts.append(account)
        self.save_all(accounts)
        return account
    
    def update(self, old_account, new_account):
        """Update an existing account with validation"""
        accounts = self.get_all()
        
        # Preserve ID and type (type should not change)
        new_account['id'] = old_account.get('id')
        new_account['type'] = old_account.get('type')
        
        # Preserve original_balance if it exists and new one not provided
        if 'original_balance' in old_account and 'original_balance' not in new_account:
            new_account['original_balance'] = old_account['original_balance']
        
        # Sanitize and validate
        if self.validation_service:
            new_account = self.validation_service.sanitize_account(new_account)
            valid, errors = self.validation_service.validate_account(new_account)
            if not valid:
                raise ValueError(f"Account validation failed: {', '.join(errors)}")
        
        for i, account in enumerate(accounts):
            if account == old_account:
                accounts[i] = new_account
                self.save_all(accounts)
                return True
        return False
    
    def delete(self, account):
        """Delete an account"""
        accounts = self.get_all()
        accounts.remove(account)
        self.save_all(accounts)