"""
Recurring Transaction Repository - Handles recurring transaction data persistence
Single Responsibility: File I/O for recurring transactions only
"""
import json
import uuid
from pathlib import Path


class RecurringRepository:
    """Repository: Manages recurring transaction data persistence"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "recurring_transactions.json"
    
    def get_all(self):
        """Load all recurring transactions from file"""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return json.load(f)
        else:
            return []
    
    def save_all(self, recurring_transactions):
        """Save all recurring transactions to file"""
        with open(self.file_path, 'w') as f:
            json.dump(recurring_transactions, f, indent=2)
    
    def get_by_id(self, recurring_id):
        """Get a recurring transaction by ID"""
        recurring_transactions = self.get_all()
        for recurring in recurring_transactions:
            if recurring.get('id') == recurring_id:
                return recurring
        return None
    
    def add(self, recurring_data):
        """Add a new recurring transaction"""
        recurring_transactions = self.get_all()
        
        # Ensure ID exists
        if 'id' not in recurring_data:
            recurring_data['id'] = str(uuid.uuid4())
        
        recurring_transactions.append(recurring_data)
        self.save_all(recurring_transactions)
        return recurring_data
    
    def update(self, recurring_id, new_data):
        """Update an existing recurring transaction"""
        recurring_transactions = self.get_all()
        
        for i, recurring in enumerate(recurring_transactions):
            if recurring.get('id') == recurring_id:
                new_data['id'] = recurring_id  # Preserve ID
                recurring_transactions[i] = new_data
                self.save_all(recurring_transactions)
                return True
        return False
    
    def delete(self, recurring_id):
        """Delete a recurring transaction"""
        recurring_transactions = self.get_all()
        recurring_transactions = [
            r for r in recurring_transactions 
            if r.get('id') != recurring_id
        ]
        self.save_all(recurring_transactions)