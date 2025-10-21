"""
Debt Payoff Pane - Model
Handles debt calculations and data aggregation
"""
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DebtPayoffModel:
    """Model: Business logic for debt payoff calculations"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_all_debts(self):
        """
        Aggregate all debts from credit accounts and liabilities
        Returns: list of debt dictionaries
        """
        debts = []
        
        # Get credit accounts with debt
        for account in self.data_manager.accounts:
            if account.get('type') == 'credit' and account.get('balance', 0) > 0:
                debts.append({
                    'name': account['name'],
                    'source_type': 'Credit Account',
                    'balance': account.get('balance', 0),
                    'original_balance': account.get('original_balance', account.get('balance', 0)),
                    'interest_rate': account.get('interest_rate', 0),
                    'minimum_payment': account.get('minimum_payment', 0),
                    'payment_due_day': account.get('payment_due_day'),
                    'id': account.get('id')
                })
        
        # Get liabilities
        for liability in self.data_manager.liabilities:
            if liability.get('balance', 0) > 0:
                debts.append({
                    'name': liability['name'],
                    'source_type': 'Liability',
                    'balance': liability.get('balance', 0),
                    'original_balance': liability.get('original_balance', liability.get('balance', 0)),
                    'interest_rate': liability.get('interest_rate', 0),
                    'minimum_payment': liability.get('minimum_payment', 0),
                    'payment_due_day': liability.get('payment_due_day'),
                    'id': liability.get('id')
                })
        
        return debts
    
    def calculate_total_debt(self):
        """Calculate total current debt"""
        debts = self.get_all_debts()
        return sum(d['balance'] for d in debts)
    
    def calculate_total_paid_off(self):
        """Calculate total amount paid off across all debts"""
        debts = self.get_all_debts()
        total_original = sum(d['original_balance'] for d in debts)
        total_current = sum(d['balance'] for d in debts)
        return total_original - total_current
    
    def calculate_payoff_projection(self, balance, interest_rate, monthly_payment):
        """
        Calculate payoff timeline using amortization formula
        
        Args:
            balance: Current debt balance
            interest_rate: Annual interest rate (as percentage, e.g., 18.5)
            monthly_payment: Monthly payment amount
            
        Returns:
            dict with:
                - months_to_payoff: int or None
                - total_interest: float
                - payoff_date: datetime or None
                - is_valid: bool
                - warning_message: str or None
        """
        if balance <= 0:
            return {
                'months_to_payoff': 0,
                'total_interest': 0.0,
                'payoff_date': datetime.now(),
                'is_valid': True,
                'warning_message': None
            }
        
        if monthly_payment <= 0:
            return {
                'months_to_payoff': None,
                'total_interest': None,
                'payoff_date': None,
                'is_valid': False,
                'warning_message': 'No payment set'
            }
        
        # Convert annual rate to monthly decimal
        monthly_rate = (interest_rate / 100) / 12
        
        if monthly_rate == 0:
            # No interest - simple division
            months = math.ceil(balance / monthly_payment)
            payoff_date = datetime.now() + relativedelta(months=months)
            return {
                'months_to_payoff': months,
                'total_interest': 0.0,
                'payoff_date': payoff_date,
                'is_valid': True,
                'warning_message': None
            }
        
        # Special case: payment exceeds balance
        # Will pay off in 1 month with only 1 month of interest
        monthly_interest = balance * monthly_rate
        if monthly_payment >= balance:
            payoff_date = datetime.now() + relativedelta(months=1)
            return {
                'months_to_payoff': 1,
                'total_interest': monthly_interest,
                'payoff_date': payoff_date,
                'is_valid': True,
                'warning_message': None
            }
        
        # Check if payment covers interest
        if monthly_payment <= monthly_interest:
            return {
                'months_to_payoff': None,
                'total_interest': None,
                'payoff_date': None,
                'is_valid': False,
                'warning_message': f'Payment (${monthly_payment:.2f}) does not cover monthly interest (${monthly_interest:.2f})'
            }
        
        # Amortization formula: n = -log(1 - (r*P/M)) / log(1 + r)
        # Where: n = months, r = monthly rate, P = principal, M = monthly payment
        try:
            numerator = math.log(1 - (monthly_rate * balance / monthly_payment))
            denominator = math.log(1 + monthly_rate)
            months = -numerator / denominator
            months = math.ceil(months)
            
            # Calculate total interest paid
            total_paid = monthly_payment * months
            total_interest = total_paid - balance
            
            # Calculate payoff date
            payoff_date = datetime.now() + relativedelta(months=months)
            
            return {
                'months_to_payoff': months,
                'total_interest': total_interest,
                'payoff_date': payoff_date,
                'is_valid': True,
                'warning_message': None
            }
        except (ValueError, ZeroDivisionError):
            return {
                'months_to_payoff': None,
                'total_interest': None,
                'payoff_date': None,
                'is_valid': False,
                'warning_message': 'Unable to calculate payoff'
            }
    
    def get_debt_summary(self):
        """
        Get comprehensive debt summary
        Returns: dict with aggregated statistics
        """
        debts = self.get_all_debts()
        
        if not debts:
            return {
                'total_debt': 0.0,
                'total_paid_off': 0.0,
                'debt_count': 0,
                'total_monthly_payments': 0.0,
                'total_projected_interest': 0.0,
                'has_debts': False
            }
        
        total_debt = sum(d['balance'] for d in debts)
        total_original = sum(d['original_balance'] for d in debts)
        total_paid_off = total_original - total_debt
        total_monthly_payments = sum(d['minimum_payment'] for d in debts)
        
        # Calculate total projected interest
        total_projected_interest = 0.0
        for debt in debts:
            projection = self.calculate_payoff_projection(
                debt['balance'],
                debt['interest_rate'],
                debt['minimum_payment']
            )
            if projection['is_valid'] and projection['total_interest']:
                total_projected_interest += projection['total_interest']
        
        return {
            'total_debt': total_debt,
            'total_paid_off': total_paid_off,
            'debt_count': len(debts),
            'total_monthly_payments': total_monthly_payments,
            'total_projected_interest': total_projected_interest,
            'has_debts': True
        }
    
    def format_payoff_date(self, payoff_date):
        """Format payoff date as readable string"""
        if payoff_date is None:
            return "Unable to calculate"
        return payoff_date.strftime("%B %Y")
    
    def calculate_progress_percentage(self, original_balance, current_balance):
        """Calculate percentage of debt paid off"""
        if original_balance <= 0:
            return 0.0
        
        paid_off = original_balance - current_balance
        percentage = (paid_off / original_balance) * 100
        return max(0.0, min(100.0, percentage))