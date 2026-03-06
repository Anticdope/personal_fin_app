"""
tests/test_repositories/test_liability_repository.py

Tests for LiabilityRepository
"""
import pytest
from data.repositories.liability_repository import LiabilityRepository


@pytest.fixture
def repo(tmp_path):
    return LiabilityRepository(tmp_path)


def make_liability(**overrides):
    data = {'name': 'Student Loan', 'balance': 20000.0}
    data.update(overrides)
    return data


class TestLiabilityRepository:

    # ===== ADD =====

    def test_add_assigns_id(self, repo):
        result = repo.add(make_liability())
        assert 'id' in result
        assert result['id'] is not None

    def test_add_preserves_existing_id(self, repo):
        liability = make_liability()
        liability['id'] = 'lib-custom'
        result = repo.add(liability)
        assert result['id'] == 'lib-custom'

    def test_add_sets_default_interest_rate(self, repo):
        result = repo.add(make_liability())
        assert result['interest_rate'] == 0.0

    def test_add_sets_default_minimum_payment(self, repo):
        result = repo.add(make_liability())
        assert result['minimum_payment'] == 0.0

    def test_add_sets_original_balance(self, repo):
        result = repo.add(make_liability(balance=20000.0))
        assert result['original_balance'] == 20000.0

    def test_add_sets_default_payment_due_day(self, repo):
        result = repo.add(make_liability())
        assert result['payment_due_day'] is None

    def test_add_preserves_interest_rate_if_provided(self, repo):
        result = repo.add(make_liability(interest_rate=5.5))
        assert result['interest_rate'] == 5.5

    def test_add_persists_to_disk(self, repo, tmp_path):
        repo.add(make_liability(name='Car Loan'))
        fresh = LiabilityRepository(tmp_path)
        names = [l['name'] for l in fresh.get_all()]
        assert 'Car Loan' in names

    # ===== GET =====

    def test_get_all_empty_initially(self, repo):
        assert repo.get_all() == []

    def test_get_all_returns_all_liabilities(self, repo):
        repo.add(make_liability(name='Loan A'))
        repo.add(make_liability(name='Loan B'))
        assert len(repo.get_all()) == 2

    def test_get_by_id_finds_liability(self, repo):
        added = repo.add(make_liability(name='Mortgage'))
        result = repo.get_by_id(added['id'])
        assert result is not None
        assert result['name'] == 'Mortgage'

    def test_get_by_id_returns_none_if_not_found(self, repo):
        assert repo.get_by_id('nonexistent') is None

    def test_get_by_name_finds_liability(self, repo):
        repo.add(make_liability(name='Car Loan'))
        result = repo.get_by_name('Car Loan')
        assert result is not None

    def test_get_by_name_returns_none_if_not_found(self, repo):
        assert repo.get_by_name('Nonexistent') is None

    # ===== UPDATE =====

    def test_update_modifies_data(self, repo):
        added = repo.add(make_liability(name='Old Loan', balance=10000.0))
        updated = {**added, 'name': 'Refinanced', 'balance': 9500.0}
        result = repo.update(added, updated)
        assert result is True
        found = repo.get_by_name('Refinanced')
        assert found is not None
        assert found['balance'] == 9500.0

    def test_update_preserves_id(self, repo):
        added = repo.add(make_liability())
        original_id = added['id']
        updated = {**added, 'balance': 5000.0}
        repo.update(added, updated)
        assert repo.get_by_id(original_id) is not None

    def test_update_preserves_original_balance(self, repo):
        added = repo.add(make_liability(balance=20000.0))
        updated = {**added, 'balance': 18000.0}
        del updated['original_balance']
        repo.update(added, updated)
        result = repo.get_by_name('Student Loan')
        assert result['original_balance'] == 20000.0

    def test_update_nonexistent_returns_false(self, repo):
        ghost = make_liability()
        ghost['id'] = 'ghost-id'
        result = repo.update(ghost, make_liability(name='New'))
        assert result is False

    def test_update_persists_to_disk(self, repo, tmp_path):
        added = repo.add(make_liability(name='Loan'))
        updated = {**added, 'balance': 15000.0}
        repo.update(added, updated)
        fresh = LiabilityRepository(tmp_path)
        result = fresh.get_by_name('Loan')
        assert result['balance'] == 15000.0

    # ===== UPDATE_BALANCE =====

    def test_update_balance_changes_only_balance(self, repo):
        added = repo.add(make_liability(balance=20000.0))
        result = repo.update_balance(added['id'], 18000.0)
        assert result is True
        found = repo.get_by_id(added['id'])
        assert found['balance'] == 18000.0

    def test_update_balance_returns_false_if_not_found(self, repo):
        result = repo.update_balance('nonexistent', 5000.0)
        assert result is False

    def test_update_balance_persists_to_disk(self, repo, tmp_path):
        added = repo.add(make_liability(balance=20000.0))
        repo.update_balance(added['id'], 15000.0)
        fresh = LiabilityRepository(tmp_path)
        found = fresh.get_by_id(added['id'])
        assert found['balance'] == 15000.0

    # ===== DELETE =====

    def test_delete_removes_liability(self, repo):
        added = repo.add(make_liability(name='Old Loan'))
        repo.delete(added)
        assert repo.get_by_name('Old Loan') is None

    def test_delete_preserves_other_liabilities(self, repo):
        l1 = repo.add(make_liability(name='Loan A'))
        repo.add(make_liability(name='Loan B'))
        repo.delete(l1)
        assert repo.get_by_name('Loan A') is None
        assert repo.get_by_name('Loan B') is not None

    def test_delete_persists_to_disk(self, repo, tmp_path):
        added = repo.add(make_liability(name='Temp Loan'))
        repo.delete(added)
        fresh = LiabilityRepository(tmp_path)
        assert fresh.get_by_name('Temp Loan') is None

    def test_data_persists_across_instances(self, repo, tmp_path):
        repo.add(make_liability(name='Mortgage'))
        repo.add(make_liability(name='Car Loan'))
        fresh = LiabilityRepository(tmp_path)
        names = [l['name'] for l in fresh.get_all()]
        assert 'Mortgage' in names
        assert 'Car Loan' in names