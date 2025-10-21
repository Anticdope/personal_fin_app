"""
Transaction Dialog - Model
Handles transaction data validation and business logic
"""


class TransactionModel:
    """Model: Transaction data validation and business logic"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_categories(self):
        """Get all categories with their types (excluding special)"""
        all_cats = []
        for cat in self.data_manager.categories:
            cat_type = cat.get('type', 'expense')
            # Skip special type categories (Transfer, Debt Payment)
            # These are handled separately in the UI
            if cat_type != 'special':
                all_cats.append({
                    'name': cat['name'],
                    'type': cat_type
                })
        return all_cats
    
    def get_accounts(self):
        """Get all account names"""
        return [acc['name'] for acc in self.data_manager.accounts]
    
    def get_liabilities(self):
        """Get all liabilities AND credit accounts (for debt payment)"""
        payoff_targets = []
        
        # Add actual liabilities
        payoff_targets.extend(self.data_manager.liabilities)
        
        # Add credit accounts (credit cards can be paid off)
        credit_accounts = [
            {'name': acc['name'], 'type': 'credit'} 
            for acc in self.data_manager.accounts 
            if acc.get('type') == 'credit'
        ]
        payoff_targets.extend(credit_accounts)
        
        return payoff_targets
    
    def get_day_transactions(self, date):
        """Get all transactions for a specific day"""
        data = self.data_manager.load_month_data(date.year(), date.month())
        day_key = str(date.day())
        return data.get(day_key, [])
    
    def validate_transaction(self, title, amount, category, account, recurring=False, frequency=None, start_date=None):
        """
        Validate transaction data
        Returns: (valid: bool, errors: dict)
        """
        errors = {}
        
        if not title or not title.strip():
            errors['title'] = "Title is required"
        
        if not amount or amount.strip() == '':
            errors['amount'] = "Amount is required"
        else:
            try:
                float(amount)
            except ValueError:
                errors['amount'] = "Invalid amount"
        
        if not category:
            errors['category'] = "Category is required"
        
        if not account:
            errors['account'] = "Account is required"
        
        # Validate recurring fields
        if recurring:
            if not start_date or start_date.strip() == '':
                errors['start_date'] = "Start date is required for recurring transactions"
            else:
                try:
                    from datetime import datetime
                    datetime.strptime(start_date, '%Y-%m-%d')
                except ValueError:
                    errors['start_date'] = "Invalid date format (use YYYY-MM-DD)"
        
        return len(errors) == 0, errors
    
    def format_transaction_data(self, title, amount, category, account):
        """
        Format transaction data for storage (regular transaction)
        Returns: dict
        """
        return {
            'title': title.strip(),
            'amount': float(amount),
            'category': category,
            'account': account,
            'status': 'posted'
        }
    
    def format_recurring_pattern(self, title, amount, category, account, frequency, start_date, end_date=None):
        """
        Format recurring transaction pattern
        Returns: dict
        """
        pattern = {
            'title': title.strip(),
            'amount': float(amount),
            'category': category,
            'account': account,
            'frequency': frequency,
            'start_date': start_date
        }
        
        if end_date and end_date.strip():
            pattern['end_date'] = end_date.strip()
        
        return pattern
    
    def add_transaction(self, date, transaction_data):
        """Add a transaction to the data manager"""
        self.data_manager.add_transaction(date, transaction_data)
    
    def update_transaction(self, date, old_transaction, new_transaction):
        """Update a transaction in the data manager"""
        self.data_manager.update_transaction(date, old_transaction, new_transaction)
    
    def delete_transaction(self, date, transaction_data):
        """Delete a transaction from the data manager"""
        self.data_manager.delete_transaction(date, transaction_data)
    
    def post_transaction(self, date, transaction):
        """Mark a pending transaction as posted"""
        transaction['status'] = 'posted'
        self.update_transaction(date, transaction, transaction)
    
    def calculate_day_summary(self, transactions):
        """
        Calculate summary totals for the day
        Returns: dict with pending, posted, and net totals
        """
        pending_total = sum(
            float(t.get('amount', 0)) 
            for t in transactions 
            if t.get('status') == 'pending'
        )
        posted_total = sum(
            float(t.get('amount', 0)) 
            for t in transactions 
            if t.get('status') != 'pending'
        )
        
        return {
            'pending': pending_total,
            'posted': posted_total,
            'net': pending_total + posted_total
        }