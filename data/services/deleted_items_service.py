"""
Deleted Items Service - Handles restoration business logic
Single Responsibility: Restoration operations and validation
"""
from PySide6.QtCore import QDate


class DeletedItemsService:
    """Service: Handles deleted items restoration logic"""
    
    def __init__(self, deleted_repo, category_repo, account_repo, transaction_repo, 
                 asset_repo, liability_repo):
        self.deleted_repo = deleted_repo
        self.category_repo = category_repo
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.asset_repo = asset_repo
        self.liability_repo = liability_repo
    
    def restore_category(self, index):
        """
        Restore a deleted category
        Returns: (success: bool, message: str)
        """
        archived = self.deleted_repo.get_category_at_index(index)
        if not archived:
            return False, "Category not found in archive"
        
        category = archived['item']
        
        # Check if category with same name already exists
        existing = self.category_repo.get_by_name(category['name'])
        if existing:
            return False, f"Category '{category['name']}' already exists"
        
        # Restore category
        self.category_repo.add(category)
        
        # Remove from archive
        self.deleted_repo.remove_category(index)
        
        return True, f"Category '{category['name']}' restored successfully"
    
    def restore_account(self, index):
        """
        Restore a deleted account
        Returns: (success: bool, message: str)
        """
        archived = self.deleted_repo.get_account_at_index(index)
        if not archived:
            return False, "Account not found in archive"
        
        account = archived['item']
        
        # Check if account with same name already exists
        existing = self.account_repo.get_by_name(account['name'])
        if existing:
            return False, f"Account '{account['name']}' already exists"
        
        # Restore account
        self.account_repo.add(account)
        
        # Remove from archive
        self.deleted_repo.remove_account(index)
        
        return True, f"Account '{account['name']}' restored successfully"
    
    def restore_transaction(self, index):
        """
        Restore a deleted transaction
        Returns: (success: bool, message: str)
        """
        archived = self.deleted_repo.get_transaction_at_index(index)
        if not archived:
            return False, "Transaction not found in archive"
        
        transaction = archived['item']
        date_info = archived['date']
        
        # Restore transaction
        year = date_info['year']
        month = date_info['month']
        day = date_info['day']
        
        self.transaction_repo.add_transaction(year, month, day, transaction)
        
        # Remove from archive
        self.deleted_repo.remove_transaction(index)
        
        return True, f"Transaction '{transaction.get('title', 'Untitled')}' restored successfully"
    
    def restore_asset(self, index):
        """
        Restore a deleted asset
        Returns: (success: bool, message: str)
        """
        archived = self.deleted_repo.get_asset_at_index(index)
        if not archived:
            return False, "Asset not found in archive"
        
        asset = archived['item']
        
        # Check if asset with same name already exists
        existing_assets = self.asset_repo.get_all()
        if any(a['name'] == asset['name'] for a in existing_assets):
            return False, f"Asset '{asset['name']}' already exists"
        
        # Restore asset
        self.asset_repo.add(asset)
        
        # Remove from archive
        self.deleted_repo.remove_asset(index)
        
        return True, f"Asset '{asset['name']}' restored successfully"
    
    def restore_liability(self, index):
        """
        Restore a deleted liability
        Returns: (success: bool, message: str)
        """
        archived = self.deleted_repo.get_liability_at_index(index)
        if not archived:
            return False, "Liability not found in archive"
        
        liability = archived['item']
        
        # Check if liability with same name already exists
        existing_liabilities = self.liability_repo.get_all()
        if any(l['name'] == liability['name'] for l in existing_liabilities):
            return False, f"Liability '{liability['name']}' already exists"
        
        # Restore liability
        self.liability_repo.add(liability)
        
        # Remove from archive
        self.deleted_repo.remove_liability(index)
        
        return True, f"Liability '{liability['name']}' restored successfully"
    
    def permanently_delete_category(self, index):
        """Permanently delete a category from archive"""
        self.deleted_repo.remove_category(index)
        return True, "Category permanently deleted"
    
    def permanently_delete_account(self, index):
        """Permanently delete an account from archive"""
        self.deleted_repo.remove_account(index)
        return True, "Account permanently deleted"
    
    def permanently_delete_transaction(self, index):
        """Permanently delete a transaction from archive"""
        self.deleted_repo.remove_transaction(index)
        return True, "Transaction permanently deleted"
    
    def permanently_delete_asset(self, index):
        """Permanently delete an asset from archive"""
        self.deleted_repo.remove_asset(index)
        return True, "Asset permanently deleted"
    
    def permanently_delete_liability(self, index):
        """Permanently delete a liability from archive"""
        self.deleted_repo.remove_liability(index)
        return True, "Liability permanently deleted"
    
    def get_all_deleted_items(self):
        """Get all deleted items from archive"""
        return self.deleted_repo.get_all()