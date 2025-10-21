"""
Audit Log Repository
Handles persistence of audit log entries
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from .audit_entry import AuditEntry


class AuditLogRepository:
    """Repository: Manages audit log persistence"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.audit_dir = self.data_dir / "audit"
        self.audit_dir.mkdir(exist_ok=True)
    
    def _get_log_file(self, year: int, month: int) -> Path:
        """Get the audit log file for a specific month"""
        return self.audit_dir / f"audit_{year}_{month:02d}.json"
    
    def append_entry(self, entry: AuditEntry):
        """Append a single audit entry to the log"""
        timestamp = entry.timestamp
        file_path = self._get_log_file(timestamp.year, timestamp.month)
        
        # Load existing entries
        entries = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                entries = json.load(f)
        
        # Append new entry
        entries.append(entry.to_dict())
        
        # Save back
        with open(file_path, 'w') as f:
            json.dump(entries, f, indent=2)
    
    def append_entries(self, entries: List[AuditEntry]):
        """Append multiple audit entries (batch operation)"""
        for entry in entries:
            self.append_entry(entry)
    
    def get_entries_for_month(self, year: int, month: int) -> List[AuditEntry]:
        """Get all audit entries for a specific month"""
        file_path = self._get_log_file(year, month)
        
        if not file_path.exists():
            return []
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return [AuditEntry.from_dict(entry_data) for entry_data in data]
    
    def get_entries_for_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[AuditEntry]:
        """Get all audit entries within a date range"""
        entries = []
        
        # Iterate through all months in range
        current = start_date.replace(day=1)
        while current <= end_date:
            month_entries = self.get_entries_for_month(current.year, current.month)
            
            # Filter by date range
            for entry in month_entries:
                if start_date <= entry.timestamp <= end_date:
                    entries.append(entry)
            
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return entries
    
    def get_entries_for_account(
        self,
        account_id: str,
        limit: Optional[int] = None
    ) -> List[AuditEntry]:
        """Get audit entries for a specific account"""
        # Get entries from recent months (last 12 months)
        now = datetime.now()
        entries = []
        
        for months_back in range(12):
            year = now.year
            month = now.month - months_back
            
            if month <= 0:
                year -= 1
                month += 12
            
            month_entries = self.get_entries_for_month(year, month)
            
            # Filter for this account
            for entry in month_entries:
                if entry.entity_id == account_id:
                    entries.append(entry)
            
            # Check if we have enough
            if limit and len(entries) >= limit:
                break
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        if limit:
            return entries[:limit]
        return entries
    
    def get_balance_changes_for_account(
        self,
        account_id: str,
        limit: Optional[int] = None
    ) -> List[AuditEntry]:
        """Get only balance change entries for an account"""
        entries = self.get_entries_for_account(account_id, limit=limit)
        return [e for e in entries if e.action == "balance_change"]
    
    def get_all_balance_changes(self, year: int, month: int) -> List[AuditEntry]:
        """Get all balance changes for a specific month"""
        entries = self.get_entries_for_month(year, month)
        return [e for e in entries if e.action == "balance_change"]