"""
Asset Pane Model - Data access for assets
"""


class AssetModel:
    """Model: Handles asset data access"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_assets_data(self):
        """
        Get all assets with formatted data
        Returns: list of dicts with asset info
        """
        assets = self.data_manager.assets
        
        assets_data = []
        for asset in assets:
            original_value = asset.get('original_value', asset.get('value', 0))
            current_value = asset.get('value', 0)
            
            assets_data.append({
                'name': asset['name'],
                'value': current_value,
                'original_value': original_value,
                'change': current_value - original_value,
                'change_percent': ((current_value - original_value) / original_value * 100) if original_value != 0 else 0
            })
        
        return assets_data