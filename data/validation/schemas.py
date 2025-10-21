"""
Data Validation Schemas
Defines the expected structure and validation rules for all data types
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class BaseSchema:
    """Base class for all schemas"""
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against schema
        Returns: (is_valid: bool, errors: List[str])
        """
        raise NotImplementedError


class CategorySchema(BaseSchema):
    """Schema for category validation"""
    
    REQUIRED_FIELDS = ['id', 'name', 'color', 'type']
    OPTIONAL_FIELDS = ['budget', 'special']
    VALID_TYPES = ['income', 'expense', 'savings', 'special']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate category data"""
        errors = []
        
        # Check required fields exist
        for field in CategorySchema.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate id
        if not isinstance(data['id'], str) or not data['id'].strip():
            errors.append("'id' must be a non-empty string")
        
        # Validate name
        if not isinstance(data['name'], str) or not data['name'].strip():
            errors.append("'name' must be a non-empty string")
        
        # Validate color (hex color format)
        color = data['color']
        if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
            errors.append("'color' must be a hex color code (e.g., #FF0000)")
        
        # Validate type
        if data['type'] not in CategorySchema.VALID_TYPES:
            errors.append(f"'type' must be one of: {CategorySchema.VALID_TYPES}")
        
        # Validate optional fields if present
        if 'budget' in data:
            try:
                float(data['budget'])
            except (ValueError, TypeError):
                errors.append("'budget' must be a valid number")
        
        if 'special' in data and not isinstance(data['special'], bool):
            errors.append("'special' must be a boolean")
        
        return len(errors) == 0, errors


class AccountSchema(BaseSchema):
    """Schema for account validation"""
    
    REQUIRED_FIELDS = ['id', 'name', 'type', 'balance']
    OPTIONAL_FIELDS = ['starting_balance']
    VALID_TYPES = ['debit', 'credit']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate account data"""
        errors = []
        
        # Check required fields exist
        for field in AccountSchema.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate id
        if not isinstance(data['id'], str) or not data['id'].strip():
            errors.append("'id' must be a non-empty string")
        
        # Validate name
        if not isinstance(data['name'], str) or not data['name'].strip():
            errors.append("'name' must be a non-empty string")
        
        # Validate type
        if data['type'] not in AccountSchema.VALID_TYPES:
            errors.append(f"'type' must be one of: {AccountSchema.VALID_TYPES}")
        
        # Validate balance
        try:
            float(data['balance'])
        except (ValueError, TypeError):
            errors.append("'balance' must be a valid number")
        
        # Validate optional starting_balance
        if 'starting_balance' in data:
            try:
                float(data['starting_balance'])
            except (ValueError, TypeError):
                errors.append("'starting_balance' must be a valid number")
        
        return len(errors) == 0, errors


class AssetSchema(BaseSchema):
    """Schema for asset validation"""
    
    REQUIRED_FIELDS = ['id', 'name', 'value']
    OPTIONAL_FIELDS = ['original_value', 'description']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate asset data"""
        errors = []
        
        # Check required fields exist
        for field in AssetSchema.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate id
        if not isinstance(data['id'], str) or not data['id'].strip():
            errors.append("'id' must be a non-empty string")
        
        # Validate name
        if not isinstance(data['name'], str) or not data['name'].strip():
            errors.append("'name' must be a non-empty string")
        
        # Validate value
        try:
            float(data['value'])
        except (ValueError, TypeError):
            errors.append("'value' must be a valid number")
        
        # Validate optional original_value
        if 'original_value' in data:
            try:
                float(data['original_value'])
            except (ValueError, TypeError):
                errors.append("'original_value' must be a valid number")
        
        return len(errors) == 0, errors


class LiabilitySchema(BaseSchema):
    """Schema for liability validation"""
    
    REQUIRED_FIELDS = ['id', 'name', 'balance']
    OPTIONAL_FIELDS = ['original_balance', 'description', 'interest_rate']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate liability data"""
        errors = []
        
        # Check required fields exist
        for field in LiabilitySchema.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate id
        if not isinstance(data['id'], str) or not data['id'].strip():
            errors.append("'id' must be a non-empty string")
        
        # Validate name
        if not isinstance(data['name'], str) or not data['name'].strip():
            errors.append("'name' must be a non-empty string")
        
        # Validate balance
        try:
            float(data['balance'])
        except (ValueError, TypeError):
            errors.append("'balance' must be a valid number")
        
        # Validate optional fields
        if 'original_balance' in data:
            try:
                float(data['original_balance'])
            except (ValueError, TypeError):
                errors.append("'original_balance' must be a valid number")
        
        if 'interest_rate' in data:
            try:
                rate = float(data['interest_rate'])
                if rate < 0 or rate > 100:
                    errors.append("'interest_rate' must be between 0 and 100")
            except (ValueError, TypeError):
                errors.append("'interest_rate' must be a valid number")
        
        return len(errors) == 0, errors


class TransactionSchema(BaseSchema):
    """Schema for transaction validation"""
    
    REQUIRED_FIELDS = ['title', 'amount', 'category', 'status']
    OPTIONAL_FIELDS = ['account', 'from_account', 'to_account', 'liability', 
                       'transaction_type', 'category_id', 'account_id']
    VALID_STATUSES = ['posted', 'pending']
    VALID_CATEGORIES_SPECIAL = ['Transfer', 'Debt Payment']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate transaction data"""
        errors = []
        
        # Check required fields exist
        for field in TransactionSchema.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate title
        if not isinstance(data['title'], str) or not data['title'].strip():
            errors.append("'title' must be a non-empty string")
        
        # Validate amount
        try:
            amount = float(data['amount'])
        except (ValueError, TypeError):
            errors.append("'amount' must be a valid number")
        
        # Validate category
        if not isinstance(data['category'], str) or not data['category'].strip():
            errors.append("'category' must be a non-empty string")
        
        # Validate status
        if data['status'] not in TransactionSchema.VALID_STATUSES:
            errors.append(f"'status' must be one of: {TransactionSchema.VALID_STATUSES}")
        
        # Category-specific validation
        category = data.get('category', '')
        
        if category == 'Transfer':
            # Transfer must have from_account and to_account
            if 'from_account' not in data or not data['from_account']:
                errors.append("Transfer transactions must have 'from_account'")
            if 'to_account' not in data or not data['to_account']:
                errors.append("Transfer transactions must have 'to_account'")
            if 'from_account' in data and 'to_account' in data:
                if data['from_account'] == data['to_account']:
                    errors.append("Transfer 'from_account' and 'to_account' must be different")
        
        elif category == 'Debt Payment':
            # Debt payment must have from_account and liability
            if 'from_account' not in data or not data['from_account']:
                errors.append("Debt Payment transactions must have 'from_account'")
            if 'liability' not in data or not data['liability']:
                errors.append("Debt Payment transactions must have 'liability'")
            if 'from_account' in data and 'liability' in data:
                if data['from_account'] == data['liability']:
                    errors.append("Debt Payment 'from_account' and 'liability' must be different")
        
        else:
            # Regular transaction must have account
            if 'account' not in data or not data['account']:
                errors.append("Regular transactions must have 'account'")
        
        return len(errors) == 0, errors


class RecurringTransactionSchema(BaseSchema):
    """Schema for recurring transaction pattern validation"""
    
    REQUIRED_FIELDS = ['id', 'title', 'amount', 'category', 'account', 'frequency', 'start_date']
    OPTIONAL_FIELDS = ['end_date', 'last_generated', 'active']
    VALID_FREQUENCIES = ['daily', 'weekly', 'biweekly', 'monthly', 'yearly']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate recurring transaction pattern data"""
        errors = []
        
        # Check required fields exist
        for field in RecurringTransactionSchema.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate id
        if not isinstance(data['id'], str) or not data['id'].strip():
            errors.append("'id' must be a non-empty string")
        
        # Validate title
        if not isinstance(data['title'], str) or not data['title'].strip():
            errors.append("'title' must be a non-empty string")
        
        # Validate amount
        try:
            float(data['amount'])
        except (ValueError, TypeError):
            errors.append("'amount' must be a valid number")
        
        # Validate category
        if not isinstance(data['category'], str) or not data['category'].strip():
            errors.append("'category' must be a non-empty string")
        
        # Validate account
        if not isinstance(data['account'], str) or not data['account'].strip():
            errors.append("'account' must be a non-empty string")
        
        # Validate frequency
        if data['frequency'] not in RecurringTransactionSchema.VALID_FREQUENCIES:
            errors.append(f"'frequency' must be one of: {RecurringTransactionSchema.VALID_FREQUENCIES}")
        
        # Validate start_date
        try:
            datetime.strptime(data['start_date'], '%Y-%m-%d')
        except (ValueError, TypeError):
            errors.append("'start_date' must be a valid date in YYYY-MM-DD format")
        
        # Validate optional end_date
        if 'end_date' in data and data['end_date']:
            try:
                datetime.strptime(data['end_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                errors.append("'end_date' must be a valid date in YYYY-MM-DD format")
        
        return len(errors) == 0, errors