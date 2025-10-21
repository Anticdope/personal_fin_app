"""
Restore Dialog - Model
Handles deleted items data operations
"""
from PySide6.QtCore import QDate


class RestoreModel:
    """Model: Deleted items operations"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_deleted_items(self):
        """
        Get all deleted items organized by type
        Returns: dict with categories, accounts, transactions, assets, liabilities
        """
        # Get deleted items from the manager
        return self.data_manager.deleted_items_manager.get_deleted_items()
    
    def restore_category(self, index):
        """
        Restore a deleted category
        Returns: (success: bool, message: str)
        """
        try:
            success = self.data_manager.restore_category(index)
            if success:
                return True, "Category restored successfully"
            else:
                return False, "Failed to restore category"
        except Exception as e:
            return False, f"Failed to restore category: {str(e)}"
    
    def restore_account(self, index):
        """
        Restore a deleted account
        Returns: (success: bool, message: str)
        """
        try:
            success = self.data_manager.restore_account(index)
            if success:
                return True, "Account restored successfully"
            else:
                return False, "Failed to restore account"
        except Exception as e:
            return False, f"Failed to restore account: {str(e)}"
    
    def restore_transaction(self, index):
        """
        Restore a deleted transaction
        Returns: (success: bool, message: str)
        """
        try:
            success = self.data_manager.restore_transaction(index)
            if success:
                return True, "Transaction restored successfully"
            else:
                return False, "Failed to restore transaction"
        except Exception as e:
            return False, f"Failed to restore transaction: {str(e)}"
    
    def restore_asset(self, index):
        """
        Restore a deleted asset
        Returns: (success: bool, message: str)
        """
        try:
            success = self.data_manager.restore_asset(index)
            if success:
                return True, "Asset restored successfully"
            else:
                return False, "Failed to restore asset"
        except Exception as e:
            return False, f"Failed to restore asset: {str(e)}"
    
    def restore_liability(self, index):
        """
        Restore a deleted liability
        Returns: (success: bool, message: str)
        """
        try:
            success = self.data_manager.restore_liability(index)
            if success:
                return True, "Liability restored successfully"
            else:
                return False, "Failed to restore liability"
        except Exception as e:
            return False, f"Failed to restore liability: {str(e)}"
    
    def permanently_delete_category(self, index):
        """
        Permanently delete a category
        Returns: (success: bool, message: str)
        """
        try:
            self.data_manager.deleted_items_manager.permanently_delete_category(index)
            return True, "Category permanently deleted"
        except Exception as e:
            return False, f"Failed to delete category: {str(e)}"
    
    def permanently_delete_account(self, index):
        """
        Permanently delete an account
        Returns: (success: bool, message: str)
        """
        try:
            self.data_manager.deleted_items_manager.permanently_delete_account(index)
            return True, "Account permanently deleted"
        except Exception as e:
            return False, f"Failed to delete account: {str(e)}"
    
    def permanently_delete_transaction(self, index):
        """
        Permanently delete a transaction
        Returns: (success: bool, message: str)
        """
        try:
            self.data_manager.deleted_items_manager.permanently_delete_transaction(index)
            return True, "Transaction permanently deleted"
        except Exception as e:
            return False, f"Failed to delete transaction: {str(e)}"
    
    def permanently_delete_asset(self, index):
        """
        Permanently delete an asset
        Returns: (success: bool, message: str)
        """
        try:
            self.data_manager.deleted_items_manager.permanently_delete_asset(index)
            return True, "Asset permanently deleted"
        except Exception as e:
            return False, f"Failed to delete asset: {str(e)}"
    
    def permanently_delete_liability(self, index):
        """
        Permanently delete a liability
        Returns: (success: bool, message: str)
        """
        try:
            self.data_manager.deleted_items_manager.permanently_delete_liability(index)
            return True, "Liability permanently deleted"
        except Exception as e:
            return False, f"Failed to delete liability: {str(e)}"