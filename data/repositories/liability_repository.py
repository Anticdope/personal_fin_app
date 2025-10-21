"""
Liability Repository - Handles liability data persistence
Single Responsibility: File I/O for liabilities only
"""
import json
import uuid
from pathlib import Path


class LiabilityRepository:
    """Repository: Manages liability data persistence"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "liabilities.json"
    
    def get_all(self):
        """Load all liabilities from file"""
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                return json.load(f)
        else:
            return []
    
    def save_all(self, liabilities):
        """Save all liabilities to file"""
        with open(self.file_path, 'w') as f:
            json.dump(liabilities, f, indent=2)
    
    def get_by_id(self, liability_id):
        """Get a liability by ID"""
        liabilities = self.get_all()
        for liability in liabilities:
            if liability.get('id') == liability_id:
                return liability
        return None
    
    def get_by_name(self, name):
        """Get a liability by name"""
        liabilities = self.get_all()
        for liability in liabilities:
            if liability.get('name') == name:
                return liability
        return None
    
    def add(self, liability):
        """Add a new liability"""
        liabilities = self.get_all()
        
        # Ensure ID exists
        if 'id' not in liability:
            liability['id'] = f"lib-{str(uuid.uuid4())[:8]}"
        
        # Add debt tracking fields (with defaults)
        if 'interest_rate' not in liability:
            liability['interest_rate'] = 0.0
        if 'minimum_payment' not in liability:
            liability['minimum_payment'] = 0.0
        if 'original_balance' not in liability:
            liability['original_balance'] = liability.get('balance', 0.0)
        if 'payment_due_day' not in liability:
            liability['payment_due_day'] = None  # Day of month (1-31)
        
        liabilities.append(liability)
        self.save_all(liabilities)
        return liability
    
    def update(self, old_liability, new_liability):
        """Update an existing liability"""
        liabilities = self.get_all()
        
        for i, liab in enumerate(liabilities):
            if liab == old_liability:
                # Preserve ID
                new_liability['id'] = old_liability.get('id')
                
                # Preserve original_balance if not provided
                if 'original_balance' not in new_liability:
                    new_liability['original_balance'] = old_liability.get('original_balance', old_liability.get('balance', 0.0))
                
                liabilities[i] = new_liability
                self.save_all(liabilities)
                return True
        return False
    
    def update_balance(self, liability_id, new_balance):
        """Update just the balance of a liability"""
        liabilities = self.get_all()
        
        for liability in liabilities:
            if liability.get('id') == liability_id:
                liability['balance'] = new_balance
                self.save_all(liabilities)
                return True
        return False
    
    def delete(self, liability):
        """Delete a liability"""
        liabilities = self.get_all()
        liabilities.remove(liability)
        self.save_all(liabilities)