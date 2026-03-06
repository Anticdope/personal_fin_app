"""
tests/test_services/test_calculation_service.py

FIXED - Tests now match your actual CalculationService methods
"""
import pytest
from data.services.calculation_service import CalculationService
from data.repositories.account_repository import AccountRepository
from data.repositories.asset_repository import AssetRepository
from data.repositories.liability_repository import LiabilityRepository
from data.repositories.transaction_repository import TransactionRepository
from data.repositories.category_repository import CategoryRepository


class TestCalculationService:
    """Test calculation service for summaries and net worth"""
    
    @pytest.fixture
    def repos(self, temp_data_dir):
        """Create all repository instances"""
        account_repo = AccountRepository(temp_data_dir)
        asset_repo = AssetRepository(temp_data_dir)
        liability_repo = LiabilityRepository(temp_data_dir)
        transaction_repo = TransactionRepository(temp_data_dir)
        category_repo = CategoryRepository(temp_data_dir)
        
        return {
            'account': account_repo,
            'asset': asset_repo,
            'liability': liability_repo,
            'transaction': transaction_repo,
            'category': category_repo
        }
    
    @pytest.fixture
    def service(self, repos):
        """Create calculation service instance"""
        return CalculationService(
            repos['account'],
            repos['asset'],
            repos['liability'],
            repos['transaction'],
            repos['category']
        )
    
    # ===== NET WORTH TESTS =====
    
    def test_net_worth_with_no_data(self, service):
        """Test net worth calculation with no accounts/assets/liabilities"""
        net_worth = service.calculate_net_worth()
        
        assert net_worth == 0.0
    
    def test_net_worth_with_only_accounts(self, service, repos):
        """Test net worth with only account balances"""
        repos['account'].add({
            'name': 'Checking',
            'type': 'debit',
            'balance': 5000.0
        })
        repos['account'].add({
            'name': 'Savings',
            'type': 'debit',
            'balance': 10000.0
        })
        
        net_worth = service.calculate_net_worth()
        
        assert net_worth == 15000.0
    
    def test_net_worth_includes_assets(self, service, repos):
        """Test that net worth includes asset values"""
        repos['account'].add({
            'name': 'Checking',
            'type': 'debit',
            'balance': 5000.0
        })
        repos['asset'].add({
            'name': 'House',
            'value': 300000.0
        })
        repos['asset'].add({
            'name': 'Car',
            'value': 25000.0
        })
        
        net_worth = service.calculate_net_worth()
        
        # 5000 + 300000 + 25000 = 330000
        assert net_worth == 330000.0
    
    def test_net_worth_subtracts_liabilities(self, service, repos):
        """Test that net worth subtracts liabilities"""
        repos['account'].add({
            'name': 'Checking',
            'type': 'debit',
            'balance': 10000.0
        })
        repos['asset'].add({
            'name': 'House',
            'value': 300000.0
        })
        repos['liability'].add({
            'name': 'Mortgage',
            'balance': 250000.0
        })
        
        net_worth = service.calculate_net_worth()
        
        # 10000 + 300000 - 250000 = 60000
        assert net_worth == 60000.0
    
    def test_net_worth_with_credit_card_debt(self, service, repos):
        """Test that credit card balances reduce net worth"""
        repos['account'].add({
            'name': 'Checking',
            'type': 'debit',
            'balance': 5000.0
        })
        repos['account'].add({
            'name': 'Credit Card',
            'type': 'credit',
            'balance': 2000.0  # Debt
        })
        
        net_worth = service.calculate_net_worth()
        
        # 5000 - 2000 = 3000
        assert net_worth == 3000.0
    
    def test_net_worth_can_be_negative(self, service, repos):
        """Test that net worth can be negative (more debt than assets)"""
        repos['account'].add({
            'name': 'Checking',
            'type': 'debit',
            'balance': 1000.0
        })
        repos['liability'].add({
            'name': 'Student Loan',
            'balance': 50000.0
        })
        
        net_worth = service.calculate_net_worth()
        
        # 1000 - 50000 = -49000
        assert net_worth == -49000.0
    
    # ===== CATEGORY SPENDING TESTS =====
    
    def test_category_spending_with_no_transactions(self, service):
        """Test category spending with no transactions"""
        spending = service.calculate_category_spending(2024, 1)
        
        assert spending == {}
    
    def test_category_spending_groups_by_category(self, service, repos):
        """Test that category spending correctly groups transactions"""
        month_data = {
            '1': [
                {'amount': -100.0, 'category': 'Groceries', 'status': 'posted'},
                {'amount': -50.0, 'category': 'Groceries', 'status': 'posted'},
                {'amount': -200.0, 'category': 'Rent', 'status': 'posted'}
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)
        
        spending = service.calculate_category_spending(2024, 1)
        
        assert 'Groceries' in spending
        assert spending['Groceries'] == 150.0  # abs(-100) + abs(-50)
        assert spending['Rent'] == 200.0
    
    def test_category_spending_only_counts_expenses(self, service, repos):
        """Test that category spending only counts negative amounts (expenses)"""
        month_data = {
            '1': [
                {'amount': -100.0, 'category': 'Food', 'status': 'posted'},
                {'amount': 500.0, 'category': 'Income', 'status': 'posted'}  # Should not count
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)
        
        spending = service.calculate_category_spending(2024, 1)
        
        assert 'Food' in spending
        assert spending['Food'] == 100.0
        assert 'Income' not in spending  # Positive amounts excluded
    
    def test_category_spending_ignores_pending(self, service, repos):
        """Test that pending transactions are excluded"""
        month_data = {
            '1': [
                {'amount': -100.0, 'category': 'Food', 'status': 'posted'},
                {'amount': -50.0, 'category': 'Food', 'status': 'pending'}
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)
        
        spending = service.calculate_category_spending(2024, 1)
        
        # Should only count posted transaction
        assert spending['Food'] == 100.0
    
    # ===== BUDGET STATUS TESTS =====
    
    def test_budget_status_with_no_categories(self, service):
        """Test budget status with no categories"""
        status = service.calculate_budget_status(2024, 1)
        
        assert status == []
    
    def test_budget_status_shows_spending_vs_budget(self, service, repos):
        """Test that budget status compares spending to budget"""
        # Add category with budget
        repos['category'].add({
            'name': 'Groceries',
            'type': 'expense',
            'budget': 500.0,
            'color': '#00FF00'
        })
        
        # Add spending
        month_data = {
            '1': [
                {'amount': -300.0, 'category': 'Groceries', 'status': 'posted'}
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)
        
        status = service.calculate_budget_status(2024, 1)
        
        assert len(status) == 1
        assert status[0]['name'] == 'Groceries'
        assert status[0]['budget'] == 500.0
        assert status[0]['spent'] == 300.0
        assert status[0]['remaining'] == 200.0
        assert status[0]['percentage'] == 60.0  # 300/500 * 100
        assert status[0]['over_budget'] == False
    
    def test_budget_status_detects_over_budget(self, service, repos):
        """Test that over-budget categories are detected"""
        repos['category'].add({
            'name': 'Dining',
            'type': 'expense',
            'budget': 200.0,
            'color': '#FF0000'
        })
        
        # Spend more than budget
        month_data = {
            '1': [
                {'amount': -250.0, 'category': 'Dining', 'status': 'posted'}
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)
        
        status = service.calculate_budget_status(2024, 1)
        
        assert status[0]['spent'] == 250.0
        assert status[0]['remaining'] == -50.0
        assert status[0]['over_budget'] == True
    
    # ===== TOTAL MONTHLY BUDGET TEST =====
    
    def test_total_monthly_budget_sums_categories(self, service, repos):
        """Test that total monthly budget sums all category budgets"""
        repos['category'].add({
            'name': 'Groceries',
            'type': 'expense',
            'budget': 500.0
        })
        repos['category'].add({
            'name': 'Gas',
            'type': 'expense',
            'budget': 200.0
        })
        repos['category'].add({
            'name': 'Transfer',
            'type': 'special',
            'special': True,
            'budget': 0.0
        })
        
        total = service.calculate_total_monthly_budget()
        
        # Should sum non-special categories: 500 + 200 = 700
        assert total == 700.0
    
    # ===== DAY TOTALS TESTS =====
    
    def test_day_totals_separate_posted_and_pending(self, service, repos):
        """Test that day totals separate posted and pending transactions"""
        month_data = {
            '15': [
                {'amount': -100.0, 'category': 'Food', 'status': 'posted'},
                {'amount': -50.0, 'category': 'Gas', 'status': 'posted'},
                {'amount': -75.0, 'category': 'Shopping', 'status': 'pending'}
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)
        
        totals = service.calculate_day_totals_separate(2024, 1, 15)
        
        assert totals['posted'] == -150.0  # -100 + -50
        assert totals['pending'] == -75.0
        assert totals['net'] == -225.0  # -150 + -75
    
    def test_day_totals_with_no_transactions(self, service):
        """Test day totals with no transactions"""
        totals = service.calculate_day_totals_separate(2024, 1, 15)
        
        assert totals['posted'] == 0.0
        assert totals['pending'] == 0.0
        assert totals['net'] == 0.0
    
    def test_day_totals_exclude_transfers(self, service, repos):
        """Test that transfers are excluded from day totals"""
        month_data = {
            '15': [
                {'amount': -100.0, 'category': 'Food', 'status': 'posted'},
                {'amount': 200.0, 'category': 'Transfer', 'status': 'posted'}  # Should be excluded
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)
        
        totals = service.calculate_day_totals_separate(2024, 1, 15)
        
        # Should only count Food, not Transfer
        assert totals['posted'] == -100.0
    
    # ===== YTD SUMMARY TESTS =====
    
    def test_ytd_summary_with_no_data(self, service):
        """Test YTD summary with no transactions"""
        summary = service.calculate_ytd_summary(2024, 1)
        
        assert summary['income'] == 0.0
        assert summary['expenses'] == 0.0
        assert summary['net'] == 0.0
    
    def test_ytd_summary_calculates_correctly(self, service, repos):
        """Test YTD summary across multiple months"""
        # January
        jan_data = {
            '1': [
                {'amount': 5000.0, 'status': 'posted'},
                {'amount': -1500.0, 'status': 'posted'}
            ]
        }
        repos['transaction'].save_month_data(2024, 1, jan_data)
        
        # February
        feb_data = {
            '1': [
                {'amount': 5000.0, 'status': 'posted'},
                {'amount': -1200.0, 'status': 'posted'}
            ]
        }
        repos['transaction'].save_month_data(2024, 2, feb_data)
        
        # Get YTD through February
        summary = service.calculate_ytd_summary(2024, 2)
        
        assert summary['income'] == 10000.0  # 5000 + 5000
        assert summary['expenses'] == 2700.0  # 1500 + 1200
        assert summary['net'] == 7300.0  # 10000 - 2700
    
    def test_ytd_summary_only_includes_up_to_current_month(self, service, repos):
        """Test that YTD only includes months up to specified month"""
        # January
        jan_data = {
            '1': [{'amount': 1000.0, 'status': 'posted'}]
        }
        repos['transaction'].save_month_data(2024, 1, jan_data)
        
        # March (should not be included when asking for Feb YTD)
        mar_data = {
            '1': [{'amount': 5000.0, 'status': 'posted'}]
        }
        repos['transaction'].save_month_data(2024, 3, mar_data)
        
        # Get YTD through January
        summary = service.calculate_ytd_summary(2024, 1)
        
        # Should only include January
        assert summary['income'] == 1000.0


    # ===== CALCULATE_DAY_TOTAL TESTS =====

    def test_day_total_sums_all_transactions(self, service, repos):
        """Test that day total sums all non-transfer transactions"""
        month_data = {
            '10': [
                {'amount': -50.0, 'category': 'Food', 'status': 'posted'},
                {'amount': -30.0, 'category': 'Gas', 'status': 'posted'},
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)

        total = service.calculate_day_total(2024, 1, 10)

        assert total == -80.0

    def test_day_total_excludes_transfers(self, service, repos):
        """Test that transfers are excluded from day total"""
        month_data = {
            '10': [
                {'amount': -50.0, 'category': 'Food', 'status': 'posted'},
                {'amount': 500.0, 'category': 'Transfer', 'status': 'posted'},
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)

        total = service.calculate_day_total(2024, 1, 10)

        assert total == -50.0

    def test_day_total_includes_income(self, service, repos):
        """Test that positive amounts (income) are included"""
        month_data = {
            '10': [
                {'amount': 1000.0, 'category': 'Income', 'status': 'posted'},
                {'amount': -50.0, 'category': 'Food', 'status': 'posted'},
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)

        total = service.calculate_day_total(2024, 1, 10)

        assert total == 950.0

    def test_day_total_with_no_transactions(self, service):
        """Test day total with no transactions returns zero"""
        total = service.calculate_day_total(2024, 1, 10)
        assert total == 0.0

    def test_day_total_includes_pending(self, service, repos):
        """Test that pending transactions ARE included in day_total (unlike day_totals_separate)"""
        month_data = {
            '10': [
                {'amount': -50.0, 'category': 'Food', 'status': 'posted'},
                {'amount': -25.0, 'category': 'Food', 'status': 'pending'},
            ]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)

        total = service.calculate_day_total(2024, 1, 10)

        assert total == -75.0

    # ===== BUDGET STATUS SPECIAL CATEGORIES =====

    def test_budget_status_skips_special_categories(self, service, repos):
        """Test that special categories are excluded from budget status"""
        repos['category'].add({
            'name': 'Transfer',
            'type': 'special',
            'special': True,
            'budget': 0.0,
            'color': '#000000'
        })
        repos['category'].add({
            'name': 'Groceries',
            'type': 'expense',
            'budget': 500.0,
            'color': '#00FF00'
        })

        status = service.calculate_budget_status(2024, 1)

        names = [s['name'] for s in status]
        assert 'Transfer' not in names
        assert 'Groceries' in names

    def test_budget_status_zero_budget_percentage_is_zero(self, service, repos):
        """Test category with no budget set shows 0% even with spending"""
        repos['category'].add({
            'name': 'Misc',
            'type': 'expense',
            'budget': 0.0,
            'color': '#AAAAAA'
        })
        month_data = {
            '1': [{'amount': -50.0, 'category': 'Misc', 'status': 'posted'}]
        }
        repos['transaction'].save_month_data(2024, 1, month_data)

        status = service.calculate_budget_status(2024, 1)

        misc = next(s for s in status if s['name'] == 'Misc')
        assert misc['percentage'] == 0
        assert misc['over_budget'] is False


# Run with: pytest tests/test_services/test_calculation_service.py -v