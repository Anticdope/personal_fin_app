"""
Asset Repository - Handles asset data persistence with validation
"""
import json
import uuid
from pathlib import Path


class AssetRepository:
    """Repository: Manages asset data persistence with validation"""
    
    def __init__(self, data_dir, validation_service=None):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "assets.json"
        self.validation_service = validation_service
    
    def get_all(self):
        """Load all assets from file"""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return []
    
    def save_all(self, assets):
        """Save all assets to file with validation"""
        # Validate all assets before saving
        if self.validation_service:
            errors_by_index = {}
            for i, asset in enumerate(assets):
                valid, errors = self.validation_service.validate_asset(asset)
                if not valid:
                    errors_by_index[i] = errors
            
            if errors_by_index:
                error_details = []
                for idx, errors in errors_by_index.items():
                    asset_name = assets[idx].get('name', f'Asset {idx}')
                    error_details.append(f"{asset_name}: {', '.join(errors)}")
                raise ValueError(f"Asset validation failed:\n" + "\n".join(error_details))
        
        with open(self.file_path, 'w') as f:
            json.dump(assets, f, indent=2)
    
    def get_by_id(self, asset_id):
        """Get an asset by ID"""
        assets = self.get_all()
        for asset in assets:
            if asset.get('id') == asset_id:
                return asset
        return None
    
    def get_by_name(self, name):
        """Get an asset by name"""
        assets = self.get_all()
        for asset in assets:
            if asset.get('name') == name:
                return asset
        return None
    
    def add(self, asset):
        """Add a new asset with validation"""
        assets = self.get_all()
        
        # Ensure ID exists
        if 'id' not in asset:
            asset['id'] = f"ast-{str(uuid.uuid4())[:8]}"
        
        # Ensure value exists
        if 'value' not in asset:
            asset['value'] = 0.0
        
        # Validate
        if self.validation_service:
            valid, errors = self.validation_service.validate_asset(asset)
            if not valid:
                raise ValueError(f"Asset validation failed: {', '.join(errors)}")
        
        assets.append(asset)
        self.save_all(assets)
        return asset
    
    def update(self, old_asset, new_asset):
        """Update an existing asset with validation"""
        assets = self.get_all()
        
        # Preserve ID
        new_asset['id'] = old_asset.get('id')
        
        # Validate
        if self.validation_service:
            valid, errors = self.validation_service.validate_asset(new_asset)
            if not valid:
                raise ValueError(f"Asset validation failed: {', '.join(errors)}")
        
        for i, asset in enumerate(assets):
            if asset == old_asset:
                assets[i] = new_asset
                self.save_all(assets)
                return True
        return False
    
    def delete(self, asset):
        """Delete an asset"""
        assets = self.get_all()
        assets.remove(asset)
        self.save_all(assets)