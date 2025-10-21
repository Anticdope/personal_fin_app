"""
Deleted Items Manager - Wrapper for backward compatibility
Wraps the new repository + service architecture
Provides the same interface that existing dialogs expect
"""


class DeletedItemsManager:
    """
    Wrapper: Provides backward-compatible interface
    Delegates to repository and service
    """
    
    def __init__(self, deleted_items_repo, deleted_items_service):
        self.repo = deleted_items_repo
        self.service = deleted_items_service
    
    # ===== ARCHIVE METHODS (Delegate to Repository) =====
    
    def archive_category(self, category):
        """Archive a deleted category"""
        self.repo.add_category(category)
    
    def archive_account(self, account):
        """Archive a deleted account"""
        self.repo.add_account(account)
    
    def archive_transaction(self, date, transaction):
        """Archive a deleted transaction"""
        self.repo.add_transaction(date, transaction)
    
    def archive_asset(self, asset):
        """Archive a deleted asset"""
        self.repo.add_asset(asset)
    
    def archive_liability(self, liability):
        """Archive a deleted liability"""
        self.repo.add_liability(liability)
    
    # ===== RETRIEVAL METHODS (Delegate to Repository) =====
    
    def get_deleted_items(self):
        """Get all deleted items"""
        return self.repo.get_all()
    
    # ===== RESTORATION METHODS (Delegate to Service) =====
    
    def restore_category(self, index):
        """Restore a deleted category"""
        return self.service.restore_category(index)
    
    def restore_account(self, index):
        """Restore a deleted account"""
        return self.service.restore_account(index)
    
    def restore_transaction(self, index):
        """Restore a deleted transaction"""
        return self.service.restore_transaction(index)
    
    def restore_asset(self, index):
        """Restore a deleted asset"""
        return self.service.restore_asset(index)
    
    def restore_liability(self, index):
        """Restore a deleted liability"""
        return self.service.restore_liability(index)
    
    # ===== PERMANENT DELETE METHODS (Delegate to Service) =====
    
    def permanently_delete_category(self, index):
        """Permanently delete a category"""
        return self.service.permanently_delete_category(index)
    
    def permanently_delete_account(self, index):
        """Permanently delete an account"""
        return self.service.permanently_delete_account(index)
    
    def permanently_delete_transaction(self, index):
        """Permanently delete a transaction"""
        return self.service.permanently_delete_transaction(index)
    
    def permanently_delete_asset(self, index):
        """Permanently delete an asset"""
        return self.service.permanently_delete_asset(index)
    
    def permanently_delete_liability(self, index):
        """Permanently delete a liability"""
        return self.service.permanently_delete_liability(index)