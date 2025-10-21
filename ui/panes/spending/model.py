"""
Spending Model - Handles data and calculations
"""

class SpendingModel:
    """Model: Business logic for category spending calculations"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_spending_data(self, year, month):
        """
        Get spending by category for a specific month
        Only includes posted transactions (not pending)
        
        Returns dict with category spending and colors
        """
        # Get category spending from data manager
        category_spending = self._calculate_category_spending(year, month)
        
        # Build data structure with colors
        spending_data = []
        
        for category, amount in category_spending.items():
            # Find category color
            color = "#95A5A6"  # Default gray
            for cat in self.data_manager.categories:
                if cat['name'] == category:
                    color = cat['color']
                    break
            
            spending_data.append({
                'category': category,
                'amount': amount,
                'color': color
            })
        
        # Sort by amount (largest first)
        spending_data.sort(key=lambda x: x['amount'], reverse=True)
        
        return spending_data
    
    def _calculate_category_spending(self, year, month):
        """
        Calculate spending by category for a month
        Only counts posted transactions (not pending)
        """
        data = self.data_manager.load_month_data(year, month)
        category_totals = {}
        
        for day_transactions in data.values():
            for transaction in day_transactions:
                # Skip pending transactions - only count posted
                if transaction.get('status') == 'pending':
                    continue
                
                category = transaction.get('category', 'Uncategorized')
                amount = float(transaction.get('amount', 0))
                
                # Only count expenses (negative amounts)
                if amount < 0:
                    category_totals[category] = category_totals.get(category, 0) + abs(amount)
        
        return category_totals