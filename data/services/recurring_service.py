"""
Recurring Transaction Service - Handles recurring transaction logic
FIXED: Handles transactions without auto_post_date gracefully
"""
from datetime import datetime, timedelta
import uuid


class RecurringService:
    """Service: Business logic for recurring transactions"""
    
    def __init__(self, recurring_repo, transaction_repo, transaction_service=None):
        self.recurring_repo = recurring_repo
        self.transaction_repo = transaction_repo
        self.transaction_service = transaction_service  # Used to apply balance on auto-post
    
    def get_all_recurring(self):
        """Get all recurring transaction patterns"""
        return self.recurring_repo.get_all()
    
    def add_recurring_pattern(self, pattern_data):
        """Add a new recurring transaction pattern"""
        pattern_data['id'] = str(uuid.uuid4())
        self.recurring_repo.add(pattern_data)
        return pattern_data['id']
    
    def update_recurring_pattern(self, pattern_id, new_data):
        """Update a recurring transaction pattern"""
        new_data['id'] = pattern_id
        return self.recurring_repo.update_by_id(pattern_id, new_data)
    
    def delete_recurring_pattern(self, pattern_id):
        """Delete a recurring transaction pattern"""
        return self.recurring_repo.delete_by_id(pattern_id)
    
    def generate_pending_transactions(self, pattern, start_date=None, end_date=None):
        """
        Generate pending transactions from a recurring pattern
        Returns: list of generated transactions
        """
        if start_date is None:
            start_date = datetime.now().date()
        
        if end_date is None:
            # Default to end of current year
            end_date = datetime(start_date.year, 12, 31).date()
        
        frequency = pattern.get('frequency', 'monthly')
        pattern_start = datetime.strptime(pattern['start_date'], '%Y-%m-%d').date()
        pattern_end_str = pattern.get('end_date')
        
        if pattern_end_str:
            pattern_end = datetime.strptime(pattern_end_str, '%Y-%m-%d').date()
        else:
            pattern_end = end_date
        
        # Don't generate before pattern starts
        current = max(pattern_start, start_date)
        
        generated = []
        
        while current <= min(pattern_end, end_date):
            # Create pending transaction for this date
            transaction = {
                'title': pattern['title'],
                'amount': pattern['amount'],
                'category': pattern['category'],
                'account': pattern['account'],
                'status': 'pending',
                'recurring_id': pattern['id'],
                'auto_post_date': current.strftime('%Y-%m-%d')
            }
            
            # Add to the appropriate month
            self.transaction_repo.add_transaction(
                current.year,
                current.month,
                current.day,
                transaction
            )
            
            generated.append({
                'date': current,
                'transaction': transaction
            })
            
            # Calculate next occurrence
            if frequency == 'daily':
                current += timedelta(days=1)
            elif frequency == 'weekly':
                current += timedelta(weeks=1)
            elif frequency == 'biweekly':
                current += timedelta(weeks=2)
            elif frequency == 'monthly':
                # Move to next month, same day
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            elif frequency == 'yearly':
                current = current.replace(year=current.year + 1)
            else:
                break  # Unknown frequency
        
        return generated
    
    def post_pending_transactions(self, year, month, day):
        """
        Mark pending transactions as posted for a specific day
        Returns: list of posted transactions
        """
        transactions = self.transaction_repo.get_day_transactions(year, month, day)
        posted = []
        
        for transaction in transactions:
            # Skip if not pending
            if transaction.get('status') != 'pending':
                continue
            
            # FIXED: Check if auto_post_date exists before trying to access it
            if 'auto_post_date' not in transaction:
                # This is a manually created pending transaction, not recurring
                # Skip it - user will manually post it
                continue
            
            # Check if it's time to post
            auto_post_date = datetime.strptime(transaction['auto_post_date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            
            if auto_post_date <= today:
                # Post the transaction
                transaction['status'] = 'posted'
                self.transaction_repo.update_transaction(year, month, day, transaction)
                
                # Apply balance effect now that the transaction is posted
                if self.transaction_service:
                    self.transaction_service.apply_transaction_to_balance(transaction)
                
                posted.append(transaction)
        
        return posted
    
    def auto_post_due_transactions(self):
        """
        Automatically post all due pending transactions
        Should be called on app startup and periodically
        Returns: count of posted transactions
        """
        today = datetime.now().date()
        posted_count = 0
        
        # Check current and previous month (in case app wasn't opened)
        for month_offset in [0, -1]:
            check_date = today.replace(day=1)
            if month_offset == -1:
                if check_date.month == 1:
                    check_date = check_date.replace(year=check_date.year - 1, month=12)
                else:
                    check_date = check_date.replace(month=check_date.month - 1)
            
            year = check_date.year
            month = check_date.month
            
            # Get days in month
            if month == 12:
                next_month = check_date.replace(year=year + 1, month=1, day=1)
            else:
                next_month = check_date.replace(month=month + 1, day=1)
            
            days_in_month = (next_month - timedelta(days=1)).day
            
            # Check each day
            for day in range(1, days_in_month + 1):
                posted = self.post_pending_transactions(year, month, day)
                posted_count += len(posted)
        
        return posted_count
    
    def delete_future_recurring_transactions(self, recurring_id, from_date=None):
        """
        Delete all future pending transactions for a recurring pattern
        Used when deleting a recurring pattern or "this and all future"
        """
        if from_date is None:
            from_date = datetime.now().date()
        
        deleted_count = 0
        
        # Start from current month, go through end of next year
        current_date = from_date.replace(day=1)
        end_date = datetime(from_date.year + 1, 12, 31).date()
        
        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            
            # Get all transactions for the month
            month_data = self.transaction_repo.load_month_data(year, month)
            
            for day_key, transactions in month_data.items():
                day = int(day_key)
                trans_date = datetime(year, month, day).date()
                
                # Only delete transactions on or after from_date
                if trans_date < from_date:
                    continue
                
                # Find and remove transactions matching the recurring_id
                original_count = len(transactions)
                month_data[day_key] = [
                    t for t in transactions
                    if not (t.get('recurring_id') == recurring_id and 
                           t.get('status') == 'pending')
                ]
                deleted_count += original_count - len(month_data[day_key])
            
            # Save the modified month data
            self.transaction_repo.save_month_data(year, month, month_data)
            
            # Move to next month
            if month == 12:
                current_date = current_date.replace(year=year + 1, month=1)
            else:
                current_date = current_date.replace(month=month + 1)
        
        return deleted_count