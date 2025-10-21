"""
Validation Service
Centralized validation for all data operations
"""
from typing import Dict, Any, List, Tuple
from .schemas import (
    CategorySchema, AccountSchema, AssetSchema, LiabilitySchema,
    TransactionSchema, RecurringTransactionSchema, ValidationError
)


class ValidationService:
    """Service: Validates all data before persistence"""
    
    def __init__(self, category_repo, account_repo, asset_repo, liability_repo):
        """Initialize with repositories for referential integrity checks"""
        self.category_repo = category_repo
        self.account_repo = account_repo
        self.asset_repo = asset_repo
        self.liability_repo = liability_repo
    
    # ===== SCHEMA VALIDATION =====
    
    def validate_category(self, data: Dict[str, Any], raise_on_error: bool = False) -> Tuple[bool, List[str]]:
        """Validate category data against schema"""
        valid, errors = CategorySchema.validate(data)
        if not valid and raise_on_error:
            raise ValidationError(f"Category validation failed: {', '.join(errors)}")
        return valid, errors
    
    def validate_account(self, data: Dict[str, Any], raise_on_error: bool = False) -> Tuple[bool, List[str]]:
        """Validate account data against schema"""
        valid, errors = AccountSchema.validate(data)
        if not valid and raise_on_error:
            raise ValidationError(f"Account validation failed: {', '.join(errors)}")
        return valid, errors
    
    def validate_asset(self, data: Dict[str, Any], raise_on_error: bool = False) -> Tuple[bool, List[str]]:
        """Validate asset data against schema"""
        valid, errors = AssetSchema.validate(data)
        if not valid and raise_on_error:
            raise ValidationError(f"Asset validation failed: {', '.join(errors)}")
        return valid, errors
    
    def validate_liability(self, data: Dict[str, Any], raise_on_error: bool = False) -> Tuple[bool, List[str]]:
        """Validate liability data against schema"""
        valid, errors = LiabilitySchema.validate(data)
        if not valid and raise_on_error:
            raise ValidationError(f"Liability validation failed: {', '.join(errors)}")
        return valid, errors
    
    def validate_transaction(self, data: Dict[str, Any], raise_on_error: bool = False) -> Tuple[bool, List[str]]:
        """Validate transaction data against schema"""
        valid, errors = TransactionSchema.validate(data)
        if not valid and raise_on_error:
            raise ValidationError(f"Transaction validation failed: {', '.join(errors)}")
        return valid, errors
    
    def validate_recurring_transaction(self, data: Dict[str, Any], raise_on_error: bool = False) -> Tuple[bool, List[str]]:
        """Validate recurring transaction pattern against schema"""
        valid, errors = RecurringTransactionSchema.validate(data)
        if not valid and raise_on_error:
            raise ValidationError(f"Recurring transaction validation failed: {', '.join(errors)}")
        return valid, errors
    
    # ===== REFERENTIAL INTEGRITY CHECKS =====
    
    def check_category_exists(self, category_name: str) -> bool:
        """Check if a category exists"""
        categories = self.category_repo.get_all()
        return any(cat['name'] == category_name for cat in categories)
    
    def check_account_exists(self, account_name: str) -> bool:
        """Check if an account exists"""
        accounts = self.account_repo.get_all()
        return any(acc['name'] == account_name for acc in accounts)
    
    def check_asset_exists(self, asset_name: str) -> bool:
        """Check if an asset exists"""
        assets = self.asset_repo.get_all()
        return any(asset['name'] == asset_name for asset in assets)
    
    def check_liability_exists(self, liability_name: str) -> bool:
        """Check if a liability exists"""
        liabilities = self.liability_repo.get_all()
        return any(lib['name'] == liability_name for lib in liabilities)
    
    def validate_transaction_references(self, transaction: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that all referenced entities exist
        Returns: (valid: bool, errors: List[str])
        """
        errors = []
        category = transaction.get('category', '')
        
        # Check category exists
        if not self.check_category_exists(category):
            # Special categories don't need to be in the database
            if category not in ['Transfer', 'Debt Payment']:
                errors.append(f"Category '{category}' does not exist")
        
        # Check account references based on transaction type
        if category == 'Transfer':
            from_account = transaction.get('from_account')
            to_account = transaction.get('to_account')
            
            if from_account and not self.check_account_exists(from_account):
                errors.append(f"From account '{from_account}' does not exist")
            
            if to_account and not self.check_account_exists(to_account):
                errors.append(f"To account '{to_account}' does not exist")
        
        elif category == 'Debt Payment':
            from_account = transaction.get('from_account')
            liability = transaction.get('liability')
            
            if from_account and not self.check_account_exists(from_account):
                errors.append(f"From account '{from_account}' does not exist")
            
            # Liability could be either a liability or a credit account
            if liability:
                if not self.check_liability_exists(liability) and not self.check_account_exists(liability):
                    errors.append(f"Liability/Credit account '{liability}' does not exist")
        
        else:
            # Regular transaction
            account = transaction.get('account')
            if account and not self.check_account_exists(account):
                errors.append(f"Account '{account}' does not exist")
        
        return len(errors) == 0, errors
    
    # ===== BATCH VALIDATION =====
    
    def validate_categories_batch(self, categories: List[Dict[str, Any]]) -> Tuple[bool, Dict[int, List[str]]]:
        """
        Validate a batch of categories
        Returns: (all_valid: bool, errors_by_index: Dict[int, List[str]])
        """
        errors_by_index = {}
        
        for i, category in enumerate(categories):
            valid, errors = self.validate_category(category)
            if not valid:
                errors_by_index[i] = errors
        
        return len(errors_by_index) == 0, errors_by_index
    
    def validate_accounts_batch(self, accounts: List[Dict[str, Any]]) -> Tuple[bool, Dict[int, List[str]]]:
        """
        Validate a batch of accounts
        Returns: (all_valid: bool, errors_by_index: Dict[int, List[str]])
        """
        errors_by_index = {}
        
        for i, account in enumerate(accounts):
            valid, errors = self.validate_account(account)
            if not valid:
                errors_by_index[i] = errors
        
        return len(errors_by_index) == 0, errors_by_index
    
    def validate_transactions_batch(self, transactions: List[Dict[str, Any]]) -> Tuple[bool, Dict[int, List[str]]]:
        """
        Validate a batch of transactions
        Returns: (all_valid: bool, errors_by_index: Dict[int, List[str]])
        """
        errors_by_index = {}
        
        for i, transaction in enumerate(transactions):
            # Schema validation
            valid, errors = self.validate_transaction(transaction)
            if not valid:
                errors_by_index[i] = errors
                continue
            
            # Referential integrity
            valid_refs, ref_errors = self.validate_transaction_references(transaction)
            if not valid_refs:
                errors_by_index[i] = ref_errors
        
        return len(errors_by_index) == 0, errors_by_index
    
    # ===== DATA SANITIZATION =====
    
    def sanitize_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize category data (trim strings, set defaults)"""
        sanitized = data.copy()
        sanitized['name'] = sanitized.get('name', '').strip()
        sanitized['color'] = sanitized.get('color', '#808080').strip()
        sanitized['budget'] = float(sanitized.get('budget', 0.0))
        sanitized['special'] = bool(sanitized.get('special', False))
        return sanitized
    
    def sanitize_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize account data"""
        sanitized = data.copy()
        sanitized['name'] = sanitized.get('name', '').strip()
        sanitized['balance'] = float(sanitized.get('balance', 0.0))
        if 'starting_balance' in sanitized:
            sanitized['starting_balance'] = float(sanitized['starting_balance'])
        return sanitized
    
    def sanitize_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize transaction data"""
        sanitized = data.copy()
        sanitized['title'] = sanitized.get('title', '').strip()
        sanitized['amount'] = float(sanitized.get('amount', 0.0))
        sanitized['category'] = sanitized.get('category', '').strip()
        sanitized['status'] = sanitized.get('status', 'posted')
        
        # Sanitize account fields based on transaction type
        if 'account' in sanitized:
            sanitized['account'] = sanitized['account'].strip()
        if 'from_account' in sanitized:
            sanitized['from_account'] = sanitized['from_account'].strip()
        if 'to_account' in sanitized:
            sanitized['to_account'] = sanitized['to_account'].strip()
        if 'liability' in sanitized:
            sanitized['liability'] = sanitized['liability'].strip()
        
        return sanitized
    
    def sanitize_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize asset data"""
        sanitized = data.copy()
        sanitized['name'] = sanitized.get('name', '').strip()
        sanitized['value'] = float(sanitized.get('value', 0.0))
        if 'original_value' in sanitized:
            sanitized['original_value'] = float(sanitized['original_value'])
        if 'description' in sanitized:
            sanitized['description'] = sanitized['description'].strip()
        return sanitized
    
    def sanitize_liability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize liability data"""
        sanitized = data.copy()
        sanitized['name'] = sanitized.get('name', '').strip()
        sanitized['balance'] = float(sanitized.get('balance', 0.0))
        if 'original_balance' in sanitized:
            sanitized['original_balance'] = float(sanitized['original_balance'])
        if 'interest_rate' in sanitized:
            sanitized['interest_rate'] = float(sanitized['interest_rate'])
        if 'description' in sanitized:
            sanitized['description'] = sanitized['description'].strip()
        return sanitized