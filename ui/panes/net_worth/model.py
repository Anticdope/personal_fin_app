"""
Net Worth Model - Handles data and calculations
"""

class NetWorthModel:
    """Model: Business logic for net worth calculations"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_net_worth_data(self):
        """
        Calculate and return all net worth data
        Returns dict with assets, liabilities, and net worth
        Excludes closed accounts from calculations
        """
        # Calculate total cash assets (debit accounts) - exclude closed accounts
        total_cash = sum(
            acc.get('balance', 0.0) 
            for acc in self.data_manager.accounts 
            if acc['type'].lower() == 'debit' and not acc.get('closed', False)
        )
        
        # Calculate total other assets
        total_assets = sum(
            asset.get('value', 0.0) 
            for asset in self.data_manager.assets
        )
        
        # Calculate total credit card debt - exclude closed accounts
        total_credit = sum(
            acc.get('balance', 0.0) 
            for acc in self.data_manager.accounts 
            if acc['type'].lower() == 'credit' and not acc.get('closed', False)
        )
        
        # Calculate total other liabilities
        total_liabilities = sum(
            liab.get('balance', 0.0) 
            for liab in self.data_manager.liabilities
        )
        
        # Calculate totals
        total_asset_value = total_cash + total_assets
        total_liability_value = total_credit + total_liabilities
        net_worth = total_asset_value - total_liability_value
        
        return {
            'cash': total_cash,
            'other_assets': total_assets,
            'total_assets': total_asset_value,
            'credit_cards': total_credit,
            'other_liabilities': total_liabilities,
            'total_liabilities': total_liability_value,
            'net_worth': net_worth
        }