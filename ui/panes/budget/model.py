class BudgetModel:
    """
    Model: Handles data access and business logic calculations
    No UI code, no styling, just data and calculations
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_budget_data(self, year, month):
        """
        Get all budget-related data for display
        Returns a dict with all the data the view needs
        """
        category_spending = self._calculate_category_spending(year, month)
        budget_status = self._calculate_budget_status(category_spending)
        total_budget = self._calculate_total_budget()
        total_spent = sum(item['spent'] for item in budget_status)
        
        return {
            'budget_status': budget_status,
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_budget - total_spent,
            'total_percentage': (total_spent / total_budget * 100) if total_budget > 0 else 0,
            'over_budget': total_spent > total_budget
        }
    
    def _calculate_category_spending(self, year, month):
        """Calculate spending by category for a month (only posted transactions)"""
        data = self.data_manager.load_month_data(year, month)
        category_totals = {}
        
        for day_transactions in data.values():
            for transaction in day_transactions:
                # Skip pending transactions
                if transaction.get('status') == 'pending':
                    continue
                
                category = transaction.get('category', 'Uncategorized')
                amount = float(transaction.get('amount', 0))
                if amount < 0:  # Only count expenses
                    category_totals[category] = category_totals.get(category, 0) + abs(amount)
        
        return category_totals
    
    def _calculate_budget_status(self, category_spending):
        """Calculate budget vs actual for all categories"""
        budget_status = []
        
        for category in self.data_manager.categories:
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
    
    def _calculate_total_budget(self):
        """Calculate total monthly budget"""
        return sum(
            cat.get('budget', 0.0) 
            for cat in self.data_manager.categories 
            if not cat.get('special', False)
        )