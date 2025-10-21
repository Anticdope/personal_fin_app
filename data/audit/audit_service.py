"""
Audit Service
Business logic for audit logging
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .audit_repository import AuditLogRepository
from .audit_entry import AuditEntry, BalanceChangeEntry


class AuditService:
    """Service: Manages audit logging operations"""
    
    def __init__(self, audit_repo: AuditLogRepository):
        self.audit_repo = audit_repo
    
    # ===== BALANCE CHANGE LOGGING =====
    
    def log_balance_change(
        self,
        account_id: str,
        account_name: str,
        old_balance: float,
        new_balance: float,
        reason: str,
        transaction_id: Optional[str] = None,
        transaction_title: Optional[str] = None
    ):
        """Log a balance change"""
        entry = BalanceChangeEntry(
            account_id=account_id,
            account_name=account_name,
            old_balance=old_balance,
            new_balance=new_balance,
            reason=reason,
            transaction_id=transaction_id,
            transaction_title=transaction_title
        )
        self.audit_repo.append_entry(entry)
    
    def log_transaction_add(
        self,
        transaction: Dict[str, Any],
        affected_accounts: List[Dict[str, Any]]
    ):
        """
        Log a transaction addition and its balance impacts
        
        Args:
            transaction: The transaction data
            affected_accounts: List of dicts with account_id, name, old_balance, new_balance
        """
        transaction_id = transaction.get('id', 'unknown')
        transaction_title = transaction.get('title', 'Untitled')
        
        for account_info in affected_accounts:
            self.log_balance_change(
                account_id=account_info['account_id'],
                account_name=account_info['account_name'],
                old_balance=account_info['old_balance'],
                new_balance=account_info['new_balance'],
                reason="transaction_add",
                transaction_id=transaction_id,
                transaction_title=transaction_title
            )
    
    def log_transaction_delete(
        self,
        transaction: Dict[str, Any],
        affected_accounts: List[Dict[str, Any]]
    ):
        """Log a transaction deletion and its balance impacts"""
        transaction_id = transaction.get('id', 'unknown')
        transaction_title = transaction.get('title', 'Untitled')
        
        for account_info in affected_accounts:
            self.log_balance_change(
                account_id=account_info['account_id'],
                account_name=account_info['account_name'],
                old_balance=account_info['old_balance'],
                new_balance=account_info['new_balance'],
                reason="transaction_delete",
                transaction_id=transaction_id,
                transaction_title=transaction_title
            )
    
    def log_transaction_update(
        self,
        old_transaction: Dict[str, Any],
        new_transaction: Dict[str, Any],
        affected_accounts: List[Dict[str, Any]]
    ):
        """Log a transaction update and its balance impacts"""
        transaction_id = new_transaction.get('id', 'unknown')
        transaction_title = new_transaction.get('title', 'Untitled')
        
        for account_info in affected_accounts:
            self.log_balance_change(
                account_id=account_info['account_id'],
                account_name=account_info['account_name'],
                old_balance=account_info['old_balance'],
                new_balance=account_info['new_balance'],
                reason="transaction_update",
                transaction_id=transaction_id,
                transaction_title=transaction_title
            )
    
    # ===== ENTITY CHANGE LOGGING =====
    
    def log_entity_add(
        self,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        entity_data: Dict[str, Any]
    ):
        """Log entity creation (account, category, etc.)"""
        entry = AuditEntry(
            action="add",
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            changes={"created": entity_data}
        )
        self.audit_repo.append_entry(entry)
    
    def log_entity_update(
        self,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ):
        """Log entity update"""
        # Calculate what changed
        changes = {}
        for key in set(list(old_data.keys()) + list(new_data.keys())):
            old_val = old_data.get(key)
            new_val = new_data.get(key)
            if old_val != new_val:
                changes[key] = {
                    "old": old_val,
                    "new": new_val
                }
        
        entry = AuditEntry(
            action="update",
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            changes=changes
        )
        self.audit_repo.append_entry(entry)
    
    def log_entity_delete(
        self,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        entity_data: Dict[str, Any]
    ):
        """Log entity deletion"""
        entry = AuditEntry(
            action="delete",
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            changes={"deleted": entity_data}
        )
        self.audit_repo.append_entry(entry)
    
    # ===== QUERY METHODS =====
    
    def get_account_history(
        self,
        account_id: str,
        limit: Optional[int] = 50
    ) -> List[AuditEntry]:
        """Get audit history for an account"""
        return self.audit_repo.get_entries_for_account(account_id, limit=limit)
    
    def get_balance_history(
        self,
        account_id: str,
        limit: Optional[int] = 50
    ) -> List[AuditEntry]:
        """Get balance change history for an account"""
        return self.audit_repo.get_balance_changes_for_account(account_id, limit=limit)
    
    def get_all_changes_for_month(
        self,
        year: int,
        month: int
    ) -> List[AuditEntry]:
        """Get all audit entries for a month"""
        return self.audit_repo.get_entries_for_month(year, month)
    
    def recalculate_account_balance(
        self,
        account_id: str,
        starting_balance: float
    ) -> float:
        """
        Recalculate account balance from audit log
        Returns: The calculated current balance
        """
        balance = starting_balance
        
        # Get all balance changes for this account
        entries = self.audit_repo.get_balance_changes_for_account(account_id)
        
        # Sort by timestamp (oldest first)
        entries.sort(key=lambda e: e.timestamp)
        
        # Apply each change
        for entry in entries:
            change_amount = entry.changes.get('change_amount', 0)
            balance += change_amount
        
        return balance