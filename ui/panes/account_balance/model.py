"""
Account Balance Model - Handles data access
"""

class AccountBalanceModel:
    """Model: Business logic for account balances"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_accounts_data(self):
        """
        Get all active (non-closed) accounts with their current balances
        Returns list of account dicts with formatted data
        """
        accounts_data = []
        
        for account in self.data_manager.accounts:
            # Skip closed accounts
            if account.get('closed', False):
                continue
                
            account_info = {
                'name': account['name'],
                'type': account['type'].title(),
                'balance': account.get('balance', 0.0),
                'is_credit': account['type'].lower() == 'credit'
            }
            accounts_data.append(account_info)
        
        return accounts_data