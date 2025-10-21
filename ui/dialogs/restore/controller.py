"""
Restore Dialog - Controller
Coordinates between Model and View for restoring deleted items
"""
from PySide6.QtCore import Qt
from .model import RestoreModel
from .view import RestoreView


class RestoreController:
    """Controller: Orchestrates restore operations"""
    
    def __init__(self, data_manager, parent=None):
        self.model = RestoreModel(data_manager)
        self.view = RestoreView(parent)
        self.restore_occurred = False  # Track if any restore happened
        
        self.connect_signals()
        self.load_deleted_items()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        self.view.restore_requested.connect(self.on_restore_requested)
        self.view.permanently_delete_requested.connect(self.on_permanently_delete_requested)
    
    def load_deleted_items(self):
        """Load and display all deleted items"""
        deleted_items = self.model.get_deleted_items()
        self.view.display_deleted_items(deleted_items)
    
    def on_restore_requested(self, item_type, index):
        """Handle restore request"""
        # Route to appropriate restore method
        if item_type == 'category':
            success, message = self.model.restore_category(index)
        elif item_type == 'account':
            success, message = self.model.restore_account(index)
        elif item_type == 'transaction':
            success, message = self.model.restore_transaction(index)
        elif item_type == 'asset':
            success, message = self.model.restore_asset(index)
        elif item_type == 'liability':
            success, message = self.model.restore_liability(index)
        else:
            success = False
            message = f"Unknown item type: {item_type}"
        
        if success:
            self.view.show_success(message)
            self.load_deleted_items()  # Refresh the list
            
            # FIXED: Set result to trigger parent refresh
            self.restore_occurred = True
        else:
            self.view.show_error(message)
    
    def on_permanently_delete_requested(self, item_type, index):
        """Handle permanent delete request"""
        # Get item name for confirmation
        deleted_items = self.model.get_deleted_items()
        
        item_name = "this item"
        if item_type == 'category' and index < len(deleted_items.get('categories', [])):
            item_name = deleted_items['categories'][index]['item'].get('name', 'Unknown')
        elif item_type == 'account' and index < len(deleted_items.get('accounts', [])):
            item_name = deleted_items['accounts'][index]['item'].get('name', 'Unknown')
        elif item_type == 'transaction' and index < len(deleted_items.get('transactions', [])):
            item_name = deleted_items['transactions'][index]['item'].get('title', 'Unknown')
        elif item_type == 'asset' and index < len(deleted_items.get('assets', [])):
            item_name = deleted_items['assets'][index]['item'].get('name', 'Unknown')
        elif item_type == 'liability' and index < len(deleted_items.get('liabilities', [])):
            item_name = deleted_items['liabilities'][index]['item'].get('name', 'Unknown')
        
        # Confirm deletion
        if not self.view.confirm_permanent_delete(item_name):
            return
        
        # Route to appropriate delete method
        if item_type == 'category':
            success, message = self.model.permanently_delete_category(index)
        elif item_type == 'account':
            success, message = self.model.permanently_delete_account(index)
        elif item_type == 'transaction':
            success, message = self.model.permanently_delete_transaction(index)
        elif item_type == 'asset':
            success, message = self.model.permanently_delete_asset(index)
        elif item_type == 'liability':
            success, message = self.model.permanently_delete_liability(index)
        else:
            success = False
            message = f"Unknown item type: {item_type}"
        
        if success:
            self.view.show_success(message)
            self.load_deleted_items()  # Refresh the list
        else:
            self.view.show_error(message)
    
    def exec(self):
        """Show dialog and return result"""
        result = self.view.exec()
        # Return True if restore occurred so parent knows to refresh
        return self.restore_occurred
    
    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)