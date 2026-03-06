"""
Calculation Service - Handles financial calculations
Single Responsibility: All financial calculations and aggregations
"""

class CalculationService:
    """Service: Handles financial calculations"""
    
    def __init__(self, account_repo, asset_repo, liability_repo, transaction_repo, category_repo):
        self.account_repo = account_repo
        self.asset_repo = asset_repo
        self.liability_repo = liability_repo
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
    
    def calculate_net_worth(self):
        """
        Calculate total net worth
        Returns: float (assets - liabilities)
        """
        # Assets: Debit accounts + other assets
        accounts = self.account_repo.get_all()
        total_cash = sum(
            acc.get('balance', 0.0) 
            for acc in accounts 
            if acc['type'].lower() == 'debit'
        )
        
        assets = self.asset_repo.get_all()
        total_assets = sum(asset.get('value', 0.0) for asset in assets)
        
        # Liabilities: Credit accounts + other liabilities
        total_credit = sum(
            acc.get('balance', 0.0) 
            for acc in accounts 
            if acc['type'].lower() == 'credit'
        )
        
        liabilities = self.liability_repo.get_all()
        total_liabilities = sum(liab.get('balance', 0.0) for liab in liabilities)
        
        return (total_cash + total_assets) - (total_credit + total_liabilities)
    
    def calculate_category_spending(self, year, month):
        """
        Calculate spending by category for a month
        Only counts posted transactions (not pending)
        Returns: dict {category_name: amount}
        """
        data = self.transaction_repo.get_month_data(year, month)
        category_totals = {}
        
        for day_transactions in data.values():
            for transaction in day_transactions:
                # Skip pending transactions
                if transaction.get('status') == 'pending':
                    continue
                
                category = transaction.get('category', 'Uncategorized')
                amount = float(transaction.get('amount', 0))
                
                # Only count expenses (negative amounts)
                if amount < 0:
                    category_totals[category] = category_totals.get(category, 0) + abs(amount)
        
        return category_totals
    
    def calculate_budget_status(self, year, month):
        """
        Calculate budget vs actual spending for all categories
        Returns: list of dicts with budget status info
        """
        category_spending = self.calculate_category_spending(year, month)
        budget_status = []
        
        categories = self.category_repo.get_all()
        for category in categories:
            # Skip special categories
            if category.get('special', False):
                continue
            
            name = category['name']
            budget = category.get('budget', 0.0)
            spent = category_spending.get(name, 0.0)
            
            budget_status.append({
                'name': name,
                'color': category['color'],
                'budget': budget,
                'spent': spent,
                'remaining': budget - spent,
                'percentage': (spent / budget * 100) if budget > 0 else 0,
                'over_budget': spent > budget if budget > 0 else False
            })
        
        return budget_status
    
    def calculate_total_monthly_budget(self):
        """
        Calculate total budget across all categories
        Returns: float
        """
        categories = self.category_repo.get_all()
        return sum(
            cat.get('budget', 0.0) 
            for cat in categories 
            if not cat.get('special', False)
        )
    
    def calculate_day_total(self, year, month, day):
        """
        Calculate total transactions for a specific day (excludes transfers)
        Returns: float
        """
        transactions = self.transaction_repo.get_day_transactions(year, month, day)
        
        # Exclude Transfer category from daily totals
        total = sum(
            float(t.get('amount', 0)) 
            for t in transactions 
            if t.get('category') != 'Transfer'
        )
        return total
    
    def calculate_day_totals_separate(self, year, month, day):
        """
        Get pending and posted totals separately for a day
        Returns: dict with 'pending', 'posted', 'net'
        """
        transactions = self.transaction_repo.get_day_transactions(year, month, day)
        
        pending_total = 0.0
        posted_total = 0.0
        
        for transaction in transactions:
            amount = float(transaction.get('amount', 0))
            category = transaction.get('category')
            
            # Skip transfers
            if category == 'Transfer':
                continue
            
            # Debt payments use positive amounts but represent money leaving the source account
            if category == 'Debt Payment':
                amount = -abs(amount)
            
            if transaction.get('status') == 'pending':
                pending_total += amount
            else:
                posted_total += amount
        
        return {
            'pending': pending_total,
            'posted': posted_total,
            'net': pending_total + posted_total
        }
    
    def calculate_ytd_summary(self, year, month):
        """
        Calculate year-to-date income, expenses, and net
        Only includes posted transactions
        Returns: dict with 'income', 'expenses', 'net'
        """
        ytd_income = 0.0
        ytd_expenses = 0.0
        
        # Loop through all months up to current month
        for m in range(1, month + 1):
            month_data = self.transaction_repo.get_month_data(year, m)
            
            for day_transactions in month_data.values():
                for transaction in day_transactions:
                    # Skip pending transactions
                    if transaction.get('status') == 'pending':
                        continue
                    
                    amount = float(transaction.get('amount', 0))
                    
                    if amount > 0:
                        ytd_income += amount
                    else:
                        ytd_expenses += abs(amount)
        
        return {
            'income': ytd_income,
            'expenses': ytd_expenses,
            'net': ytd_income - ytd_expenses
        }