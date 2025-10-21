"""
Transaction Dialog - View
Pure UI for viewing and managing transactions for a specific day
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QComboBox, QScrollArea,
                               QWidget, QFrame, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, Signal


class TransactionView(QDialog):
    """View: Pure UI for transaction management"""
    
    # Signals for user actions
    add_transaction_requested = Signal(dict)
    edit_transaction_requested = Signal(dict)
    delete_transaction_requested = Signal(dict)
    post_transaction_requested = Signal(dict)
    
    def __init__(self, date, parent=None):
        super().__init__(parent)
        self.date = date
        self.dark_mode = False
        self.all_categories = []  # Store all categories with their types
        
        self.setWindowTitle(f"Transactions - {date.toString('MMMM d, yyyy')}")
        self.setModal(True)
        self.resize(700, 600)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"Transactions for {self.date.toString('MMMM d, yyyy')}")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Day of week
        day_label = QLabel(self.date.toString('dddd'))
        day_label.setObjectName("subtitle")
        layout.addWidget(day_label)
        
        # Transactions list (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.transactions_widget = QWidget()
        self.transactions_layout = QVBoxLayout(self.transactions_widget)
        self.transactions_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.transactions_widget)
        layout.addWidget(scroll)
        
        # Add transaction section
        add_section = QFrame()
        add_section.setObjectName("sectionFrame")
        add_layout = QVBoxLayout(add_section)
        
        add_label = QLabel("Add Transaction")
        add_label.setObjectName("subtitle")
        add_layout.addWidget(add_label)
        
        form_layout = QVBoxLayout()
        
        # Transaction Type selection (Income/Expense/Savings/Transfer/Debt Payment)
        row_type = QHBoxLayout()
        type_label = QLabel("Transaction Type:")
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("formCombo")
        self.type_combo.addItems(["Expense", "Income", "Savings", "Transfer", "Debt Payment"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        row_type.addWidget(type_label)
        row_type.addWidget(self.type_combo)
        row_type.addStretch()
        form_layout.addLayout(row_type)
        
        # Title and Amount
        row1 = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setObjectName("formInput")
        self.title_input.setPlaceholderText("Title")
        
        self.amount_input = QLineEdit()
        self.amount_input.setObjectName("formInput")
        self.amount_input.setPlaceholderText("Amount (positive number)")
        
        row1.addWidget(self.title_input)
        row1.addWidget(self.amount_input)
        form_layout.addLayout(row1)
        
        # Regular transaction fields (Category + Account)
        self.regular_frame = QFrame()
        self.regular_frame.setObjectName("formFrame")
        regular_layout = QHBoxLayout(self.regular_frame)
        
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.setObjectName("formCombo")
        
        account_label = QLabel("Account:")
        self.account_combo = QComboBox()
        self.account_combo.setObjectName("formCombo")
        
        regular_layout.addWidget(category_label)
        regular_layout.addWidget(self.category_combo)
        regular_layout.addWidget(account_label)
        regular_layout.addWidget(self.account_combo)
        form_layout.addWidget(self.regular_frame)
        
        # Transfer fields (From Account + To Account)
        self.transfer_frame = QFrame()
        self.transfer_frame.setObjectName("formFrame")
        self.transfer_frame.setVisible(False)
        transfer_layout = QHBoxLayout(self.transfer_frame)
        
        from_label = QLabel("From Account:")
        self.from_account_combo = QComboBox()
        self.from_account_combo.setObjectName("formCombo")
        
        to_label = QLabel("To Account:")
        self.to_account_combo = QComboBox()
        self.to_account_combo.setObjectName("formCombo")
        
        transfer_layout.addWidget(from_label)
        transfer_layout.addWidget(self.from_account_combo)
        transfer_layout.addWidget(to_label)
        transfer_layout.addWidget(self.to_account_combo)
        form_layout.addWidget(self.transfer_frame)
        
        # Debt Payment fields (From Account + Liability)
        self.debt_frame = QFrame()
        self.debt_frame.setObjectName("formFrame")
        self.debt_frame.setVisible(False)
        debt_layout = QHBoxLayout(self.debt_frame)
        
        debt_from_label = QLabel("From Account:")
        self.debt_from_account_combo = QComboBox()
        self.debt_from_account_combo.setObjectName("formCombo")
        
        liability_label = QLabel("Pay Off:")
        self.liability_combo = QComboBox()
        self.liability_combo.setObjectName("formCombo")
        
        debt_layout.addWidget(debt_from_label)
        debt_layout.addWidget(self.debt_from_account_combo)
        debt_layout.addWidget(liability_label)
        debt_layout.addWidget(self.liability_combo)
        form_layout.addWidget(self.debt_frame)
        
        # Recurring checkbox
        row3 = QHBoxLayout()
        self.recurring_checkbox = QCheckBox("Recurring Transaction")
        self.recurring_checkbox.stateChanged.connect(self.on_recurring_changed)
        row3.addWidget(self.recurring_checkbox)
        row3.addStretch()
        form_layout.addLayout(row3)
        
        # Recurring fields (initially hidden)
        self.recurring_frame = QFrame()
        self.recurring_frame.setObjectName("formFrame")
        self.recurring_frame.setVisible(False)
        recurring_layout = QVBoxLayout(self.recurring_frame)
        
        # Frequency
        freq_layout = QHBoxLayout()
        freq_label = QLabel("Frequency:")
        freq_label.setObjectName("formLabel")
        self.frequency_combo = QComboBox()
        self.frequency_combo.setObjectName("formCombo")
        self.frequency_combo.addItems(["Daily", "Weekly", "Bi-weekly", "Monthly", "Yearly"])
        self.frequency_combo.setCurrentText("Monthly")
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.frequency_combo)
        freq_layout.addStretch()
        recurring_layout.addLayout(freq_layout)
        
        # Start date
        start_layout = QHBoxLayout()
        start_label = QLabel("Start Date:")
        start_label.setObjectName("formLabel")
        self.start_date_edit = QLineEdit()
        self.start_date_edit.setObjectName("formInput")
        self.start_date_edit.setPlaceholderText("YYYY-MM-DD")
        self.start_date_edit.setText(self.date.toString('yyyy-MM-dd'))
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_date_edit)
        recurring_layout.addLayout(start_layout)
        
        # End date
        end_layout = QHBoxLayout()
        end_label = QLabel("End Date:")
        end_label.setObjectName("formLabel")
        self.end_date_edit = QLineEdit()
        self.end_date_edit.setObjectName("formInput")
        self.end_date_edit.setPlaceholderText("YYYY-MM-DD (optional)")
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_date_edit)
        recurring_layout.addLayout(end_layout)
        
        form_layout.addWidget(self.recurring_frame)
        
        add_layout.addLayout(form_layout)
        
        # Add button
        self.add_button = QPushButton("Add Transaction")
        self.add_button.setObjectName("successButton")
        add_layout.addWidget(self.add_button)
        
        layout.addWidget(add_section)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setObjectName("cardFrame")
        summary_layout = QVBoxLayout(summary_frame)
        
        self.pending_summary = QLabel()
        self.pending_summary.setObjectName("mutedLabel")
        
        self.posted_summary = QLabel()
        
        self.net_summary = QLabel()
        self.net_summary.setObjectName("subtitle")
        
        summary_layout.addWidget(self.pending_summary)
        summary_layout.addWidget(self.posted_summary)
        summary_layout.addWidget(self.net_summary)
        
        layout.addWidget(summary_frame)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def populate_dropdowns(self, categories, accounts, liabilities=None):
        """
        Populate dropdowns with data
        categories: list of dicts with 'name' and 'type' keys
        accounts: list of account names (all types)
        liabilities: list of liability dicts
        """
        # Store categories - convert if needed for backward compatibility
        self.all_categories = []
        
        for cat in categories:
            if isinstance(cat, dict):
                self.all_categories.append(cat)
            else:
                # Legacy format - convert string to dict
                self.all_categories.append({'name': cat, 'type': 'expense'})
        
        # Account dropdowns
        self.account_combo.clear()
        self.account_combo.addItems(accounts)
        
        self.from_account_combo.clear()
        self.from_account_combo.addItems(accounts)
        
        self.to_account_combo.clear()
        self.to_account_combo.addItems(accounts)
        
        self.debt_from_account_combo.clear()
        self.debt_from_account_combo.addItems(accounts)
        
        # Liability dropdown - should include both credit accounts AND liabilities
        # This is for "Pay Off" in debt payment
        self.liability_combo.clear()
        payoff_targets = []
        
        # Add liabilities
        if liabilities:
            payoff_targets.extend([l['name'] for l in liabilities])
        
        # Add credit accounts (they can also be paid off)
        # We need to get credit accounts from the model
        self.liability_combo.addItems(payoff_targets)
        
        # Update category combo based on current type
        self.on_type_changed(self.type_combo.currentText())
    
    def on_type_changed(self, transaction_type):
        """Update category dropdown based on transaction type"""
        is_transfer = (transaction_type == "Transfer")
        is_debt_payment = (transaction_type == "Debt Payment")
        is_regular = not is_transfer and not is_debt_payment
        
        # Show/hide appropriate frames
        self.regular_frame.setVisible(is_regular)
        self.transfer_frame.setVisible(is_transfer)
        self.debt_frame.setVisible(is_debt_payment)
        
        if is_regular:
            # Filter categories by type
            type_map = {
                "Income": "income",
                "Expense": "expense",
                "Savings": "savings"
            }
            category_type = type_map.get(transaction_type, "expense")
            
            # Get categories matching this type
            filtered_categories = []
            for cat in self.all_categories:
                cat_type = cat.get('type', 'expense')
                if cat_type == category_type:
                    filtered_categories.append(cat['name'])
            
            # Update category combo
            self.category_combo.clear()
            if filtered_categories:
                self.category_combo.addItems(filtered_categories)
            else:
                # Always show at least the General category for that type
                general_name = f"General {transaction_type}"
                self.category_combo.addItem(general_name)
        
        # Update placeholders
        if is_transfer:
            self.title_input.setPlaceholderText("Transfer description (optional)")
            self.amount_input.setPlaceholderText("Amount (positive)")
        elif is_debt_payment:
            self.title_input.setPlaceholderText("Payment description (optional)")
            self.amount_input.setPlaceholderText("Payment amount (positive)")
        else:
            self.title_input.setPlaceholderText("Title")
            if transaction_type == "Income":
                self.amount_input.setPlaceholderText("Amount (positive)")
            elif transaction_type == "Expense":
                self.amount_input.setPlaceholderText("Amount (positive)")
            else:  # Savings
                self.amount_input.setPlaceholderText("Amount (positive)")
    
    def display_transactions(self, transactions):
        """Display all transactions for the day"""
        # Clear existing
        while self.transactions_layout.count():
            child = self.transactions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not transactions:
            no_trans = QLabel("No transactions for this day")
            no_trans.setObjectName("mutedLabel")
            no_trans.setAlignment(Qt.AlignCenter)
            self.transactions_layout.addWidget(no_trans)
        else:
            # Separate pending and posted
            pending = [t for t in transactions if t.get('status') == 'pending']
            posted = [t for t in transactions if t.get('status') != 'pending']
            
            # Show posted first, then pending
            for transaction in posted:
                widget = self.create_transaction_widget(transaction)
                self.transactions_layout.addWidget(widget)
            
            for transaction in pending:
                widget = self.create_transaction_widget(transaction)
                self.transactions_layout.addWidget(widget)
    
    def create_transaction_widget(self, transaction):
        """Create widget for a single transaction"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        # Header row
        header = QHBoxLayout()
        
        title_label = QLabel(transaction.get('title', 'Untitled'))
        title_label.setObjectName("subtitle")
        
        amount = float(transaction.get('amount', 0))
        amount_label = QLabel(f"${abs(amount):.2f}")
        if amount >= 0:
            amount_label.setObjectName("positiveLabel")
        else:
            amount_label.setObjectName("negativeLabel")
        
        header.addWidget(title_label)
        header.addStretch()
        header.addWidget(amount_label)
        layout.addLayout(header)
        
        # Details row
        details = QHBoxLayout()
        
        category = transaction.get('category', 'N/A')
        trans_type = transaction.get('transaction_type', 'Expense')
        
        # Show type and category for regular transactions
        if category not in ["Transfer", "Debt Payment"]:
            type_label = QLabel(f"Type: {trans_type}")
            type_label.setObjectName("mutedLabel")
            details.addWidget(type_label)
            
            category_label = QLabel(f"Category: {category}")
            category_label.setObjectName("mutedLabel")
            details.addWidget(category_label)
        else:
            category_label = QLabel(f"Type: {category}")
            category_label.setObjectName("mutedLabel")
            details.addWidget(category_label)
        
        # Show appropriate account info based on category
        if category == "Transfer":
            from_acc = transaction.get('source_account', 'N/A')
            to_acc = transaction.get('target_account', 'N/A')
            account_label = QLabel(f"From: {from_acc} → To: {to_acc}")
        elif category == "Debt Payment":
            from_acc = transaction.get('source_account', 'N/A')
            liability = transaction.get('target_debt', 'N/A')
            account_label = QLabel(f"From: {from_acc} → Liability: {liability}")
        else:
            account_label = QLabel(f"Account: {transaction.get('account', 'N/A')}")
        account_label.setObjectName("mutedLabel")
        details.addWidget(account_label)
        
        status = transaction.get('status', 'posted')
        status_label = QLabel(f"Status: {status.capitalize()}")
        status_label.setObjectName("mutedLabel")
        details.addWidget(status_label)
        
        details.addStretch()
        layout.addLayout(details)
        
        # Buttons row
        buttons = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_transaction_requested.emit(transaction))
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_transaction_requested.emit(transaction))
        
        buttons.addWidget(edit_btn)
        buttons.addWidget(delete_btn)
        
        # Post button for pending transactions
        if status == 'pending':
            post_btn = QPushButton("Post")
            post_btn.setObjectName("successButton")
            post_btn.clicked.connect(lambda: self.post_transaction_requested.emit(transaction))
            buttons.addWidget(post_btn)
        
        buttons.addStretch()
        layout.addLayout(buttons)
        
        return frame
    
    def get_form_data(self):
        """Get current form values"""
        transaction_type = self.type_combo.currentText()
        
        data = {
            'title': self.title_input.text().strip(),
            'amount': self.amount_input.text().strip(),
            'transaction_type': transaction_type,
            'recurring': self.recurring_checkbox.isChecked()
        }
        
        # Add fields based on transaction type
        if transaction_type == "Transfer":
            data['from_account'] = self.from_account_combo.currentText()
            data['to_account'] = self.to_account_combo.currentText()
            data['category'] = 'Transfer'
        elif transaction_type == "Debt Payment":
            data['from_account'] = self.debt_from_account_combo.currentText()
            data['liability'] = self.liability_combo.currentText()
            data['category'] = 'Debt Payment'
        else:
            # Regular transaction (Income/Expense/Savings)
            data['category'] = self.category_combo.currentText()
            data['account'] = self.account_combo.currentText()
        
        # Add recurring fields if checked
        if data['recurring']:
            data['frequency'] = self.frequency_combo.currentText().lower().replace('-', '')
            data['start_date'] = self.start_date_edit.text().strip()
            data['end_date'] = self.end_date_edit.text().strip()
        
        return data
    
    def clear_form(self):
        """Clear all form inputs"""
        self.title_input.clear()
        self.amount_input.clear()
        self.recurring_checkbox.setChecked(False)
        self.recurring_frame.setVisible(False)
        self.type_combo.setCurrentIndex(0)
    
    def set_edit_mode(self, editing):
        """Switch between add and edit mode"""
        if editing:
            self.add_button.setText("Update Transaction")
        else:
            self.add_button.setText("Add Transaction")
    
    def on_recurring_changed(self, state):
        """Show/hide recurring fields based on checkbox"""
        self.recurring_frame.setVisible(state == 2)  # 2 = Qt.Checked
    
    def update_summary(self, summary):
        """Update the summary labels"""
        self.pending_summary.setText(f"Pending: ${summary['pending']:.2f}")
        self.posted_summary.setText(f"Posted: ${summary['posted']:.2f}")
        self.net_summary.setText(f"Net Total: ${summary['net']:.2f}")
    
    def show_error(self, message):
        """Display error message"""
        QMessageBox.warning(self, "Error", message)
    
    def show_success(self, message):
        """Display success message"""
        QMessageBox.information(self, "Success", message)
    
    def confirm_delete(self, transaction_title):
        """Ask user to confirm deletion"""
        reply = QMessageBox.question(
            self,
            "Delete Transaction",
            f"Are you sure you want to delete '{transaction_title}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def set_dark_mode(self, enabled):
        """Update theme"""
        self.dark_mode = enabled