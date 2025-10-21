"""
Transaction Service - Handles transaction business logic
FIXED: Proper debit/credit account logic
UPDATED: Now logs all balance changes to audit log
"""


class TransactionService:
    """Service: Business logic for transaction operations with audit logging"""
    
    def __init__(self, account_repo, asset_repo, liability_repo, audit_service=None):
        self.account_repo = account_repo
        self.asset_repo = asset_repo
        self.liability_repo = liability_repo
        self.audit_service = audit_service
    
    def apply_transaction_to_balance(self, transaction):
        """
        Apply a transaction's effects to account/liability balances
        Handles: Regular transactions, Transfers, Debt Payments
        """
        category = transaction.get('category', '')
        
        if category == 'Transfer':
            self._handle_transfer(transaction)
        elif category == 'Debt Payment':
            self._handle_debt_payment(transaction)
        else:
            self._handle_regular_transaction(transaction)
    
    def reverse_transaction_from_balance(self, transaction):
        """
        Reverse a transaction's effects on balances (for updates/deletes)
        """
        category = transaction.get('category', '')
        
        if category == 'Transfer':
            self._reverse_transfer(transaction)
        elif category == 'Debt Payment':
            self._reverse_debt_payment(transaction)
        else:
            self._reverse_regular_transaction(transaction)
    
    def _handle_regular_transaction(self, transaction):
        """Handle a regular income or expense transaction"""
        amount = float(transaction.get('amount', 0))
        account_name = transaction.get('account')
        
        account = self.account_repo.get_by_name(account_name)
        if not account:
            print(f"⚠️ Account '{account_name}' not found")
            return
        
        # Get old balance for audit
        old_balance = account['balance']
        
        # Apply transaction based on account type
        account_type = account.get('type', 'debit').lower()
        
        if account_type == 'debit':
            # Debit account: positive amount = money in (increase), negative = money out (decrease)
            # Example: +100 income = balance increases, -50 expense = balance decreases
            new_balance = account['balance'] + amount
        else:  # credit
            # Credit account: positive amount = charges/purchases (INCREASE debt owed)
            #                 negative amount = payments/refunds (DECREASE debt owed)
            # Example: -50 expense (charge) = debt increases by 50, +50 payment = debt decreases by 50
            # SO WE SUBTRACT because amounts come in as negative for expenses
            new_balance = account['balance'] - amount
        
        # Create updated account
        updated_account = account.copy()
        updated_account['balance'] = new_balance
        
        # Update in repository
        self.account_repo.update(account, updated_account)
        
        # Log to audit if service is available
        if self.audit_service:
            self.audit_service.log_balance_change(
                account_id=account['id'],
                account_name=account_name,
                old_balance=old_balance,
                new_balance=new_balance,
                reason="transaction_add",
                transaction_id=transaction.get('id'),
                transaction_title=transaction.get('title')
            )

    
    def _handle_transfer(self, transaction):
        """Handle a transfer between accounts"""
        amount = abs(float(transaction.get('amount', 0)))
        source_account_name = transaction.get('source_account')
        target_account_name = transaction.get('target_account')
        
        source = self.account_repo.get_by_name(source_account_name)
        target = self.account_repo.get_by_name(target_account_name)
        
        if not source or not target:
            print(f"⚠️ Transfer accounts not found")
            return
        
        # Get old balances for audit
        source_old_balance = source['balance']
        target_old_balance = target['balance']
        
        # Calculate new balances
        source_type = source.get('type', 'debit').lower()
        target_type = target.get('type', 'debit').lower()
        
        if source_type == 'debit':
            source_new_balance = source['balance'] - amount
        else:  # credit
            source_new_balance = source['balance'] - amount
        
        if target_type == 'debit':
            target_new_balance = target['balance'] + amount
        else:  # credit
            target_new_balance = target['balance'] + amount
        
        # Create updated accounts
        updated_source = source.copy()
        updated_source['balance'] = source_new_balance
        
        updated_target = target.copy()
        updated_target['balance'] = target_new_balance
        
        # Update in repository
        self.account_repo.update(source, updated_source)
        self.account_repo.update(target, updated_target)
        
        # Log to audit
        if self.audit_service:
            transaction_id = transaction.get('id')
            transaction_title = transaction.get('title')
            
            self.audit_service.log_balance_change(
                account_id=source['id'],
                account_name=source_account_name,
                old_balance=source_old_balance,
                new_balance=source_new_balance,
                reason="transfer_out",
                transaction_id=transaction_id,
                transaction_title=transaction_title
            )
            
            self.audit_service.log_balance_change(
                account_id=target['id'],
                account_name=target_account_name,
                old_balance=target_old_balance,
                new_balance=target_new_balance,
                reason="transfer_in",
                transaction_id=transaction_id,
                transaction_title=transaction_title
            )
    
    def _handle_debt_payment(self, transaction):
        """Handle a debt payment"""
        amount = abs(float(transaction.get('amount', 0)))
        source_account_name = transaction.get('source_account')
        target_debt_name = transaction.get('target_debt')
        target_type = transaction.get('target_type', 'credit')
        
        print(f"DEBUG DEBT PAYMENT: amount={amount}, source={source_account_name}, target={target_debt_name}, type={target_type}")
        
        source = self.account_repo.get_by_name(source_account_name)
        if not source:
            print(f"⚠️ Source account '{source_account_name}' not found")
            return
        
        # Get old balance for audit
        source_old_balance = source['balance']
        print(f"DEBUG: Source old balance: {source_old_balance}")
        
        # Deduct from source account
        source_new_balance = source['balance'] - amount
        print(f"DEBUG: Source new balance: {source_new_balance}")
        
        updated_source = source.copy()
        updated_source['balance'] = source_new_balance
        self.account_repo.update(source, updated_source)
        print(f"DEBUG: Source account updated")
        
        # Reduce debt balance
        if target_type == 'credit':
            target = self.account_repo.get_by_name(target_debt_name)
            if target and target['type'].lower() == 'credit':
                target_old_balance = target['balance']
                print(f"DEBUG: Target (credit) old balance: {target_old_balance}")
                
                target_new_balance = target['balance'] - amount  # Reduce debt
                print(f"DEBUG: Target (credit) new balance: {target_new_balance}")
                
                updated_target = target.copy()
                updated_target['balance'] = target_new_balance
                self.account_repo.update(target, updated_target)
                print(f"DEBUG: Target credit account updated")
                
                # Log debt reduction
                if self.audit_service:
                    self.audit_service.log_balance_change(
                        account_id=target['id'],
                        account_name=target_debt_name,
                        old_balance=target_old_balance,
                        new_balance=target_new_balance,
                        reason="debt_payment",
                        transaction_id=transaction.get('id'),
                        transaction_title=transaction.get('title')
                    )
        else:  # liability
            target = self.liability_repo.get_by_name(target_debt_name)
            if target:
                target_old_balance = target['balance']
                print(f"DEBUG: Target (liability) old balance: {target_old_balance}")
                
                target_new_balance = target['balance'] - amount  # Reduce debt
                print(f"DEBUG: Target (liability) new balance: {target_new_balance}")
                
                updated_target = target.copy()
                updated_target['balance'] = target_new_balance
                self.liability_repo.update(target, updated_target)
                print(f"DEBUG: Target liability updated")
                
                # Log liability reduction
                if self.audit_service:
                    self.audit_service.log_balance_change(
                        account_id=target['id'],
                        account_name=target_debt_name,
                        old_balance=target_old_balance,
                        new_balance=target_new_balance,
                        reason="debt_payment",
                        transaction_id=transaction.get('id'),
                        transaction_title=transaction.get('title')
                    )
        
        # Log source account deduction
        if self.audit_service:
            self.audit_service.log_balance_change(
                account_id=source['id'],
                account_name=source_account_name,
                old_balance=source_old_balance,
                new_balance=source_new_balance,
                reason="debt_payment_deduction",
                transaction_id=transaction.get('id'),
                transaction_title=transaction.get('title')
            )
        
        print(f"DEBUG: Debt payment processing complete")
    
    def _reverse_regular_transaction(self, transaction):
        """Reverse a regular transaction"""
        amount = float(transaction.get('amount', 0))
        account_name = transaction.get('account')
        
        account = self.account_repo.get_by_name(account_name)
        if not account:
            return
        
        # Get old balance for audit
        old_balance = account['balance']
        
        # Get account type
        account_type = account.get('type', 'debit').lower()
        
        # Reverse the effect based on account type
        if account_type == 'debit':
            new_balance = account['balance'] - amount
        else:  # credit
            new_balance = account['balance'] + amount  # Opposite of apply
        
        # Update account
        updated_account = account.copy()
        updated_account['balance'] = new_balance
        self.account_repo.update(account, updated_account)
        
        # Log reversal
        if self.audit_service:
            self.audit_service.log_balance_change(
                account_id=account['id'],
                account_name=account_name,
                old_balance=old_balance,
                new_balance=new_balance,
                reason="transaction_reverse",
                transaction_id=transaction.get('id'),
                transaction_title=transaction.get('title')
            )
    
    def _reverse_transfer(self, transaction):
        """Reverse a transfer"""
        amount = abs(float(transaction.get('amount', 0)))
        source_account_name = transaction.get('source_account')
        target_account_name = transaction.get('target_account')
        
        source = self.account_repo.get_by_name(source_account_name)
        target = self.account_repo.get_by_name(target_account_name)
        
        if source and target:
            # Get old balances
            source_old = source['balance']
            target_old = target['balance']
            
            # Calculate new balances (reverse)
            source_new = source['balance'] + amount
            target_new = target['balance'] - amount
            
            # Update accounts
            updated_source = source.copy()
            updated_source['balance'] = source_new
            self.account_repo.update(source, updated_source)
            
            updated_target = target.copy()
            updated_target['balance'] = target_new
            self.account_repo.update(target, updated_target)
            
            # Log reversals
            if self.audit_service:
                transaction_id = transaction.get('id')
                transaction_title = transaction.get('title')
                
                self.audit_service.log_balance_change(
                    account_id=source['id'],
                    account_name=source_account_name,
                    old_balance=source_old,
                    new_balance=source_new,
                    reason="transfer_reverse",
                    transaction_id=transaction_id,
                    transaction_title=transaction_title
                )
                
                self.audit_service.log_balance_change(
                    account_id=target['id'],
                    account_name=target_account_name,
                    old_balance=target_old,
                    new_balance=target_new,
                    reason="transfer_reverse",
                    transaction_id=transaction_id,
                    transaction_title=transaction_title
                )
    
    def _reverse_debt_payment(self, transaction):
        """Reverse a debt payment"""
        amount = abs(float(transaction.get('amount', 0)))
        source_account_name = transaction.get('source_account')
        target_debt_name = transaction.get('target_debt')
        target_type = transaction.get('target_type', 'credit')
        
        # Restore source account
        source = self.account_repo.get_by_name(source_account_name)
        if source:
            source_old = source['balance']
            source_new = source['balance'] + amount
            updated_source = source.copy()
            updated_source['balance'] = source_new
            self.account_repo.update(source, updated_source)
            
            if self.audit_service:
                self.audit_service.log_balance_change(
                    account_id=source['id'],
                    account_name=source_account_name,
                    old_balance=source_old,
                    new_balance=source_new,
                    reason="debt_payment_reverse",
                    transaction_id=transaction.get('id'),
                    transaction_title=transaction.get('title')
                )
        
        # Restore debt
        if target_type == 'credit':
            target = self.account_repo.get_by_name(target_debt_name)
            if target:
                target_old = target['balance']
                target_new = target['balance'] + amount
                updated_target = target.copy()
                updated_target['balance'] = target_new
                self.account_repo.update(target, updated_target)
                
                if self.audit_service:
                    self.audit_service.log_balance_change(
                        account_id=target['id'],
                        account_name=target_debt_name,
                        old_balance=target_old,
                        new_balance=target_new,
                        reason="debt_payment_reverse",
                        transaction_id=transaction.get('id'),
                        transaction_title=transaction.get('title')
                    )
        else:
            target = self.liability_repo.get_by_name(target_debt_name)
            if target:
                target_old = target['balance']
                target_new = target['balance'] + amount
                updated_target = target.copy()
                updated_target['balance'] = target_new
                self.liability_repo.update(target, updated_target)
                
                if self.audit_service:
                    self.audit_service.log_balance_change(
                        account_id=target['id'],
                        account_name=target_debt_name,
                        old_balance=target_old,
                        new_balance=target_new,
                        reason="debt_payment_reverse",
                        transaction_id=transaction.get('id'),
                        transaction_title=transaction.get('title')
                    )