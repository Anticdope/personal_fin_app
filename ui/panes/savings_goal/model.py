"""
Savings Goals Pane - Model
Handles savings goals data and calculations
"""


class SavingsGoalsModel:
    """Model: Business logic for savings goals tracking"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_savings_categories(self):
        """Get only savings type categories"""
        return [
            cat for cat in self.data_manager.categories 
            if cat.get('type') == 'savings' and not cat.get('special', False)
        ]
    
    def get_savings_progress(self, year, month):
        """
        Calculate progress toward savings goals for the current month
        Returns list of dicts with category, goal, saved, and percentage
        """
        savings_categories = self.get_savings_categories()
        progress_data = []
        
        # Get month data
        month_data = self.data_manager.load_month_data(year, month)
        
        for category in savings_categories:
            cat_name = category['name']
            goal = category.get('budget', 0)  # "budget" field stores the goal
            
            # Calculate total saved in this category for the month
            saved = 0.0
            for day_transactions in month_data.values():
                for transaction in day_transactions:
                    if (transaction.get('category') == cat_name and 
                        transaction.get('status') != 'pending'):
                        saved += float(transaction.get('amount', 0))
            
            # Calculate percentage
            percentage = (saved / goal * 100) if goal > 0 else 0
            
            progress_data.append({
                'name': cat_name,
                'color': category.get('color', '#808080'),
                'goal': goal,
                'saved': saved,
                'percentage': percentage,
                'remaining': goal - saved
            })
        
        return progress_data
    
    def get_total_savings_summary(self, year, month):
        """
        Get summary of all savings goals
        Returns dict with total_goal, total_saved, and percentage
        """
        progress_data = self.get_savings_progress(year, month)
        
        total_goal = sum(item['goal'] for item in progress_data)
        total_saved = sum(item['saved'] for item in progress_data)
        percentage = (total_saved / total_goal * 100) if total_goal > 0 else 0
        
        return {
            'total_goal': total_goal,
            'total_saved': total_saved,
            'percentage': percentage,
            'remaining': total_goal - total_saved
        }