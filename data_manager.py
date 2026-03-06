"""
Data Manager - Facade Pattern
Provides simple interface to repositories and services
Much cleaner than before - delegates to specialized classes
UPDATED: Now includes audit logging system
"""
from pathlib import Path
from PySide6.QtCore import QDate

# Import repositories
from data.repositories.category_repository import CategoryRepository
from data.repositories.account_repository import AccountRepository
from data.repositories.transaction_repository import TransactionRepository
from data.repositories.asset_repository import AssetRepository
from data.repositories.liability_repository import LiabilityRepository
from data.repositories.recurring_repository import RecurringRepository

# Import services
from data.services.transaction_service import TransactionService
from data.services.calculation_service import CalculationService
from data.services.recurring_service import RecurringService
from data.services.migration_service import MigrationService
from data.services.deleted_items_service import DeletedItemsService

# Import deleted items repository and manager
from data.repositories.deleted_items_repository import DeletedItemsRepository
from deleted_items_manager import DeletedItemsManager

# Import audit system
from data.audit.audit_repository import AuditLogRepository
from data.audit.audit_service import AuditService


class DataManager:
    """
    Facade: Provides simple interface to complex subsystems
    Coordinates repositories and services
    """
    
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize repositories (data access layer)
        self.category_repo = CategoryRepository(self.data_dir)
        self.account_repo = AccountRepository(self.data_dir)
        self.transaction_repo = TransactionRepository(self.data_dir)
        self.asset_repo = AssetRepository(self.data_dir)
        self.liability_repo = LiabilityRepository(self.data_dir)
        self.recurring_repo = RecurringRepository(self.data_dir)
        self.deleted_items_repo = DeletedItemsRepository(self.data_dir)
        
        # Initialize audit system
        self.audit_repo = AuditLogRepository(self.data_dir)
        self.audit_service = AuditService(self.audit_repo)
        
        # Initialize services (business logic layer)
        self.transaction_service = TransactionService(
            self.account_repo,
            self.asset_repo,
            self.liability_repo,
            self.audit_service  # Pass audit service
        )
        self.calculation_service = CalculationService(
            self.account_repo,
            self.asset_repo,
            self.liability_repo,
            self.transaction_repo,
            self.category_repo
        )
        self.recurring_service = RecurringService(
            self.recurring_repo,
            self.transaction_repo,
            self.transaction_service  # So it can apply balances when auto-posting
        )
        
        # Deleted items service
        self.deleted_items_service = DeletedItemsService(
            self.deleted_items_repo,
            self.category_repo,
            self.account_repo,
            self.transaction_repo,
            self.asset_repo,
            self.liability_repo
        )
        
        # Initialize deleted items manager (wrapper for backward compatibility)
        self.deleted_items_manager = DeletedItemsManager(
            self.deleted_items_repo,
            self.deleted_items_service
        )
        
        # Migration service
        self.migration_service = MigrationService(self.data_dir)
        
        # Load data into memory (for quick access)
        self.categories = self.category_repo.get_all()
        self.accounts = self._ensure_account_fields(self.account_repo.get_all())
        self.assets = self.asset_repo.get_all()
        self.liabilities = self.liability_repo.get_all()
        self.recurring_transactions = self.recurring_repo.get_all()
        
        # Save categories if this is first run (to create the file)
        if not (self.data_dir / "categories.json").exists():
            self.category_repo.save_all(self.categories)
    
    def _ensure_account_fields(self, accounts):
        """Ensure all accounts have required fields"""
        for account in accounts:
            if 'type' not in account:
                account['type'] = 'debit'  # Default to debit
            if 'balance' not in account:
                account['balance'] = 0.0
        return accounts
    
    # ===== CATEGORY METHODS =====
    
    def save_config(self):
        """Save configuration (for backward compatibility)"""
        # This is handled by repository now, but kept for compatibility
        pass
    
    def add_category(self, category_data):
        """Add a new category"""
        category = self.category_repo.add(category_data)
        self.categories = self.category_repo.get_all()  # Refresh
        return category
    
    def delete_category(self, category):
        """Delete a category (soft delete)"""
        self.deleted_items_manager.archive_category(category)
        self.category_repo.delete(category)
        self.categories = self.category_repo.get_all()  # Refresh

    def update_category(self, old_category, new_category):
        """Update an existing category"""
        # Preserve ID
        new_category['id'] = old_category.get('id')
        
        # Update in repository
        result = self.category_repo.update(old_category, new_category)
        
        # Refresh in memory
        self.categories = self.category_repo.get_all()
        
        return result
    
    def get_category_id(self, category_name):
        """Get category ID by name"""
        category = next((c for c in self.categories if c['name'] == category_name), None)
        return category['id'] if category else None
    
    # ===== ACCOUNT METHODS =====
    
    def add_account(self, account_data):
        """Add a new account"""
        # Ensure required fields exist
        if 'type' not in account_data:
            account_data['type'] = 'debit'  # Default to debit
        
        account = self.account_repo.add(account_data)
        self.accounts = self._ensure_account_fields(self.account_repo.get_all())  # Refresh
        return account
    
    def update_account(self, old_account, new_account):
        """Update an account"""
        result = self.account_repo.update(old_account, new_account)
        self.accounts = self._ensure_account_fields(self.account_repo.get_all())  # Refresh
        return result
    
    def delete_account(self, account):
        """Delete an account (soft delete)"""
        self.deleted_items_manager.archive_account(account)
        self.account_repo.delete(account)
        self.accounts = self._ensure_account_fields(self.account_repo.get_all())  # Refresh
    
    def get_account_id(self, account_name):
        """Get account ID by name"""
        account = next((a for a in self.accounts if a['name'] == account_name), None)
        return account['id'] if account else None
    
    # ===== ASSET METHODS =====
    
    def add_asset(self, asset_data):
        """Add a new asset"""
        asset = self.asset_repo.add(asset_data)
        self.assets = self.asset_repo.get_all()  # Refresh
        return asset
    
    def update_asset(self, old_asset, new_asset):
        """Update an asset"""
        result = self.asset_repo.update(old_asset, new_asset)
        self.assets = self.asset_repo.get_all()  # Refresh
        return result
    
    def delete_asset(self, asset):
        """Delete an asset (soft delete)"""
        self.deleted_items_manager.archive_asset(asset)
        self.asset_repo.delete(asset)
        self.assets = self.asset_repo.get_all()  # Refresh
    
    # ===== LIABILITY METHODS =====
    
    def add_liability(self, liability_data):
        """Add a new liability"""
        liability = self.liability_repo.add(liability_data)
        self.liabilities = self.liability_repo.get_all()  # Refresh
        return liability
    
    def update_liability(self, old_liability, new_liability):
        """Update a liability"""
        result = self.liability_repo.update(old_liability, new_liability)
        self.liabilities = self.liability_repo.get_all()  # Refresh
        return result
    
    def delete_liability(self, liability):
        """Delete a liability (soft delete)"""
        self.deleted_items_manager.archive_liability(liability)
        self.liability_repo.delete(liability)
        self.liabilities = self.liability_repo.get_all()  # Refresh
    
    # ===== TRANSACTION METHODS =====
    
    def load_month_data(self, year, month):
        """Load transaction data for a month"""
        return self.transaction_repo.get_month_data(year, month)
    
    def save_month_data(self, year, month, data):
        """Save transaction data for a month"""
        self.transaction_repo.save_month_data(year, month, data)
    
    def get_day_transactions(self, date):
        """Get all transactions for a specific day"""
        return self.transaction_repo.get_day_transactions(
            date.year(), date.month(), date.day()
        )
    
    def add_transaction(self, date, transaction):
        """Add a transaction to a specific date"""
        year, month, day = date.year(), date.month(), date.day()
        
        # Ensure IDs are set
        if 'category' in transaction and 'category_id' not in transaction:
            transaction['category_id'] = self.get_category_id(transaction['category'])
        if 'account' in transaction and 'account_id' not in transaction:
            transaction['account_id'] = self.get_account_id(transaction['account'])
        
        # Add to repository
        self.transaction_repo.add_transaction(year, month, day, transaction)
        
        # Update account balances - FIXED: singular method name
        self.transaction_service.apply_transaction_to_balance(transaction)
        
        # Refresh accounts in memory
        self.accounts = self.account_repo.get_all()
        self.liabilities = self.liability_repo.get_all()
    
    def update_transaction(self, date, old_transaction, new_transaction):
        """Update an existing transaction"""
        year, month, day = date.year(), date.month(), date.day()
        
        # Reverse old transaction's effect - FIXED: singular method name
        self.transaction_service.reverse_transaction_from_balance(old_transaction)
        
        # Update in repository
        self.transaction_repo.update_transaction(year, month, day, old_transaction, new_transaction)
        
        # Apply new transaction's effect - FIXED: singular method name
        self.transaction_service.apply_transaction_to_balance(new_transaction)
        
        # Refresh accounts in memory
        self.accounts = self.account_repo.get_all()
        self.liabilities = self.liability_repo.get_all()
    
    def delete_transaction(self, date, transaction):
        """Delete a transaction (soft delete)"""
        year, month, day = date.year(), date.month(), date.day()
        
        # Archive before deleting
        self.deleted_items_manager.archive_transaction(date, transaction)
        
        # Remove from repository
        self.transaction_repo.delete_transaction(year, month, day, transaction)
        
        # Reverse transaction's effect on balances - FIXED: singular method name
        self.transaction_service.reverse_transaction_from_balance(transaction)
        
        # Refresh accounts in memory
        self.accounts = self.account_repo.get_all()
        self.liabilities = self.liability_repo.get_all()
    
    # ===== RECURRING TRANSACTION METHODS =====
    
    def save_recurring(self):
        """Save recurring transactions (for backward compatibility)"""
        self.recurring_repo.save_all(self.recurring_transactions)
    
    def add_recurring_transaction(self, recurring_data):
        """Add a new recurring transaction pattern"""
        # Add to repository
        recurring_data = self.recurring_repo.add(recurring_data)
        
        # Generate pending transactions
        self.recurring_service.generate_pending_transactions(recurring_data)
        
        # Refresh in memory
        self.recurring_transactions = self.recurring_repo.get_all()
        
        return recurring_data
    
    def update_recurring_transaction(self, old_recurring, new_recurring):
        """Update a recurring transaction pattern"""
        result = self.recurring_repo.update(old_recurring, new_recurring)
        self.recurring_transactions = self.recurring_repo.get_all()  # Refresh
        return result
    
    def delete_recurring_transaction(self, recurring):
        """Delete a recurring transaction pattern"""
        self.recurring_repo.delete(recurring)
        self.recurring_transactions = self.recurring_repo.get_all()  # Refresh
    
    def auto_post_due_transactions(self):
        """Auto-post any recurring transactions that are due"""
        posted_count = self.recurring_service.auto_post_due_transactions()
        
        # Refresh accounts in memory if any transactions were posted
        if posted_count > 0:
            self.accounts = self.account_repo.get_all()
            self.liabilities = self.liability_repo.get_all()
        
        return posted_count
    
    # ===== CALCULATION METHODS =====
    
    def get_net_worth(self):
        """Get current net worth"""
        return self.calculation_service.calculate_net_worth()
    
    def get_account_balance(self, account_name):
        """Get balance for a specific account"""
        return self.calculation_service.get_account_balance(account_name)
    
    def get_month_summary(self, year, month):
        """Get summary for a specific month"""
        return self.calculation_service.calculate_month_summary(year, month)
    
    def get_category_totals(self, year, month):
        """Get totals by category for a month"""
        return self.calculation_service.calculate_category_totals(year, month)
    
    def get_day_totals_separate(self, date):
        """Get pending and posted totals separately for a day"""
        return self.calculation_service.calculate_day_totals_separate(
            date.year(), date.month(), date.day()
        )
    
    # ===== AUDIT METHODS =====
    
    def get_account_audit_history(self, account_id, limit=50):
        """Get audit history for an account"""
        return self.audit_service.get_account_history(account_id, limit)
    
    def get_balance_history(self, account_id, limit=50):
        """Get balance change history for an account"""
        return self.audit_service.get_balance_history(account_id, limit)
    
    def recalculate_account_balance(self, account_id, starting_balance):
        """Recalculate account balance from audit log"""
        return self.audit_service.recalculate_account_balance(account_id, starting_balance)
    
    def get_month_audit_log(self, year, month):
        """Get all audit entries for a specific month"""
        return self.audit_service.get_all_changes_for_month(year, month)
    
    # ===== RESTORE METHODS =====
    
    def get_deleted_items(self):
        """Get all deleted items"""
        return self.deleted_items_manager.get_deleted_items()
    
    def restore_transaction(self, index):
        """Restore a deleted transaction by index"""
        # Get all deleted items
        deleted_items = self.deleted_items_manager.get_deleted_items()
        
        # Get the specific transaction from the transactions list
        if 'transactions' not in deleted_items or index >= len(deleted_items['transactions']):
            return False
        
        deleted_item = deleted_items['transactions'][index]
        
        # Restore it through the manager (this adds it back to the repository)
        success = self.deleted_items_manager.restore_transaction(index)
        
        if success:
            # Get the transaction data
            transaction = deleted_item['item']
            
            # Re-apply transaction to balances
            self.transaction_service.apply_transaction_to_balance(transaction)
            
            # Refresh accounts in memory
            self.accounts = self._ensure_account_fields(self.account_repo.get_all())
            self.liabilities = self.liability_repo.get_all()
        
        return success
    
    def restore_account(self, index):
        """Restore a deleted account by index"""
        success = self.deleted_items_manager.restore_account(index)
        if success:
            self.accounts = self._ensure_account_fields(self.account_repo.get_all())
        return success
    
    def restore_category(self, index):
        """Restore a deleted category by index"""
        success = self.deleted_items_manager.restore_category(index)
        if success:
            self.categories = self.category_repo.get_all()
        return success
    
    def restore_asset(self, index):
        """Restore a deleted asset by index"""
        success = self.deleted_items_manager.restore_asset(index)
        if success:
            self.assets = self.asset_repo.get_all()
        return success
    
    def restore_liability(self, index):
        """Restore a deleted liability by index"""
        success = self.deleted_items_manager.restore_liability(index)
        if success:
            self.liabilities = self.liability_repo.get_all()
        return success
    
    def permanently_delete_item(self, item_type, deleted_item):
        """Permanently delete an item from the deleted items list"""
        self.deleted_items_manager.permanently_delete(item_type, deleted_item)