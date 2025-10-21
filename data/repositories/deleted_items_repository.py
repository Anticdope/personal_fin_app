"""
Deleted Items Repository - Handles deleted items persistence
Single Responsibility: File I/O for deleted items archive
"""
import json
from pathlib import Path
from datetime import datetime


class DeletedItemsRepository:
    """Repository: Manages deleted items data persistence"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "deleted_items.json"
    
    def get_all(self):
        """Load all deleted items from archive"""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return json.load(f)
        else:
            return {
                'categories': [],
                'accounts': [],
                'transactions': [],
                'assets': [],
                'liabilities': []
            }
    
    def save_all(self, deleted_items):
        """Save all deleted items to archive"""
        with open(self.file_path, 'w') as f:
            json.dump(deleted_items, f, indent=2)
    
    def add_category(self, category):
        """Archive a deleted category"""
        deleted = self.get_all()
        
        deleted['categories'].append({
            'item': category,
            'deleted_at': datetime.now().isoformat()
        })
        
        self.save_all(deleted)
    
    def add_account(self, account):
        """Archive a deleted account"""
        deleted = self.get_all()
        
        deleted['accounts'].append({
            'item': account,
            'deleted_at': datetime.now().isoformat()
        })
        
        self.save_all(deleted)
    
    def add_transaction(self, date, transaction):
        """Archive a deleted transaction"""
        deleted = self.get_all()
        
        deleted['transactions'].append({
            'item': transaction,
            'date': {
                'year': date.year(),
                'month': date.month(),
                'day': date.day()
            },
            'deleted_at': datetime.now().isoformat()
        })
        
        self.save_all(deleted)
    
    def add_asset(self, asset):
        """Archive a deleted asset"""
        deleted = self.get_all()
        
        deleted['assets'].append({
            'item': asset,
            'deleted_at': datetime.now().isoformat()
        })
        
        self.save_all(deleted)
    
    def add_liability(self, liability):
        """Archive a deleted liability"""
        deleted = self.get_all()
        
        deleted['liabilities'].append({
            'item': liability,
            'deleted_at': datetime.now().isoformat()
        })
        
        self.save_all(deleted)
    
    def remove_category(self, index):
        """Remove a category from archive (permanent delete)"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['categories']):
            deleted['categories'].pop(index)
            self.save_all(deleted)
    
    def remove_account(self, index):
        """Remove an account from archive (permanent delete)"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['accounts']):
            deleted['accounts'].pop(index)
            self.save_all(deleted)
    
    def remove_transaction(self, index):
        """Remove a transaction from archive (permanent delete)"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['transactions']):
            deleted['transactions'].pop(index)
            self.save_all(deleted)
    
    def remove_asset(self, index):
        """Remove an asset from archive (permanent delete)"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['assets']):
            deleted['assets'].pop(index)
            self.save_all(deleted)
    
    def remove_liability(self, index):
        """Remove a liability from archive (permanent delete)"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['liabilities']):
            deleted['liabilities'].pop(index)
            self.save_all(deleted)
    
    def get_category_at_index(self, index):
        """Get a deleted category by index"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['categories']):
            return deleted['categories'][index]
        return None
    
    def get_account_at_index(self, index):
        """Get a deleted account by index"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['accounts']):
            return deleted['accounts'][index]
        return None
    
    def get_transaction_at_index(self, index):
        """Get a deleted transaction by index"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['transactions']):
            return deleted['transactions'][index]
        return None
    
    def get_asset_at_index(self, index):
        """Get a deleted asset by index"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['assets']):
            return deleted['assets'][index]
        return None
    
    def get_liability_at_index(self, index):
        """Get a deleted liability by index"""
        deleted = self.get_all()
        if 0 <= index < len(deleted['liabilities']):
            return deleted['liabilities'][index]
        return None