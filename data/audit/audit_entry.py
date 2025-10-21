"""
Audit Log Entry Schema
Defines the structure of audit log entries
"""
from datetime import datetime
from typing import Dict, Any, Optional


class AuditEntry:
    """Represents a single audit log entry"""
    
    def __init__(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        changes: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Create an audit log entry
        
        Args:
            action: Type of action (add, update, delete, balance_change)
            entity_type: Type of entity (account, transaction, category, etc.)
            entity_id: Unique identifier of the entity
            entity_name: Human-readable name of the entity
            changes: Dictionary of what changed (old_value, new_value, etc.)
            timestamp: When the change occurred (defaults to now)
            metadata: Additional context (transaction_id, reason, etc.)
        """
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.changes = changes
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "changes": self.changes,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create from dictionary"""
        return cls(
            action=data["action"],
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            entity_name=data["entity_name"],
            changes=data["changes"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class BalanceChangeEntry(AuditEntry):
    """Specialized audit entry for balance changes"""
    
    def __init__(
        self,
        account_id: str,
        account_name: str,
        old_balance: float,
        new_balance: float,
        reason: str,
        transaction_id: Optional[str] = None,
        transaction_title: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Create a balance change audit entry
        
        Args:
            account_id: ID of the account
            account_name: Name of the account
            old_balance: Balance before change
            new_balance: Balance after change
            reason: Why the balance changed (transaction_add, transaction_delete, etc.)
            transaction_id: ID of related transaction (if applicable)
            transaction_title: Title of related transaction (if applicable)
            timestamp: When the change occurred (defaults to now)
        """
        change_amount = new_balance - old_balance
        
        changes = {
            "old_balance": old_balance,
            "new_balance": new_balance,
            "change_amount": change_amount
        }
        
        metadata = {
            "reason": reason
        }
        
        if transaction_id:
            metadata["transaction_id"] = transaction_id
        if transaction_title:
            metadata["transaction_title"] = transaction_title
        
        super().__init__(
            action="balance_change",
            entity_type="account",
            entity_id=account_id,
            entity_name=account_name,
            changes=changes,
            timestamp=timestamp,
            metadata=metadata
        )