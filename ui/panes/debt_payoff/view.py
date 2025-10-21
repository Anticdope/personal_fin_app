"""
Debt Payoff Pane - View
Pure UI for displaying debt payoff information
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QScrollArea, QProgressBar, QPushButton)
from PySide6.QtCore import Qt, Signal


class DebtPayoffView(QWidget):
    """View: Pure UI for debt payoff display"""
    
    # Signals
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("💳 Debt Payoff Tracker")
        title.setObjectName("paneTitle")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setObjectName("secondaryButton")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Summary section
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summaryFrame")
        self.summary_layout = QVBoxLayout(self.summary_frame)
        layout.addWidget(self.summary_frame)
        
        # Debts scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("debtScrollArea")
        
        self.debts_container = QWidget()
        self.debts_layout = QVBoxLayout(self.debts_container)
        self.debts_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.debts_container)
        layout.addWidget(scroll)
        
        # Footer note
        note = QLabel(
            "💡 Tip: Projections assume minimum payments with no additional charges. "
            "Pay more than the minimum to save on interest and become debt-free faster!"
        )
        note.setObjectName("mutedLabel")
        note.setWordWrap(True)
        layout.addWidget(note)
    
    def display_summary(self, summary_data):
        """Display the summary statistics"""
        # Clear existing
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not summary_data['has_debts']:
            # No debts - celebration message
            celebration = QLabel("🎉 Congratulations! You have no debts!")
            celebration.setObjectName("positiveLabel")
            celebration.setAlignment(Qt.AlignCenter)
            self.summary_layout.addWidget(celebration)
            return
        
        # Summary stats in a grid for better spacing
        stats_widget = QWidget()
        stats_grid = QHBoxLayout(stats_widget)
        stats_grid.setSpacing(20)
        
        # Total debt
        debt_frame = QFrame()
        debt_frame.setObjectName("summaryStatFrame")
        debt_layout = QVBoxLayout(debt_frame)
        debt_layout.setSpacing(2)
        debt_label = QLabel("Total Debt")
        debt_label.setObjectName("mutedLabel")
        debt_label.setAlignment(Qt.AlignCenter)
        debt_value = QLabel(f"${summary_data['total_debt']:,.2f}")
        debt_value.setObjectName("negativeLabel")
        debt_value.setAlignment(Qt.AlignCenter)
        debt_layout.addWidget(debt_label)
        debt_layout.addWidget(debt_value)
        stats_grid.addWidget(debt_frame)
        
        # Paid off
        paid_frame = QFrame()
        paid_frame.setObjectName("summaryStatFrame")
        paid_layout = QVBoxLayout(paid_frame)
        paid_layout.setSpacing(2)
        paid_label = QLabel("Paid Off")
        paid_label.setObjectName("mutedLabel")
        paid_label.setAlignment(Qt.AlignCenter)
        paid_value = QLabel(f"${summary_data['total_paid_off']:,.2f}")
        paid_value.setObjectName("positiveLabel")
        paid_value.setAlignment(Qt.AlignCenter)
        paid_layout.addWidget(paid_label)
        paid_layout.addWidget(paid_value)
        stats_grid.addWidget(paid_frame)
        
        # Monthly payments
        payment_frame = QFrame()
        payment_frame.setObjectName("summaryStatFrame")
        payment_layout = QVBoxLayout(payment_frame)
        payment_layout.setSpacing(2)
        payment_label = QLabel("Monthly Payments")
        payment_label.setObjectName("mutedLabel")
        payment_label.setAlignment(Qt.AlignCenter)
        payment_value = QLabel(f"${summary_data['total_monthly_payments']:,.2f}")
        payment_value.setObjectName("subtitle")
        payment_value.setAlignment(Qt.AlignCenter)
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(payment_value)
        stats_grid.addWidget(payment_frame)
        
        # Projected interest
        if summary_data['total_projected_interest'] > 0:
            interest_frame = QFrame()
            interest_frame.setObjectName("summaryStatFrame")
            interest_layout = QVBoxLayout(interest_frame)
            interest_layout.setSpacing(2)
            interest_label = QLabel("Total Interest")
            interest_label.setObjectName("mutedLabel")
            interest_label.setAlignment(Qt.AlignCenter)
            interest_value = QLabel(f"${summary_data['total_projected_interest']:,.2f}")
            interest_value.setObjectName("warningLabel")
            interest_value.setAlignment(Qt.AlignCenter)
            interest_layout.addWidget(interest_label)
            interest_layout.addWidget(interest_value)
            stats_grid.addWidget(interest_frame)
        
        stats_grid.addStretch()
        
        self.summary_layout.addWidget(stats_widget)
        
        # Debt count
        count_label = QLabel(f"Tracking {summary_data['debt_count']} debt(s)")
        count_label.setObjectName("mutedLabel")
        self.summary_layout.addWidget(count_label)
    
    def display_debts(self, debts_with_projections):
        """
        Display debt cards with projections
        
        Args:
            debts_with_projections: list of tuples (debt_dict, projection_dict)
        """
        # Clear existing
        while self.debts_layout.count():
            child = self.debts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not debts_with_projections:
            no_debts = QLabel("No debts to display")
            no_debts.setObjectName("mutedLabel")
            no_debts.setAlignment(Qt.AlignCenter)
            self.debts_layout.addWidget(no_debts)
            return
        
        for debt, projection in debts_with_projections:
            card = self.create_debt_card(debt, projection)
            self.debts_layout.addWidget(card)
    
    def create_debt_card(self, debt, projection):
        """Create a card widget for a single debt"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        # Header
        header = QHBoxLayout()
        
        name_label = QLabel(debt['name'])
        name_label.setObjectName("subtitle")
        
        type_label = QLabel(f"({debt['source_type']})")
        type_label.setObjectName("mutedLabel")
        
        header.addWidget(name_label)
        header.addWidget(type_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Balance info
        balance_layout = QHBoxLayout()
        
        current_balance = QLabel(f"Current: ${debt['balance']:,.2f}")
        current_balance.setObjectName("negativeLabel")
        balance_layout.addWidget(current_balance)
        
        original_balance = QLabel(f"Original: ${debt['original_balance']:,.2f}")
        original_balance.setObjectName("mutedLabel")
        balance_layout.addWidget(original_balance)
        
        balance_layout.addStretch()
        layout.addLayout(balance_layout)
        
        # Payment info
        payment_layout = QHBoxLayout()
        
        if debt['interest_rate'] > 0:
            interest_label = QLabel(f"Interest: {debt['interest_rate']:.2f}%")
            interest_label.setObjectName("mutedLabel")
            payment_layout.addWidget(interest_label)
        
        if debt['minimum_payment'] > 0:
            payment_label = QLabel(f"Min Payment: ${debt['minimum_payment']:,.2f}")
            payment_label.setObjectName("mutedLabel")
            payment_layout.addWidget(payment_label)
        
        # Payment due day indicator
        if debt.get('payment_due_day'):
            due_day_label = QLabel(f"📅 Due: Day {debt['payment_due_day']}")
            due_day_label.setObjectName("mutedLabel")
            due_day_label.setStyleSheet("font-weight: bold;")
            payment_layout.addWidget(due_day_label)
        
        payment_layout.addStretch()
        layout.addLayout(payment_layout)
        
        # Progress bar
        paid_off = debt['original_balance'] - debt['balance']
        progress_percent = (paid_off / debt['original_balance'] * 100) if debt['original_balance'] > 0 else 0
        
        progress_label = QLabel(f"Progress: ${paid_off:,.2f} paid off ({progress_percent:.1f}%)")
        progress_label.setObjectName("mutedLabel")
        layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(progress_percent))
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(20)
        layout.addWidget(progress_bar)
        
        # Payoff projection
        if projection['is_valid'] and projection['months_to_payoff'] is not None:
            projection_layout = QVBoxLayout()
            projection_layout.setSpacing(5)
            
            # Payoff date
            payoff_date_str = projection['payoff_date'].strftime("%B %Y") if projection['payoff_date'] else "Unknown"
            date_label = QLabel(f"📅 Estimated Payoff: {payoff_date_str}")
            date_label.setObjectName("positiveLabel")
            projection_layout.addWidget(date_label)
            
            # Months remaining
            months_label = QLabel(f"⏱️ {projection['months_to_payoff']} months remaining")
            months_label.setObjectName("mutedLabel")
            projection_layout.addWidget(months_label)
            
            # Total interest
            if projection['total_interest'] and projection['total_interest'] > 0:
                interest_label = QLabel(f"💰 Total Interest: ${projection['total_interest']:,.2f}")
                interest_label.setObjectName("warningLabel")
                projection_layout.addWidget(interest_label)
            
            layout.addLayout(projection_layout)
        
        elif not projection['is_valid']:
            # Show warning
            warning = QLabel(f"⚠️ {projection['warning_message']}")
            warning.setObjectName("negativeLabel")
            warning.setWordWrap(True)
            layout.addWidget(warning)
        
        else:
            # No payment set
            note = QLabel("ℹ️ Set a minimum payment in Manage Accounts to see projections")
            note.setObjectName("mutedLabel")
            note.setWordWrap(True)
            layout.addWidget(note)
        
        return frame
    
    def show_no_debts_message(self):
        """Display when there are no debts"""
        # Clear debts area
        while self.debts_layout.count():
            child = self.debts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        message = QLabel("🎉 You have no debts!\n\nGreat job managing your finances!")
        message.setObjectName("positiveLabel")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        self.debts_layout.addWidget(message)
    
    def set_dark_mode(self, enabled):
        """Update theme"""
        self.dark_mode = enabled