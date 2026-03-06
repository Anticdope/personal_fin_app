"""
tests/test_services/test_transaction_service.py

Tests for transaction service - this will catch balance calculation bugs
"""
import pytest
from data.services.transaction_service import TransactionService
from data.repositories.account_repository import AccountRepository
from data.repositories.liability_repository import LiabilityRepository
from data.repositories.asset_repository import AssetRepository
from data.audit.audit_repository import AuditLogRepository
from data.audit.audit_service import AuditService


class TestTransactionService:
    """Test transaction service balance calculations"""
    
    @pytest.fixture
    def repos(self, temp_data_dir):
        """Create repository instances"""
        account_repo = AccountRepository(temp_data_dir)
        liability_repo = LiabilityRepository(temp_data_dir)
        asset_repo = AssetRepository(temp_data_dir)
        return account_repo, liability_repo, asset_repo
    
    @pytest.fixture
    def service(self, repos):
        """Create transaction service instance"""
        account_repo, liability_repo, asset_repo = repos
        return TransactionService(account_repo, asset_repo, liability_repo)
    
    # ===== DEBIT ACCOUNT TESTS =====
    
    def test_debit_account_expense_decreases_balance(self, service, repos, sample_account):
        """Test that expenses decrease debit account balance"""
        account_repo, _, _ = repos
        account_repo.add(sample_account)
        transaction = {
            'id': 'txn-1', 'title': 'Groceries',
            'amount': -50.0, 'category': 'Food', 'account': 'Test Checking'
        }
        service.apply_transaction_to_balance(transaction)
        updated_account = account_repo.get_by_name('Test Checking')
        assert updated_account['balance'] == 950.0
    
    def test_debit_account_income_increases_balance(self, service, repos, sample_account):
        """Test that income increases debit account balance"""
        account_repo, _, _ = repos
        account_repo.add(sample_account)
        transaction = {
            'id': 'txn-2', 'title': 'Paycheck',
            'amount': 500.0, 'category': 'Income', 'account': 'Test Checking'
        }
        service.apply_transaction_to_balance(transaction)
        updated_account = account_repo.get_by_name('Test Checking')
        assert updated_account['balance'] == 1500.0
    
    # ===== CREDIT ACCOUNT TESTS =====
    
    def test_credit_account_expense_increases_balance(self, service, repos, sample_credit_account):
        """Test that expenses (charges) increase credit card balance (debt)"""
        account_repo, _, _ = repos
        account_repo.add(sample_credit_account)
        transaction = {
            'id': 'txn-3', 'title': 'Amazon Purchase',
            'amount': -100.0, 'category': 'Shopping', 'account': 'Test Credit Card'
        }
        service.apply_transaction_to_balance(transaction)
        updated_account = account_repo.get_by_name('Test Credit Card')
        assert updated_account['balance'] == 600.0
    
    def test_credit_account_payment_decreases_balance(self, service, repos, sample_credit_account):
        """Test that payments decrease credit card balance (debt)"""
        account_repo, _, _ = repos
        account_repo.add(sample_credit_account)
        transaction = {
            'id': 'txn-4', 'title': 'Credit Card Payment',
            'amount': 100.0, 'category': 'Payment', 'account': 'Test Credit Card'
        }
        service.apply_transaction_to_balance(transaction)
        updated_account = account_repo.get_by_name('Test Credit Card')
        assert updated_account['balance'] == 400.0
    
    def test_credit_account_refund_decreases_balance(self, service, repos, sample_credit_account):
        """Test that refunds (positive expense) decrease credit balance"""
        account_repo, _, _ = repos
        account_repo.add(sample_credit_account)
        transaction = {
            'id': 'txn-5', 'title': 'Return Item',
            'amount': 50.0, 'category': 'Shopping', 'account': 'Test Credit Card'
        }
        service.apply_transaction_to_balance(transaction)
        updated_account = account_repo.get_by_name('Test Credit Card')
        assert updated_account['balance'] == 450.0
    
    # ===== TRANSFER TESTS =====
    
    def test_transfer_between_debit_accounts(self, service, repos):
        """Test transfer from one debit account to another"""
        account_repo, _, _ = repos
        account_repo.add({'id': 'acc-checking', 'name': 'Checking', 'type': 'debit', 'balance': 1000.0})
        account_repo.add({'id': 'acc-savings', 'name': 'Savings', 'type': 'debit', 'balance': 500.0})
        transaction = {
            'id': 'txn-6', 'title': 'Transfer to Savings', 'amount': 200.0,
            'category': 'Transfer', 'source_account': 'Checking', 'target_account': 'Savings'
        }
        service.apply_transaction_to_balance(transaction)
        assert account_repo.get_by_name('Checking')['balance'] == 800.0
        assert account_repo.get_by_name('Savings')['balance'] == 700.0
    
    # ===== DEBT PAYMENT TESTS =====
    
    def test_debt_payment_to_credit_card(self, service, repos):
        """Test paying off credit card from checking account"""
        account_repo, _, _ = repos
        account_repo.add({'id': 'acc-checking', 'name': 'Checking', 'type': 'debit', 'balance': 1000.0})
        account_repo.add({'id': 'acc-credit', 'name': 'Credit Card', 'type': 'credit', 'balance': 500.0})
        transaction = {
            'id': 'txn-7', 'title': 'CC Payment', 'amount': 100.0,
            'category': 'Debt Payment', 'source_account': 'Checking',
            'target_debt': 'Credit Card', 'target_type': 'credit'
        }
        service.apply_transaction_to_balance(transaction)
        assert account_repo.get_by_name('Checking')['balance'] == 900.0
        assert account_repo.get_by_name('Credit Card')['balance'] == 400.0
    
    def test_debt_payment_to_liability(self, service, repos):
        """Test paying off liability from checking account"""
        account_repo, liability_repo, _ = repos
        account_repo.add({'id': 'acc-checking', 'name': 'Checking', 'type': 'debit', 'balance': 2000.0})
        liability_repo.add({'id': 'lib-loan', 'name': 'Car Loan', 'balance': 15000.0})
        transaction = {
            'id': 'txn-8', 'title': 'Loan Payment', 'amount': 500.0,
            'category': 'Debt Payment', 'source_account': 'Checking',
            'target_debt': 'Car Loan', 'target_type': 'liability'
        }
        service.apply_transaction_to_balance(transaction)
        assert account_repo.get_by_name('Checking')['balance'] == 1500.0
        assert liability_repo.get_by_name('Car Loan')['balance'] == 14500.0
    
    # ===== REVERSE TRANSACTION TESTS =====
    
    def test_reverse_debit_expense(self, service, repos, sample_account):
        """Test reversing an expense transaction"""
        account_repo, _, _ = repos
        account_repo.add(sample_account)
        transaction = {'amount': -50.0, 'account': 'Test Checking'}
        service.apply_transaction_to_balance(transaction)
        service.reverse_transaction_from_balance(transaction)
        assert account_repo.get_by_name('Test Checking')['balance'] == 1000.0
    
    def test_reverse_credit_charge(self, service, repos, sample_credit_account):
        """Test reversing a credit card charge"""
        account_repo, _, _ = repos
        account_repo.add(sample_credit_account)
        transaction = {'amount': -100.0, 'account': 'Test Credit Card'}
        service.apply_transaction_to_balance(transaction)
        service.reverse_transaction_from_balance(transaction)
        assert account_repo.get_by_name('Test Credit Card')['balance'] == 500.0


# ============================================================
# EXTENDED TESTS - Transfers, debt payments, reversals, edge cases
# ============================================================

@pytest.fixture
def ext_repos(tmp_path):
    return {
        'account': AccountRepository(tmp_path),
        'asset': AssetRepository(tmp_path),
        'liability': LiabilityRepository(tmp_path),
        'audit_repo': AuditLogRepository(tmp_path),
    }


@pytest.fixture
def ext_service(ext_repos):
    audit_service = AuditService(ext_repos['audit_repo'])
    return TransactionService(
        ext_repos['account'], ext_repos['asset'], ext_repos['liability'], audit_service
    )


@pytest.fixture
def ext_service_no_audit(ext_repos):
    return TransactionService(
        ext_repos['account'], ext_repos['asset'], ext_repos['liability'], audit_service=None
    )


def _add_debit(repos, name, balance=1000.0):
    return repos['account'].add({'name': name, 'type': 'debit', 'balance': balance})


def _add_credit(repos, name, balance=500.0):
    return repos['account'].add({'name': name, 'type': 'credit', 'balance': balance})


def _add_liability(repos, name, balance=5000.0):
    return repos['liability'].add({'name': name, 'balance': balance})


def _bal(repos, name, repo='account'):
    if repo == 'account':
        a = repos['account'].get_by_name(name)
        return a['balance'] if a else None
    else:
        l = repos['liability'].get_by_name(name)
        return l['balance'] if l else None


class TestTransfers:

    def test_transfer_debit_to_debit(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_debit(ext_repos, 'Savings', 500.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Transfer', 'amount': 200.0,
            'source_account': 'Checking', 'target_account': 'Savings'
        })
        assert _bal(ext_repos, 'Checking') == 800.0
        assert _bal(ext_repos, 'Savings') == 700.0

    def test_transfer_debit_to_credit(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_credit(ext_repos, 'Visa', 300.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Transfer', 'amount': 100.0,
            'source_account': 'Checking', 'target_account': 'Visa'
        })
        assert _bal(ext_repos, 'Checking') == 900.0
        assert _bal(ext_repos, 'Visa') == 400.0

    def test_transfer_uses_absolute_amount(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_debit(ext_repos, 'Savings', 500.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Transfer', 'amount': -200.0,
            'source_account': 'Checking', 'target_account': 'Savings'
        })
        assert _bal(ext_repos, 'Checking') == 800.0
        assert _bal(ext_repos, 'Savings') == 700.0

    def test_transfer_missing_source_does_nothing(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Savings', 500.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Transfer', 'amount': 100.0,
            'source_account': 'NonExistent', 'target_account': 'Savings'
        })
        assert _bal(ext_repos, 'Savings') == 500.0

    def test_transfer_missing_target_does_nothing(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Transfer', 'amount': 100.0,
            'source_account': 'Checking', 'target_account': 'NonExistent'
        })
        assert _bal(ext_repos, 'Checking') == 1000.0

    def test_reverse_transfer(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 800.0)
        _add_debit(ext_repos, 'Savings', 700.0)
        ext_service.reverse_transaction_from_balance({
            'category': 'Transfer', 'amount': 200.0,
            'source_account': 'Checking', 'target_account': 'Savings'
        })
        assert _bal(ext_repos, 'Checking') == 1000.0
        assert _bal(ext_repos, 'Savings') == 500.0

    def test_apply_then_reverse_transfer_returns_original(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_debit(ext_repos, 'Savings', 500.0)
        txn = {'category': 'Transfer', 'amount': 300.0,
               'source_account': 'Checking', 'target_account': 'Savings'}
        ext_service.apply_transaction_to_balance(txn)
        ext_service.reverse_transaction_from_balance(txn)
        assert _bal(ext_repos, 'Checking') == 1000.0
        assert _bal(ext_repos, 'Savings') == 500.0


class TestDebtPaymentsCreditAccount:

    def test_payment_reduces_source(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_credit(ext_repos, 'Visa', 500.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Debt Payment', 'amount': 200.0,
            'source_account': 'Checking', 'target_debt': 'Visa', 'target_type': 'credit'
        })
        assert _bal(ext_repos, 'Checking') == 800.0

    def test_payment_reduces_credit_debt(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_credit(ext_repos, 'Visa', 500.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Debt Payment', 'amount': 200.0,
            'source_account': 'Checking', 'target_debt': 'Visa', 'target_type': 'credit'
        })
        assert _bal(ext_repos, 'Visa') == 300.0

    def test_payment_uses_absolute_amount(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_credit(ext_repos, 'Visa', 500.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Debt Payment', 'amount': -200.0,
            'source_account': 'Checking', 'target_debt': 'Visa', 'target_type': 'credit'
        })
        assert _bal(ext_repos, 'Checking') == 800.0
        assert _bal(ext_repos, 'Visa') == 300.0

    def test_reverse_restores_both(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 800.0)
        _add_credit(ext_repos, 'Visa', 300.0)
        ext_service.reverse_transaction_from_balance({
            'category': 'Debt Payment', 'amount': 200.0,
            'source_account': 'Checking', 'target_debt': 'Visa', 'target_type': 'credit'
        })
        assert _bal(ext_repos, 'Checking') == 1000.0
        assert _bal(ext_repos, 'Visa') == 500.0

    def test_apply_then_reverse_returns_original(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_credit(ext_repos, 'Visa', 500.0)
        txn = {'category': 'Debt Payment', 'amount': 200.0,
               'source_account': 'Checking', 'target_debt': 'Visa', 'target_type': 'credit'}
        ext_service.apply_transaction_to_balance(txn)
        ext_service.reverse_transaction_from_balance(txn)
        assert _bal(ext_repos, 'Checking') == 1000.0
        assert _bal(ext_repos, 'Visa') == 500.0


class TestDebtPaymentsLiability:

    def test_payment_reduces_source(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_liability(ext_repos, 'Car Loan', 8000.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Debt Payment', 'amount': 300.0,
            'source_account': 'Checking', 'target_debt': 'Car Loan', 'target_type': 'liability'
        })
        assert _bal(ext_repos, 'Checking') == 700.0

    def test_payment_reduces_liability(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_liability(ext_repos, 'Car Loan', 8000.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Debt Payment', 'amount': 300.0,
            'source_account': 'Checking', 'target_debt': 'Car Loan', 'target_type': 'liability'
        })
        assert _bal(ext_repos, 'Car Loan', 'liability') == 7700.0

    def test_reverse_restores_both(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 700.0)
        _add_liability(ext_repos, 'Car Loan', 7700.0)
        ext_service.reverse_transaction_from_balance({
            'category': 'Debt Payment', 'amount': 300.0,
            'source_account': 'Checking', 'target_debt': 'Car Loan', 'target_type': 'liability'
        })
        assert _bal(ext_repos, 'Checking') == 1000.0
        assert _bal(ext_repos, 'Car Loan', 'liability') == 8000.0

    def test_apply_then_reverse_returns_original(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_liability(ext_repos, 'Car Loan', 8000.0)
        txn = {'category': 'Debt Payment', 'amount': 300.0,
               'source_account': 'Checking', 'target_debt': 'Car Loan', 'target_type': 'liability'}
        ext_service.apply_transaction_to_balance(txn)
        ext_service.reverse_transaction_from_balance(txn)
        assert _bal(ext_repos, 'Checking') == 1000.0
        assert _bal(ext_repos, 'Car Loan', 'liability') == 8000.0

    def test_missing_source_does_nothing(self, ext_repos, ext_service):
        _add_liability(ext_repos, 'Car Loan', 8000.0)
        ext_service.apply_transaction_to_balance({
            'category': 'Debt Payment', 'amount': 300.0,
            'source_account': 'NonExistent', 'target_debt': 'Car Loan', 'target_type': 'liability'
        })
        assert _bal(ext_repos, 'Car Loan', 'liability') == 8000.0


class TestMissingAccountHandling:

    def test_regular_transaction_missing_account_does_not_raise(self, ext_repos, ext_service):
        ext_service.apply_transaction_to_balance({
            'category': 'Food', 'amount': -50.0, 'account': 'NonExistent'
        })

    def test_reverse_missing_account_does_not_raise(self, ext_repos, ext_service):
        ext_service.reverse_transaction_from_balance({
            'category': 'Food', 'amount': -50.0, 'account': 'NonExistent'
        })

    def test_reverse_transfer_missing_accounts_does_not_raise(self, ext_repos, ext_service):
        ext_service.reverse_transaction_from_balance({
            'category': 'Transfer', 'amount': 100.0,
            'source_account': 'Ghost', 'target_account': 'Phantom'
        })


class TestAuditLogging:

    def test_regular_transaction_creates_audit_entry(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        ext_service.apply_transaction_to_balance({
            'id': 'txn-001', 'title': 'Coffee',
            'category': 'Food', 'amount': -5.0, 'account': 'Checking'
        })
        account = ext_repos['account'].get_by_name('Checking')
        history = ext_service.audit_service.get_account_history(account['id'])
        assert len(history) > 0

    def test_transfer_creates_audit_entries_for_both_accounts(self, ext_repos, ext_service):
        _add_debit(ext_repos, 'Checking', 1000.0)
        _add_debit(ext_repos, 'Savings', 500.0)
        ext_service.apply_transaction_to_balance({
            'id': 'txn-001', 'category': 'Transfer', 'amount': 200.0,
            'source_account': 'Checking', 'target_account': 'Savings'
        })
        checking = ext_repos['account'].get_by_name('Checking')
        savings = ext_repos['account'].get_by_name('Savings')
        assert len(ext_service.audit_service.get_account_history(checking['id'])) > 0
        assert len(ext_service.audit_service.get_account_history(savings['id'])) > 0

    def test_no_audit_service_does_not_raise(self, ext_repos, ext_service_no_audit):
        _add_debit(ext_repos, 'Checking', 1000.0)
        ext_service_no_audit.apply_transaction_to_balance({
            'category': 'Food', 'amount': -5.0, 'account': 'Checking'
        })