"""
Liability Pane Model - Data access for liabilities
"""


class LiabilityModel:
    """Model: Handles liability data access"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_liabilities_data(self):
        """
        Get all liabilities with formatted data
        Returns: list of dicts with liability info
        """
        liabilities = self.data_manager.liabilities
        
        liabilities_data = []
        for liability in liabilities:
            original_balance = liability.get('original_balance', liability.get('balance', 0))
            current_balance = liability.get('balance', 0)
            
            liabilities_data.append({
                'name': liability['name'],
                'balance': current_balance,
                'original_balance': original_balance,
                'paid_off': original_balance - current_balance,
                'percent_paid': ((original_balance - current_balance) / original_balance * 100) if original_balance != 0 else 0
            })
        
        return liabilities_data