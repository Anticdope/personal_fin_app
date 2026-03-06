"""
Integration Tests - CRUD Operations
Tests the full stack: DataManager -> Repository -> File
No mocks - uses real objects with temp directories
These tests catch signature mismatches and wiring bugs that unit tests miss
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from data_manager import DataManager
from PySide6.QtCore import QDate


@pytest.fixture
def dm(tmp_path):
    """Real DataManager pointed at a temp directory"""
    manager = DataManager.__new__(DataManager)
    manager.data_dir = tmp_path
    
    # Initialize repos
    from data.repositories.category_repository import CategoryRepository
    from data.repositories.account_repository import AccountRepository
    from data.repositories.transaction_repository import TransactionRepository
    from data.repositories.asset_repository import AssetRepository
    from data.repositories.liability_repository import LiabilityRepository
    from data.repositories.recurring_repository import RecurringRepository
    from data.repositories.deleted_items_repository import DeletedItemsRepository
    from data.audit.audit_repository import AuditLogRepository
    from data.audit.audit_service import AuditService
    from data.services.transaction_service import TransactionService
    from data.services.calculation_service import CalculationService
    from data.services.recurring_service import RecurringService
    from data.services.deleted_items_service import DeletedItemsService
    from deleted_items_manager import DeletedItemsManager

    manager.category_repo = CategoryRepository(tmp_path)
    manager.account_repo = AccountRepository(tmp_path)
    manager.transaction_repo = TransactionRepository(tmp_path)
    manager.asset_repo = AssetRepository(tmp_path)
    manager.liability_repo = LiabilityRepository(tmp_path)
    manager.recurring_repo = RecurringRepository(tmp_path)
    manager.deleted_items_repo = DeletedItemsRepository(tmp_path)

    manager.audit_repo = AuditLogRepository(tmp_path)
    manager.audit_service = AuditService(manager.audit_repo)

    manager.transaction_service = TransactionService(
        manager.account_repo, manager.asset_repo,
        manager.liability_repo, manager.audit_service
    )
    manager.calculation_service = CalculationService(
        manager.account_repo, manager.asset_repo,
        manager.liability_repo, manager.transaction_repo,
        manager.category_repo
    )
    manager.recurring_service = RecurringService(
        manager.recurring_repo, manager.transaction_repo
    )
    manager.deleted_items_service = DeletedItemsService(
        manager.deleted_items_repo, manager.category_repo,
        manager.account_repo, manager.transaction_repo,
        manager.asset_repo, manager.liability_repo
    )
    manager.deleted_items_manager = DeletedItemsManager(
        manager.deleted_items_repo, manager.deleted_items_service
    )

    manager.categories = manager.category_repo.get_all()
    manager.accounts = manager.account_repo.get_all()
    manager.assets = manager.asset_repo.get_all()
    manager.liabilities = manager.liability_repo.get_all()
    manager.recurring_transactions = manager.recurring_repo.get_all()

    return manager


# ============================================================
# CATEGORY CRUD
# ============================================================

class TestCategoryCRUD:

    def test_add_category(self, dm):
        category = {'name': 'Groceries', 'color': '#FF0000', 'type': 'expense', 'budget': 200.0}
        dm.add_category(category)
        names = [c['name'] for c in dm.categories]
        assert 'Groceries' in names

    def test_add_category_persists_to_disk(self, dm, tmp_path):
        category = {'name': 'Groceries', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        dm.add_category(category)
        # Reload from disk
        from data.repositories.category_repository import CategoryRepository
        fresh_repo = CategoryRepository(tmp_path)
        names = [c['name'] for c in fresh_repo.get_all()]
        assert 'Groceries' in names

    def test_add_category_assigns_id(self, dm):
        category = {'name': 'Transport', 'color': '#0000FF', 'type': 'expense', 'budget': 0.0}
        result = dm.add_category(category)
        assert 'id' in result
        assert result['id'] is not None

    def test_update_category(self, dm):
        category = {'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        added = dm.add_category(category)
        updated = {**added, 'name': 'Food & Drink', 'budget': 300.0}
        dm.update_category(added, updated)
        names = [c['name'] for c in dm.categories]
        assert 'Food & Drink' in names
        assert 'Food' not in names

    def test_update_category_persists_to_disk(self, dm, tmp_path):
        category = {'name': 'Food', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
        added = dm.add_category(category)
        updated = {**added, 'name': 'Food & Drink'}
        dm.update_category(added, updated)
        from data.repositories.category_repository import CategoryRepository
        fresh_repo = CategoryRepository(tmp_path)
        names = [c['name'] for c in fresh_repo.get_all()]
        assert 'Food & Drink' in names
        assert 'Food' not in names

    def test_delete_category(self, dm):
        category = {'name': 'Junk', 'color': '#888888', 'type': 'expense', 'budget': 0.0}
        added = dm.add_category(category)
        dm.delete_category(added)
        names = [c['name'] for c in dm.categories]
        assert 'Junk' not in names

    def test_delete_category_persists_to_disk(self, dm, tmp_path):
        category = {'name': 'Junk', 'color': '#888888', 'type': 'expense', 'budget': 0.0}
        added = dm.add_category(category)
        dm.delete_category(added)
        from data.repositories.category_repository import CategoryRepository
        fresh_repo = CategoryRepository(tmp_path)
        names = [c['name'] for c in fresh_repo.get_all()]
        assert 'Junk' not in names

    def test_delete_category_archives_to_deleted_items(self, dm):
        category = {'name': 'Junk', 'color': '#888888', 'type': 'expense', 'budget': 0.0}
        added = dm.add_category(category)
        dm.delete_category(added)
        deleted = dm.deleted_items_manager.get_deleted_items()
        deleted_names = [d['item']['name'] for d in deleted.get('categories', [])]
        assert 'Junk' in deleted_names


# ============================================================
# ACCOUNT CRUD
# ============================================================

class TestAccountCRUD:

    def test_add_debit_account(self, dm):
        account = {'name': 'Checking', 'type': 'debit', 'balance': 1000.0}
        dm.add_account(account)
        names = [a['name'] for a in dm.accounts]
        assert 'Checking' in names

    def test_add_credit_account(self, dm):
        account = {'name': 'Visa', 'type': 'credit', 'balance': 500.0}
        dm.add_account(account)
        names = [a['name'] for a in dm.accounts]
        assert 'Visa' in names

    def test_add_account_persists_to_disk(self, dm, tmp_path):
        account = {'name': 'Savings', 'type': 'debit', 'balance': 5000.0}
        dm.add_account(account)
        from data.repositories.account_repository import AccountRepository
        fresh_repo = AccountRepository(tmp_path)
        names = [a['name'] for a in fresh_repo.get_all()]
        assert 'Savings' in names

    def test_add_account_assigns_id(self, dm):
        account = {'name': 'Checking', 'type': 'debit', 'balance': 0.0}
        result = dm.add_account(account)
        assert 'id' in result

    def test_update_account(self, dm):
        account = {'name': 'Old Name', 'type': 'debit', 'balance': 100.0}
        added = dm.add_account(account)
        updated = {**added, 'name': 'New Name', 'balance': 200.0}
        dm.update_account(added, updated)
        names = [a['name'] for a in dm.accounts]
        assert 'New Name' in names
        assert 'Old Name' not in names

    def test_update_account_persists_to_disk(self, dm, tmp_path):
        account = {'name': 'Old Name', 'type': 'debit', 'balance': 100.0}
        added = dm.add_account(account)
        updated = {**added, 'name': 'New Name'}
        dm.update_account(added, updated)
        from data.repositories.account_repository import AccountRepository
        fresh_repo = AccountRepository(tmp_path)
        names = [a['name'] for a in fresh_repo.get_all()]
        assert 'New Name' in names
        assert 'Old Name' not in names

    def test_delete_account(self, dm):
        account = {'name': 'OldBank', 'type': 'debit', 'balance': 0.0}
        added = dm.add_account(account)
        dm.delete_account(added)
        names = [a['name'] for a in dm.accounts]
        assert 'OldBank' not in names

    def test_delete_account_persists_to_disk(self, dm, tmp_path):
        account = {'name': 'OldBank', 'type': 'debit', 'balance': 0.0}
        added = dm.add_account(account)
        dm.delete_account(added)
        from data.repositories.account_repository import AccountRepository
        fresh_repo = AccountRepository(tmp_path)
        names = [a['name'] for a in fresh_repo.get_all()]
        assert 'OldBank' not in names

    def test_delete_account_archives_to_deleted_items(self, dm):
        account = {'name': 'OldBank', 'type': 'debit', 'balance': 0.0}
        added = dm.add_account(account)
        dm.delete_account(added)
        deleted = dm.deleted_items_manager.get_deleted_items()
        deleted_names = [d['item']['name'] for d in deleted.get('accounts', [])]
        assert 'OldBank' in deleted_names


# ============================================================
# ASSET CRUD
# ============================================================

class TestAssetCRUD:

    def test_add_asset(self, dm):
        asset = {'name': 'Car', 'value': 15000.0}
        dm.add_asset(asset)
        names = [a['name'] for a in dm.assets]
        assert 'Car' in names

    def test_add_asset_persists_to_disk(self, dm, tmp_path):
        asset = {'name': 'Car', 'value': 15000.0}
        dm.add_asset(asset)
        from data.repositories.asset_repository import AssetRepository
        fresh_repo = AssetRepository(tmp_path)
        names = [a['name'] for a in fresh_repo.get_all()]
        assert 'Car' in names

    def test_add_asset_sets_original_value(self, dm):
        asset = {'name': 'Car', 'value': 15000.0}
        result = dm.add_asset(asset)
        assert result['original_value'] == 15000.0

    def test_update_asset(self, dm):
        asset = {'name': 'Car', 'value': 15000.0}
        added = dm.add_asset(asset)
        updated = {**added, 'value': 12000.0}
        dm.update_asset(added, updated)
        car = next(a for a in dm.assets if a['name'] == 'Car')
        assert car['value'] == 12000.0

    def test_update_asset_preserves_original_value(self, dm):
        asset = {'name': 'Car', 'value': 15000.0}
        added = dm.add_asset(asset)
        updated = {**added, 'value': 12000.0}
        dm.update_asset(added, updated)
        car = next(a for a in dm.assets if a['name'] == 'Car')
        assert car['original_value'] == 15000.0

    def test_delete_asset(self, dm):
        asset = {'name': 'Boat', 'value': 5000.0}
        added = dm.add_asset(asset)
        dm.delete_asset(added)
        names = [a['name'] for a in dm.assets]
        assert 'Boat' not in names

    def test_delete_asset_persists_to_disk(self, dm, tmp_path):
        asset = {'name': 'Boat', 'value': 5000.0}
        added = dm.add_asset(asset)
        dm.delete_asset(added)
        from data.repositories.asset_repository import AssetRepository
        fresh_repo = AssetRepository(tmp_path)
        names = [a['name'] for a in fresh_repo.get_all()]
        assert 'Boat' not in names

    def test_delete_asset_archives_to_deleted_items(self, dm):
        asset = {'name': 'Boat', 'value': 5000.0}
        added = dm.add_asset(asset)
        dm.delete_asset(added)
        deleted = dm.deleted_items_manager.get_deleted_items()
        deleted_names = [d['item']['name'] for d in deleted.get('assets', [])]
        assert 'Boat' in deleted_names


# ============================================================
# LIABILITY CRUD
# ============================================================

class TestLiabilityCRUD:

    def test_add_liability(self, dm):
        liability = {'name': 'Student Loan', 'balance': 20000.0}
        dm.add_liability(liability)
        names = [l['name'] for l in dm.liabilities]
        assert 'Student Loan' in names

    def test_add_liability_persists_to_disk(self, dm, tmp_path):
        liability = {'name': 'Student Loan', 'balance': 20000.0}
        dm.add_liability(liability)
        from data.repositories.liability_repository import LiabilityRepository
        fresh_repo = LiabilityRepository(tmp_path)
        names = [l['name'] for l in fresh_repo.get_all()]
        assert 'Student Loan' in names

    def test_add_liability_assigns_id(self, dm):
        liability = {'name': 'Car Loan', 'balance': 8000.0}
        result = dm.add_liability(liability)
        assert 'id' in result

    def test_update_liability(self, dm):
        liability = {'name': 'Old Loan', 'balance': 10000.0}
        added = dm.add_liability(liability)
        updated = {**added, 'name': 'Refinanced Loan', 'balance': 9500.0}
        dm.update_liability(added, updated)
        names = [l['name'] for l in dm.liabilities]
        assert 'Refinanced Loan' in names
        assert 'Old Loan' not in names

    def test_update_liability_persists_to_disk(self, dm, tmp_path):
        liability = {'name': 'Old Loan', 'balance': 10000.0}
        added = dm.add_liability(liability)
        updated = {**added, 'name': 'Refinanced Loan'}
        dm.update_liability(added, updated)
        from data.repositories.liability_repository import LiabilityRepository
        fresh_repo = LiabilityRepository(tmp_path)
        names = [l['name'] for l in fresh_repo.get_all()]
        assert 'Refinanced Loan' in names
        assert 'Old Loan' not in names

    def test_delete_liability(self, dm):
        liability = {'name': 'Paid Off Loan', 'balance': 0.0}
        added = dm.add_liability(liability)
        dm.delete_liability(added)
        names = [l['name'] for l in dm.liabilities]
        assert 'Paid Off Loan' not in names

    def test_delete_liability_persists_to_disk(self, dm, tmp_path):
        liability = {'name': 'Paid Off Loan', 'balance': 0.0}
        added = dm.add_liability(liability)
        dm.delete_liability(added)
        from data.repositories.liability_repository import LiabilityRepository
        fresh_repo = LiabilityRepository(tmp_path)
        names = [l['name'] for l in fresh_repo.get_all()]
        assert 'Paid Off Loan' not in names

    def test_delete_liability_archives_to_deleted_items(self, dm):
        liability = {'name': 'Paid Off Loan', 'balance': 0.0}
        added = dm.add_liability(liability)
        dm.delete_liability(added)
        deleted = dm.deleted_items_manager.get_deleted_items()
        deleted_names = [d['item']['name'] for d in deleted.get('liabilities', [])]
        assert 'Paid Off Loan' in deleted_names


# ============================================================
# TRANSACTION CRUD
# ============================================================

class TestTransactionCRUD:

    def _make_date(self, year=2024, month=1, day=15):
        return QDate(year, month, day)

    def _make_account(self, dm, name='Checking'):
        return dm.add_account({'name': name, 'type': 'debit', 'balance': 1000.0})

    def test_add_transaction(self, dm):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        transactions = dm.get_day_transactions(date)
        assert any(t['title'] == 'Coffee' for t in transactions)

    def test_add_transaction_persists_to_disk(self, dm, tmp_path):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        from data.repositories.transaction_repository import TransactionRepository
        fresh_repo = TransactionRepository(tmp_path)
        transactions = fresh_repo.get_day_transactions(2024, 1, 15)
        assert any(t['title'] == 'Coffee' for t in transactions)

    def test_add_transaction_updates_account_balance(self, dm):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Groceries', 'amount': -50.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        checking = next(a for a in dm.accounts if a['name'] == 'Checking')
        assert checking['balance'] == 950.0

    def test_update_transaction(self, dm):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        old = dm.get_day_transactions(date)[0]
        updated = {**old, 'amount': -6.0, 'title': 'Fancy Coffee'}
        dm.update_transaction(date, old, updated)
        transactions = dm.get_day_transactions(date)
        assert any(t['title'] == 'Fancy Coffee' for t in transactions)
        assert not any(t['title'] == 'Coffee' for t in transactions)

    def test_update_transaction_corrects_balance(self, dm):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        old = dm.get_day_transactions(date)[0]
        updated = {**old, 'amount': -10.0}
        dm.update_transaction(date, old, updated)
        checking = next(a for a in dm.accounts if a['name'] == 'Checking')
        assert checking['balance'] == 990.0

    def test_delete_transaction(self, dm):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        added = dm.get_day_transactions(date)[0]
        dm.delete_transaction(date, added)
        transactions = dm.get_day_transactions(date)
        assert not any(t['title'] == 'Coffee' for t in transactions)

    def test_delete_transaction_reverses_balance(self, dm):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        added = dm.get_day_transactions(date)[0]
        dm.delete_transaction(date, added)
        checking = next(a for a in dm.accounts if a['name'] == 'Checking')
        assert checking['balance'] == 1000.0

    def test_delete_transaction_archives_to_deleted_items(self, dm):
        self._make_account(dm)
        date = self._make_date()
        transaction = {
            'title': 'Coffee', 'amount': -5.0,
            'category': 'Food', 'status': 'posted', 'account': 'Checking'
        }
        dm.add_transaction(date, transaction)
        added = dm.get_day_transactions(date)[0]
        dm.delete_transaction(date, added)
        deleted = dm.deleted_items_manager.get_deleted_items()
        deleted_titles = [d['item']['title'] for d in deleted.get('transactions', [])]
        assert 'Coffee' in deleted_titles