"""
Transaction Repository - Handles transaction data persistence with validation
Single Responsibility: File I/O for transactions only
"""
import json
from pathlib import Path


class TransactionRepository:
    """Repository: Manages transaction data persistence with validation"""
    
    def __init__(self, data_dir, validation_service=None):
        self.data_dir = Path(data_dir)
        self.validation_service = validation_service
    
    def _get_month_file(self, year, month):
        """Get the file path for a specific month"""
        return self.data_dir / f"{year}-{month:02d}.json"
    
    def get_month_data(self, year, month):
        """Load transaction data for a month"""
        file_path = self._get_month_file(year, month)
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_month_data(self, year, month, data):
        """Save transaction data for a month with validation"""
        # Validate all transactions in the month
        if self.validation_service:
            errors_by_day = {}
            
            for day_key, transactions in data.items():
                for i, transaction in enumerate(transactions):
                    # Schema validation
                    valid, errors = self.validation_service.validate_transaction(transaction)
                    if not valid:
                        if day_key not in errors_by_day:
                            errors_by_day[day_key] = {}
                        errors_by_day[day_key][i] = errors
                        continue
                    
                    # Referential integrity
                    valid_refs, ref_errors = self.validation_service.validate_transaction_references(transaction)
                    if not valid_refs:
                        if day_key not in errors_by_day:
                            errors_by_day[day_key] = {}
                        errors_by_day[day_key][i] = ref_errors
            
            if errors_by_day:
                error_details = []
                for day, day_errors in errors_by_day.items():
                    for idx, errors in day_errors.items():
                        error_details.append(f"Day {day}, Transaction {idx}: {', '.join(errors)}")
                raise ValueError(f"Transaction validation failed:\n" + "\n".join(error_details))
        
        file_path = self._get_month_file(year, month)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_day_transactions(self, year, month, day):
        """Get all transactions for a specific day"""
        data = self.get_month_data(year, month)
        day_key = str(day)
        return data.get(day_key, [])
    
    def get_all_transactions(self, year, month):
        """Get all transactions for a month as a flat list"""
        data = self.get_month_data(year, month)
        all_transactions = []
        for day_transactions in data.values():
            all_transactions.extend(day_transactions)
        return all_transactions
    
    def add_transaction(self, year, month, day, transaction):
        """Add a transaction to a specific day with validation"""
        # Sanitize and validate
        if self.validation_service:
            transaction = self.validation_service.sanitize_transaction(transaction)
            
            # Schema validation
            valid, errors = self.validation_service.validate_transaction(transaction)
            if not valid:
                raise ValueError(f"Transaction validation failed: {', '.join(errors)}")
            
            # Referential integrity
            valid_refs, ref_errors = self.validation_service.validate_transaction_references(transaction)
            if not valid_refs:
                raise ValueError(f"Transaction reference validation failed: {', '.join(ref_errors)}")
        
        data = self.get_month_data(year, month)
        day_key = str(day)
        
        if day_key not in data:
            data[day_key] = []
        
        data[day_key].append(transaction)
        self.save_month_data(year, month, data)
    
    def update_transaction(self, year, month, day, old_transaction, new_transaction):
        """Update a transaction with validation"""
        # Sanitize and validate new transaction
        if self.validation_service:
            new_transaction = self.validation_service.sanitize_transaction(new_transaction)
            
            # Schema validation
            valid, errors = self.validation_service.validate_transaction(new_transaction)
            if not valid:
                raise ValueError(f"Transaction validation failed: {', '.join(errors)}")
            
            # Referential integrity
            valid_refs, ref_errors = self.validation_service.validate_transaction_references(new_transaction)
            if not valid_refs:
                raise ValueError(f"Transaction reference validation failed: {', '.join(ref_errors)}")
        
        data = self.get_month_data(year, month)
        day_key = str(day)
        
        if day_key in data:
            for i, transaction in enumerate(data[day_key]):
                if transaction == old_transaction:
                    data[day_key][i] = new_transaction
                    self.save_month_data(year, month, data)
                    return True
        return False
    
    def delete_transaction(self, year, month, day, transaction):
        """Delete a transaction"""
        data = self.get_month_data(year, month)
        day_key = str(day)
        
        if day_key in data:
            data[day_key].remove(transaction)
            if not data[day_key]:
                del data[day_key]
            self.save_month_data(year, month, data)