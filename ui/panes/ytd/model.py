"""
YTD (Year-to-Date) Model - Handles data and calculations
"""

class YTDModel:
    """Model: Business logic for year-to-date calculations"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_ytd_data(self, year, month):
        """
        Calculate year-to-date income, expenses, and net
        Only includes posted transactions (not pending)
        
        Returns dict with income, expenses, and net
        """
        ytd_income = 0.0
        ytd_expenses = 0.0
        
        # Loop through all months up to current month
        for m in range(1, month + 1):
            month_data = self.data_manager.load_month_data(year, m)
            
            for day_transactions in month_data.values():
                for transaction in day_transactions:
                    # Skip pending transactions - only count posted
                    if transaction.get('status') == 'pending':
                        continue
                    
                    amount = float(transaction.get('amount', 0))
                    
                    # Positive amounts are income
                    if amount > 0:
                        ytd_income += amount
                    # Negative amounts are expenses
                    else:
                        ytd_expenses += abs(amount)
        
        # Calculate net
        ytd_net = ytd_income - ytd_expenses
        
        return {
            'year': year,
            'income': ytd_income,
            'expenses': ytd_expenses,
            'net': ytd_net
        }