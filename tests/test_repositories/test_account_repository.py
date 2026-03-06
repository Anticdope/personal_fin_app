"""
tests/test_repositories/test_account_repository.py

Tests for AccountRepository - covers validation paths, default field population,
credit account defaults, and update/delete behavior.
"""
import pytest
from unittest.mock import MagicMock
from data.repositories.account_repository import AccountRepository


@pytest.fixture
def repo(tmp_path):
    return AccountRepository(tmp_path)


@pytest.fixture
def repo_with_validation(tmp_path):
    validation = MagicMock()
    validation.sanitize_account.side_effect = lambda a: a
    validation.validate_account.return_value = (True, [])
    validation.validate_accounts_batch.return_value = (True, {})
    return AccountRepository(tmp_path, validation_service=validation)


def make_account(**overrides):
    data = {'name': 'Checking', 'type': 'debit', 'balance': 1000.0}
    data.update(overrides)
    return data


# ===== DEFAULT FIELD POPULATION =====

class TestDefaultFields:

    def test_add_assigns_id_if_missing(self, repo):
        account = repo.add({'name': 'Checking', 'type': 'debit', 'balance': 0.0})
        assert 'id' in account
        assert account['id'].startswith('acc-')

    def test_add_preserves_existing_id(self, repo):
        account = repo.add({'id': 'acc-custom', 'name': 'Checking', 'type': 'debit', 'balance': 0.0})
        assert account['id'] == 'acc-custom'

    def test_add_defaults_type_to_debit(self, repo):
        account = repo.add({'name': 'Checking', 'balance': 0.0})
        assert account['type'] == 'debit'

    def test_add_defaults_balance_to_zero(self, repo):
        account = repo.add({'name': 'Checking', 'type': 'debit'})
        assert account['balance'] == 0.0

    def test_credit_account_gets_interest_rate_default(self, repo):
        account = repo.add({'name': 'Visa', 'type': 'credit', 'balance': 500.0})
        assert account['interest_rate'] == 0.0

    def test_credit_account_gets_minimum_payment_default(self, repo):
        account = repo.add({'name': 'Visa', 'type': 'credit', 'balance': 500.0})
        assert account['minimum_payment'] == 0.0

    def test_credit_account_gets_original_balance_from_balance(self, repo):
        account = repo.add({'name': 'Visa', 'type': 'credit', 'balance': 500.0})
        assert account['original_balance'] == 500.0

    def test_credit_account_gets_payment_due_day_none(self, repo):
        account = repo.add({'name': 'Visa', 'type': 'credit', 'balance': 500.0})
        assert account['payment_due_day'] is None

    def test_credit_account_preserves_provided_interest_rate(self, repo):
        account = repo.add({'name': 'Visa', 'type': 'credit', 'balance': 500.0, 'interest_rate': 19.99})
        assert account['interest_rate'] == 19.99

    def test_credit_account_preserves_provided_original_balance(self, repo):
        account = repo.add({'name': 'Visa', 'type': 'credit', 'balance': 300.0, 'original_balance': 1000.0})
        assert account['original_balance'] == 1000.0

    def test_debit_account_does_not_get_credit_fields(self, repo):
        account = repo.add({'name': 'Checking', 'type': 'debit', 'balance': 1000.0})
        assert 'interest_rate' not in account
        assert 'minimum_payment' not in account


# ===== GET OPERATIONS =====

class TestGetOperations:

    def test_get_all_empty_initially(self, repo):
        assert repo.get_all() == []

    def test_get_by_id_returns_account(self, repo):
        account = repo.add({'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 0.0})
        result = repo.get_by_id('acc-001')
        assert result is not None
        assert result['name'] == 'Checking'

    def test_get_by_id_returns_none_if_not_found(self, repo):
        assert repo.get_by_id('nonexistent') is None

    def test_get_by_name_returns_account(self, repo):
        repo.add({'name': 'Savings', 'type': 'debit', 'balance': 0.0})
        result = repo.get_by_name('Savings')
        assert result is not None
        assert result['name'] == 'Savings'

    def test_get_by_name_returns_none_if_not_found(self, repo):
        assert repo.get_by_name('Ghost') is None


# ===== UPDATE =====

class TestUpdate:

    def test_update_modifies_account(self, repo):
        old = repo.add(make_account())
        new = {**old, 'balance': 2000.0}
        repo.update(old, new)
        assert repo.get_by_id(old['id'])['balance'] == 2000.0

    def test_update_preserves_id(self, repo):
        old = repo.add(make_account(name='Checking'))
        new = {'name': 'Updated', 'type': 'debit', 'balance': 500.0}
        repo.update(old, new)
        result = repo.get_by_id(old['id'])
        assert result is not None

    def test_update_preserves_type(self, repo):
        old = repo.add(make_account(type='credit', balance=500.0))
        new = {**old, 'balance': 200.0, 'type': 'debit'}  # type change attempt
        repo.update(old, new)
        result = repo.get_by_id(old['id'])
        assert result['type'] == 'credit'

    def test_update_preserves_original_balance(self, repo):
        old = repo.add(make_account(type='credit', balance=500.0, original_balance=1000.0))
        new = {**old}
        del new['original_balance']
        repo.update(old, new)
        result = repo.get_by_id(old['id'])
        assert result['original_balance'] == 1000.0

    def test_update_returns_false_if_not_found(self, repo):
        ghost = {'id': 'acc-ghost', 'name': 'Ghost', 'type': 'debit', 'balance': 0.0}
        result = repo.update(ghost, ghost)
        assert result is False

    def test_update_persists_to_disk(self, repo):
        old = repo.add(make_account())
        new = {**old, 'balance': 9999.0}
        repo.update(old, new)
        fresh = AccountRepository(repo.data_dir)
        assert fresh.get_by_id(old['id'])['balance'] == 9999.0


# ===== DELETE =====

class TestDelete:

    def test_delete_removes_account(self, repo):
        account = repo.add(make_account())
        repo.delete(account)
        assert repo.get_by_name('Checking') is None

    def test_delete_preserves_other_accounts(self, repo):
        a1 = repo.add(make_account(name='Checking'))
        a2 = repo.add(make_account(name='Savings'))
        repo.delete(a1)
        assert repo.get_by_name('Savings') is not None

    def test_delete_persists_to_disk(self, repo):
        account = repo.add(make_account())
        repo.delete(account)
        fresh = AccountRepository(repo.data_dir)
        assert fresh.get_by_name('Checking') is None


# ===== VALIDATION PATHS =====

class TestValidationPaths:

    def test_add_calls_sanitize(self, repo_with_validation):
        repo_with_validation.add(make_account())
        repo_with_validation.validation_service.sanitize_account.assert_called()

    def test_add_calls_validate(self, repo_with_validation):
        repo_with_validation.add(make_account())
        repo_with_validation.validation_service.validate_account.assert_called()

    def test_add_raises_on_validation_failure(self, tmp_path):
        validation = MagicMock()
        validation.sanitize_account.side_effect = lambda a: a
        validation.validate_account.return_value = (False, ['name is required'])
        repo = AccountRepository(tmp_path, validation_service=validation)
        with pytest.raises(ValueError, match='validation failed'):
            repo.add(make_account())

    def test_update_calls_validate(self, repo_with_validation):
        old = repo_with_validation.add(make_account())
        new = {**old, 'balance': 500.0}
        repo_with_validation.update(old, new)
        assert repo_with_validation.validation_service.validate_account.call_count >= 2

    def test_update_raises_on_validation_failure(self, tmp_path):
        # First add without validation
        repo_no_val = AccountRepository(tmp_path)
        old = repo_no_val.add(make_account())

        validation = MagicMock()
        validation.sanitize_account.side_effect = lambda a: a
        validation.validate_account.return_value = (False, ['balance invalid'])
        validation.validate_accounts_batch.return_value = (True, {})
        repo = AccountRepository(tmp_path, validation_service=validation)
        with pytest.raises(ValueError, match='validation failed'):
            repo.update(old, {**old, 'balance': -1.0})

    def test_save_all_raises_on_batch_validation_failure(self, tmp_path):
        validation = MagicMock()
        validation.validate_accounts_batch.return_value = (False, {0: ['type invalid']})
        repo = AccountRepository(tmp_path, validation_service=validation)
        with pytest.raises(ValueError, match='validation failed'):
            repo.save_all([make_account()])

    def test_no_validation_service_does_not_raise(self, repo):
        # Should work fine without validation
        account = repo.add(make_account())
        assert account is not None


# ===== PERSISTENCE =====

class TestPersistence:

    def test_data_persists_across_instances(self, repo):
        repo.add(make_account(name='Checking'))
        fresh = AccountRepository(repo.data_dir)
        assert fresh.get_by_name('Checking') is not None

    def test_multiple_accounts_persist(self, repo):
        repo.add(make_account(name='Checking'))
        repo.add(make_account(name='Savings'))
        fresh = AccountRepository(repo.data_dir)
        assert len(fresh.get_all()) == 2