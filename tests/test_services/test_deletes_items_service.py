"""
Tests for DeletedItemsService
Covers: restore operations, duplicate prevention, permanent deletion, missing archive entries
"""
import pytest
from PySide6.QtCore import QDate
from data.services.deleted_items_service import DeletedItemsService
from data.repositories.deleted_items_repository import DeletedItemsRepository
from data.repositories.category_repository import CategoryRepository
from data.repositories.account_repository import AccountRepository
from data.repositories.transaction_repository import TransactionRepository
from data.repositories.asset_repository import AssetRepository
from data.repositories.liability_repository import LiabilityRepository


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def repos(tmp_path):
    return {
        'deleted': DeletedItemsRepository(tmp_path),
        'category': CategoryRepository(tmp_path),
        'account': AccountRepository(tmp_path),
        'transaction': TransactionRepository(tmp_path),
        'asset': AssetRepository(tmp_path),
        'liability': LiabilityRepository(tmp_path),
    }


@pytest.fixture
def service(repos):
    return DeletedItemsService(
        repos['deleted'], repos['category'], repos['account'],
        repos['transaction'], repos['asset'], repos['liability']
    )


# ============================================================
# CATEGORY restore
# ============================================================

class TestRestoreCategory:

    def test_restore_category_succeeds(self, repos, service):
        category = {'id': 'cat-001', 'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        repos['deleted'].add_category(category)
        success, message = service.restore_category(0)
        assert success is True
        restored = repos['category'].get_by_name('Food')
        assert restored is not None

    def test_restore_category_removes_from_archive(self, repos, service):
        category = {'id': 'cat-001', 'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        repos['deleted'].add_category(category)
        service.restore_category(0)
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('categories', [])) == 0

    def test_restore_category_fails_if_name_already_exists(self, repos, service):
        category = {'id': 'cat-001', 'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        repos['category'].add(category.copy())
        repos['deleted'].add_category(category)
        success, message = service.restore_category(0)
        assert success is False
        assert 'Food' in message

    def test_restore_category_fails_if_index_invalid(self, service):
        success, message = service.restore_category(99)
        assert success is False

    def test_restore_category_success_message(self, repos, service):
        category = {'id': 'cat-001', 'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        repos['deleted'].add_category(category)
        success, message = service.restore_category(0)
        assert 'Food' in message
        assert 'restored' in message.lower()


# ============================================================
# ACCOUNT restore
# ============================================================

class TestRestoreAccount:

    def test_restore_account_succeeds(self, repos, service):
        account = {'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 1000.0}
        repos['deleted'].add_account(account)
        success, message = service.restore_account(0)
        assert success is True
        restored = repos['account'].get_by_name('Checking')
        assert restored is not None

    def test_restore_account_removes_from_archive(self, repos, service):
        account = {'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 1000.0}
        repos['deleted'].add_account(account)
        service.restore_account(0)
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('accounts', [])) == 0

    def test_restore_account_fails_if_name_exists(self, repos, service):
        account = {'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 1000.0}
        repos['account'].add(account.copy())
        repos['deleted'].add_account(account)
        success, message = service.restore_account(0)
        assert success is False
        assert 'Checking' in message

    def test_restore_account_fails_if_index_invalid(self, service):
        success, message = service.restore_account(0)
        assert success is False

    def test_restore_multiple_accounts_correct_index(self, repos, service):
        acc1 = {'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 0.0}
        acc2 = {'id': 'acc-002', 'name': 'Savings', 'type': 'debit', 'balance': 0.0}
        repos['deleted'].add_account(acc1)
        repos['deleted'].add_account(acc2)
        service.restore_account(0)  # Restore first
        assert repos['account'].get_by_name('Checking') is not None
        assert repos['account'].get_by_name('Savings') is None


# ============================================================
# TRANSACTION restore
# ============================================================

class TestRestoreTransaction:

    def test_restore_transaction_succeeds(self, repos, service):
        date = QDate(2024, 1, 15)
        transaction = {
            'id': 'txn-001', 'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        repos['deleted'].add_transaction(date, transaction)
        success, message = service.restore_transaction(0)
        assert success is True
        saved = repos['transaction'].get_day_transactions(2024, 1, 15)
        assert any(t['title'] == 'Coffee' for t in saved)

    def test_restore_transaction_removes_from_archive(self, repos, service):
        date = QDate(2024, 1, 15)
        transaction = {'id': 'txn-001', 'title': 'Coffee', 'amount': -5.0,
                       'category': 'Food', 'status': 'posted', 'account': 'Checking'}
        repos['deleted'].add_transaction(date, transaction)
        service.restore_transaction(0)
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('transactions', [])) == 0

    def test_restore_transaction_fails_if_index_invalid(self, service):
        success, message = service.restore_transaction(0)
        assert success is False

    def test_restore_transaction_success_message(self, repos, service):
        date = QDate(2024, 1, 15)
        transaction = {'id': 'txn-001', 'title': 'Coffee', 'amount': -5.0,
                       'category': 'Food', 'status': 'posted', 'account': 'Checking'}
        repos['deleted'].add_transaction(date, transaction)
        success, message = service.restore_transaction(0)
        assert 'Coffee' in message


# ============================================================
# ASSET restore
# ============================================================

class TestRestoreAsset:

    def test_restore_asset_succeeds(self, repos, service):
        asset = {'id': 'ast-001', 'name': 'Car', 'value': 15000.0, 'original_value': 20000.0}
        repos['deleted'].add_asset(asset)
        success, message = service.restore_asset(0)
        assert success is True
        assets = repos['asset'].get_all()
        assert any(a['name'] == 'Car' for a in assets)

    def test_restore_asset_removes_from_archive(self, repos, service):
        asset = {'id': 'ast-001', 'name': 'Car', 'value': 15000.0, 'original_value': 20000.0}
        repos['deleted'].add_asset(asset)
        service.restore_asset(0)
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('assets', [])) == 0

    def test_restore_asset_fails_if_name_exists(self, repos, service):
        asset = {'id': 'ast-001', 'name': 'Car', 'value': 15000.0, 'original_value': 20000.0}
        repos['asset'].add(asset.copy())
        repos['deleted'].add_asset(asset)
        success, message = service.restore_asset(0)
        assert success is False
        assert 'Car' in message

    def test_restore_asset_fails_if_index_invalid(self, service):
        success, message = service.restore_asset(0)
        assert success is False


# ============================================================
# LIABILITY restore
# ============================================================

class TestRestoreLiability:

    def test_restore_liability_succeeds(self, repos, service):
        liability = {'id': 'lib-001', 'name': 'Student Loan', 'balance': 20000.0}
        repos['deleted'].add_liability(liability)
        success, message = service.restore_liability(0)
        assert success is True
        liabilities = repos['liability'].get_all()
        assert any(l['name'] == 'Student Loan' for l in liabilities)

    def test_restore_liability_removes_from_archive(self, repos, service):
        liability = {'id': 'lib-001', 'name': 'Student Loan', 'balance': 20000.0}
        repos['deleted'].add_liability(liability)
        service.restore_liability(0)
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('liabilities', [])) == 0

    def test_restore_liability_fails_if_name_exists(self, repos, service):
        liability = {'id': 'lib-001', 'name': 'Student Loan', 'balance': 20000.0}
        repos['liability'].add(liability.copy())
        repos['deleted'].add_liability(liability)
        success, message = service.restore_liability(0)
        assert success is False
        assert 'Student Loan' in message

    def test_restore_liability_fails_if_index_invalid(self, service):
        success, message = service.restore_liability(0)
        assert success is False


# ============================================================
# Permanent deletion
# ============================================================

class TestPermanentDeletion:

    def test_permanently_delete_category(self, repos, service):
        category = {'id': 'cat-001', 'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        repos['deleted'].add_category(category)
        success, _ = service.permanently_delete_category(0)
        assert success is True
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('categories', [])) == 0

    def test_permanently_delete_account(self, repos, service):
        account = {'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 0.0}
        repos['deleted'].add_account(account)
        success, _ = service.permanently_delete_account(0)
        assert success is True
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('accounts', [])) == 0

    def test_permanently_delete_transaction(self, repos, service):
        date = QDate(2024, 1, 15)
        transaction = {'id': 'txn-001', 'title': 'Coffee', 'amount': -5.0,
                       'category': 'Food', 'status': 'posted', 'account': 'Checking'}
        repos['deleted'].add_transaction(date, transaction)
        success, _ = service.permanently_delete_transaction(0)
        assert success is True
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('transactions', [])) == 0

    def test_permanently_delete_asset(self, repos, service):
        asset = {'id': 'ast-001', 'name': 'Car', 'value': 15000.0}
        repos['deleted'].add_asset(asset)
        success, _ = service.permanently_delete_asset(0)
        assert success is True
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('assets', [])) == 0

    def test_permanently_delete_liability(self, repos, service):
        liability = {'id': 'lib-001', 'name': 'Loan', 'balance': 5000.0}
        repos['deleted'].add_liability(liability)
        success, _ = service.permanently_delete_liability(0)
        assert success is True
        deleted = repos['deleted'].get_all()
        assert len(deleted.get('liabilities', [])) == 0

    def test_permanent_delete_does_not_restore_to_repo(self, repos, service):
        category = {'id': 'cat-001', 'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        repos['deleted'].add_category(category)
        service.permanently_delete_category(0)
        assert repos['category'].get_by_name('Food') is None


# ============================================================
# get_all_deleted_items
# ============================================================

class TestGetAllDeletedItems:

    def test_returns_empty_initially(self, service):
        deleted = service.get_all_deleted_items()
        assert deleted.get('categories', []) == []
        assert deleted.get('accounts', []) == []
        assert deleted.get('transactions', []) == []
        assert deleted.get('assets', []) == []
        assert deleted.get('liabilities', []) == []

    def test_returns_all_archived_items(self, repos, service):
        repos['deleted'].add_category({'id': 'cat-001', 'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0})
        repos['deleted'].add_account({'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 0.0})
        repos['deleted'].add_asset({'id': 'ast-001', 'name': 'Car', 'value': 15000.0})
        deleted = service.get_all_deleted_items()
        assert len(deleted.get('categories', [])) == 1
        assert len(deleted.get('accounts', [])) == 1
        assert len(deleted.get('assets', [])) == 1