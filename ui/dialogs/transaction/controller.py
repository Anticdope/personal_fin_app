"""
Transaction Dialog - Controller
Coordinates between Model and View for transaction management
"""
from .model import TransactionModel
from .view import TransactionView


class TransactionController:
    """Controller: Orchestrates transaction dialog operations"""
    
    def __init__(self, date, data_manager, parent=None):
        """
        Initialize transaction dialog for a specific date
        date: QDate object
        data_manager: DataManager instance
        parent: Parent widget
        """
        self.date = date
        self.model = TransactionModel(data_manager)
        self.view = TransactionView(date, parent)
        self.parent = parent
        self.editing_transaction = None  # Track which transaction is being edited
        
        self.connect_signals()
        self.load_data()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        # Add button
        self.view.add_button.clicked.connect(self.on_add_transaction)
        
        # Transaction actions
        self.view.edit_transaction_requested.connect(self.on_edit_transaction)
        self.view.delete_transaction_requested.connect(self.on_delete_transaction)
        self.view.post_transaction_requested.connect(self.on_post_transaction)
    
    def load_data(self):
        """Load initial data into the view"""
        # Populate dropdowns
        categories = self.model.get_categories()
        accounts = self.model.get_accounts()
        liabilities = self.model.get_liabilities()
        self.view.populate_dropdowns(categories, accounts, liabilities)
        
        # Load transactions
        self.load_transactions()
    
    def load_transactions(self):
        """Load and display transactions for the day"""
        transactions = self.model.get_day_transactions(self.date)
        self.view.display_transactions(transactions)
        
        # Update summary
        summary = self.model.calculate_day_summary(transactions)
        self.view.update_summary(summary)
    
    def on_add_transaction(self):
        """Handle add transaction button click"""
        # Check if we're in edit mode
        if self.editing_transaction:
            self._handle_update_transaction()
            return
        
        # Otherwise, add new transaction
        # Get form data
        data = self.view.get_form_data()
        category = data.get('category', '')
        
        # Handle special transaction types first (Transfer, Debt Payment)
        # These don't support recurring yet
        if category == "Transfer":
            if data.get('recurring', False):
                self.view.show_error("Recurring transfers are not yet supported")
                return
            self._handle_transfer(data)
        elif category == "Debt Payment":
            if data.get('recurring', False):
                self.view.show_error("Recurring debt payments are not yet supported")
                return
            self._handle_debt_payment(data)
        elif data.get('recurring', False):
            # Regular transaction with recurring flag
            self._handle_recurring(data)
        else:
            # Regular one-time transaction
            self._handle_regular_transaction(data)
    
    def _handle_regular_transaction(self, data):
        """Handle adding a regular transaction"""
        transaction_type = data.get('transaction_type', 'Expense')
        
        # Validate
        valid, errors = self.model.validate_transaction(
            data['title'],
            data['amount'],
            data['category'],
            data['account']
        )
        
        if not valid:
            error_message = "\n".join(f"• {error}" for error in errors.values())
            self.view.show_error(error_message)
            return
        
        # Convert amount based on transaction type
        amount = abs(float(data['amount']))
        if transaction_type == "Expense":
            amount = -amount  # Expenses are negative
        # Income and Savings are positive
        
        # Format transaction data
        transaction = {
            'title': data['title'],
            'amount': amount,
            'category': data['category'],
            'account': data['account'],
            'transaction_type': transaction_type,
            'status': 'posted'
        }
        
        # Add transaction
        self.model.add_transaction(self.date, transaction)
        
        # Clear form and reload
        self.view.clear_form()
        self.load_transactions()
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'refresh_all'):
            self.parent.refresh_all()
    
    def _handle_transfer(self, data):
        """Handle adding a transfer transaction"""
        # Validate
        if not data.get('amount') or data['amount'].strip() == '':
            self.view.show_error("Amount is required")
            return
        
        try:
            amount = abs(float(data['amount']))  # Transfers are always positive
        except ValueError:
            self.view.show_error("Invalid amount")
            return
        
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        
        if not from_account or not to_account:
            self.view.show_error("Both accounts are required for transfer")
            return
        
        if from_account == to_account:
            self.view.show_error("Cannot transfer to the same account")
            return
        
        # Create transfer transaction
        transaction = {
            'title': data.get('title') or f"Transfer: {from_account} → {to_account}",
            'amount': amount,
            'category': 'Transfer',
            'source_account': from_account,
            'target_account': to_account,
            'status': 'posted'
        }
        
        # Add transaction
        self.model.add_transaction(self.date, transaction)
        
        # Clear form and reload
        self.view.clear_form()
        self.load_transactions()
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'refresh_all'):
            self.parent.refresh_all()
    
    def _handle_debt_payment(self, data):
        """Handle adding a debt payment transaction"""
        # Validate
        if not data.get('amount') or data['amount'].strip() == '':
            self.view.show_error("Amount is required")
            return
        
        try:
            amount = abs(float(data['amount']))  # Payments are always positive
        except ValueError:
            self.view.show_error("Invalid amount")
            return
        
        from_account = data.get('from_account')
        liability = data.get('liability')
        
        if not from_account or not liability:
            self.view.show_error("Both account and liability are required")
            return
        
        # Check if trying to pay from same account (e.g., paying Credit Card 1 from Credit Card 1)
        if from_account == liability:
            self.view.show_error("Cannot pay a debt from the same account")
            return
        
        # Determine if the liability is a credit account or actual liability
        target_type = 'credit'  # Default to credit account
        
        # Check if it's actually a liability
        for liab in self.model.data_manager.liabilities:
            if liab['name'] == liability:
                target_type = 'liability'
                break
        
        # Create debt payment transaction with correct field names
        transaction = {
            'title': data.get('title') or f"Payment: {liability}",
            'amount': amount,
            'category': 'Debt Payment',
            'source_account': from_account,  # Changed from 'from_account'
            'target_debt': liability,  # Changed from 'liability'
            'target_type': target_type,
            'status': 'posted'
        }
        
        # Add transaction
        self.model.add_transaction(self.date, transaction)
        
        # Clear form and reload
        self.view.clear_form()
        self.load_transactions()
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'refresh_all'):
            self.parent.refresh_all()
    
    def _handle_recurring(self, data):
        """Handle adding a recurring transaction"""
        # Validate with recurring fields
        valid, errors = self.model.validate_transaction(
            data['title'],
            data['amount'],
            data['category'],
            data['account'],
            recurring=True,
            frequency=data.get('frequency'),
            start_date=data.get('start_date')
        )
        
        if not valid:
            error_message = "\n".join(f"• {error}" for error in errors.values())
            self.view.show_error(error_message)
            return
        
        # Create recurring pattern
        pattern = self.model.format_recurring_pattern(
            data['title'],
            data['amount'],
            data['category'],
            data['account'],
            data['frequency'],
            data['start_date'],
            data.get('end_date')
        )
        
        # Add recurring pattern
        from datetime import datetime
        pattern_id = self.model.data_manager.recurring_service.add_recurring_pattern(pattern)
        
        # Generate pending transactions
        self.model.data_manager.recurring_service.generate_pending_transactions(pattern)
        
        self.view.show_success("Recurring transaction created successfully")
        
        # Clear form and reload
        self.view.clear_form()
        self.load_transactions()
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'refresh_all'):
            self.parent.refresh_all()
    
    def on_edit_transaction(self, transaction):
        """Handle edit transaction request"""
        # Store the transaction being edited
        self.editing_transaction = transaction
        
        # Populate form based on transaction type
        category = transaction.get('category', '')
        
        if category == 'Transfer':
            self._populate_transfer_form(transaction)
        elif category == 'Debt Payment':
            self._populate_debt_payment_form(transaction)
        else:
            self._populate_regular_form(transaction)
        
        # Switch to update mode
        self.view.set_edit_mode(True)
    
    def on_delete_transaction(self, transaction):
        """Handle delete transaction request"""
        # Confirm deletion
        if not self.view.confirm_delete(transaction.get('title', 'this transaction')):
            return
        
        # Delete transaction
        self.model.delete_transaction(self.date, transaction)
        
        # Reload
        self.load_transactions()
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'refresh_all'):
            self.parent.refresh_all()
    
    def on_post_transaction(self, transaction):
        """Handle post transaction request"""
        # Mark as posted
        self.model.post_transaction(self.date, transaction)
        
        # Reload
        self.load_transactions()
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'refresh_all'):
            self.parent.refresh_all()
    
    def exec(self):
        """Show dialog and return result"""
        return self.view.exec()
    
    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)
    
    # ===== EDIT TRANSACTION HELPERS =====
    
    def _populate_regular_form(self, transaction):
        """Populate form for editing a regular transaction"""
        self.view.type_combo.setCurrentText(transaction.get('transaction_type', 'Expense'))
        self.view.title_input.setText(transaction.get('title', ''))
        self.view.amount_input.setText(str(abs(transaction.get('amount', 0))))
        self.view.category_combo.setCurrentText(transaction.get('category', ''))
        self.view.account_combo.setCurrentText(transaction.get('account', ''))
    
    def _populate_transfer_form(self, transaction):
        """Populate form for editing a transfer"""
        self.view.type_combo.setCurrentText('Transfer')
        self.view.title_input.setText(transaction.get('title', ''))
        self.view.amount_input.setText(str(abs(transaction.get('amount', 0))))
        self.view.from_account_combo.setCurrentText(transaction.get('source_account', ''))
        self.view.to_account_combo.setCurrentText(transaction.get('target_account', ''))
    
    def _populate_debt_payment_form(self, transaction):
        """Populate form for editing a debt payment"""
        self.view.type_combo.setCurrentText('Debt Payment')
        self.view.title_input.setText(transaction.get('title', ''))
        self.view.amount_input.setText(str(abs(transaction.get('amount', 0))))
        self.view.debt_from_account_combo.setCurrentText(transaction.get('source_account', ''))
        self.view.liability_combo.setCurrentText(transaction.get('target_debt', ''))
    
    def _handle_update_transaction(self):
        """Handle updating an existing transaction"""
        if not self.editing_transaction:
            return
        
        # Get form data
        data = self.view.get_form_data()
        category = data.get('category', '')
        
        # Create new transaction based on type
        if category == "Transfer":
            new_transaction = self._create_transfer_transaction(data)
        elif category == "Debt Payment":
            new_transaction = self._create_debt_payment_transaction(data)
        else:
            new_transaction = self._create_regular_transaction(data)
        
        if not new_transaction:
            return  # Error already shown
        
        # Update transaction through model
        self.model.update_transaction(self.date, self.editing_transaction, new_transaction)
        
        # Clear editing state
        self.editing_transaction = None
        self.view.set_edit_mode(False)
        
        # Clear form and reload
        self.view.clear_form()
        self.load_transactions()
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'refresh_all'):
            self.parent.refresh_all()
    
    def _create_regular_transaction(self, data):
        """Create a regular transaction from form data"""
        transaction_type = data.get('transaction_type', 'Expense')
        
        # Validate
        valid, errors = self.model.validate_transaction(
            data['title'],
            data['amount'],
            data['category'],
            data['account']
        )
        
        if not valid:
            error_message = "\n".join(f"• {error}" for error in errors.values())
            self.view.show_error(error_message)
            return None
        
        # Convert amount based on transaction type
        amount = abs(float(data['amount']))
        if transaction_type == "Expense":
            amount = -amount
        
        return {
            'title': data['title'],
            'amount': amount,
            'category': data['category'],
            'account': data['account'],
            'transaction_type': transaction_type,
            'status': 'posted'
        }
    
    def _create_transfer_transaction(self, data):
        """Create a transfer transaction from form data"""
        if not data.get('amount') or data['amount'].strip() == '':
            self.view.show_error("Amount is required")
            return None
        
        try:
            amount = abs(float(data['amount']))
        except ValueError:
            self.view.show_error("Invalid amount")
            return None
        
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        
        if not from_account or not to_account:
            self.view.show_error("Both accounts are required for transfer")
            return None
        
        if from_account == to_account:
            self.view.show_error("Cannot transfer to the same account")
            return None
        
        return {
            'title': data.get('title') or f"Transfer: {from_account} → {to_account}",
            'amount': amount,
            'category': 'Transfer',
            'source_account': from_account,
            'target_account': to_account,
            'status': 'posted'
        }
    
    def _create_debt_payment_transaction(self, data):
        """Create a debt payment transaction from form data"""
        if not data.get('amount') or data['amount'].strip() == '':
            self.view.show_error("Amount is required")
            return None
        
        try:
            amount = abs(float(data['amount']))
        except ValueError:
            self.view.show_error("Invalid amount")
            return None
        
        from_account = data.get('from_account')
        liability = data.get('liability')
        
        if not from_account or not liability:
            self.view.show_error("Both account and liability are required")
            return None
        
        if from_account == liability:
            self.view.show_error("Cannot pay a debt from the same account")
            return None
        
        # Determine if the liability is a credit account or actual liability
        target_type = 'credit'
        for liab in self.model.data_manager.liabilities:
            if liab['name'] == liability:
                target_type = 'liability'
                break
        
        return {
            'title': data.get('title') or f"Payment: {liability}",
            'amount': amount,
            'category': 'Debt Payment',
            'source_account': from_account,
            'target_debt': liability,
            'target_type': target_type,
            'status': 'posted'
        }