"""
tests/test_repositories/test_transaction_repository.py

Tests for TransactionRepository - extended coverage
"""
import pytest
from data.repositories.transaction_repository import TransactionRepository


@pytest.fixture
def repo(tmp_path):
    return TransactionRepository(tmp_path)


def make_transaction(**overrides):
    data = {
        'title': 'Coffee', 'amount': -5.0,
        'category': 'Food', 'status': 'posted', 'account': 'Checking'
    }
    data.update(overrides)
    return data


class TestTransactionRepository:

    # ===== ADD =====

    def test_add_transaction_to_specific_day(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Coffee'))
        transactions = repo.get_day_transactions(2024, 1, 15)
        assert any(t['title'] == 'Coffee' for t in transactions)

    def test_add_multiple_transactions_same_day(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Coffee'))
        repo.add_transaction(2024, 1, 15, make_transaction(title='Lunch'))
        transactions = repo.get_day_transactions(2024, 1, 15)
        assert len(transactions) == 2

    def test_add_transactions_different_days(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Coffee'))
        repo.add_transaction(2024, 1, 20, make_transaction(title='Dinner'))
        assert len(repo.get_day_transactions(2024, 1, 15)) == 1
        assert len(repo.get_day_transactions(2024, 1, 20)) == 1

    def test_add_transactions_different_months(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Jan'))
        repo.add_transaction(2024, 2, 10, make_transaction(title='Feb'))
        assert repo.get_day_transactions(2024, 1, 15)[0]['title'] == 'Jan'
        assert repo.get_day_transactions(2024, 2, 10)[0]['title'] == 'Feb'

    def test_add_transaction_creates_month_file(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction())
        assert (repo.data_dir / '2024-01.json').exists()

    def test_json_format_is_valid(self, repo):
        import json
        repo.add_transaction(2024, 1, 15, make_transaction())
        file_path = repo.data_dir / '2024-01.json'
        with open(file_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert '15' in data

    # ===== GET =====

    def test_get_month_data_returns_empty_dict(self, repo):
        data = repo.get_month_data(2024, 1)
        assert data == {}

    def test_get_day_transactions_returns_empty_list(self, repo):
        transactions = repo.get_day_transactions(2024, 1, 15)
        assert transactions == []

    def test_get_all_transactions_for_month(self, repo):
        repo.add_transaction(2024, 1, 1, make_transaction(title='A'))
        repo.add_transaction(2024, 1, 15, make_transaction(title='B'))
        repo.add_transaction(2024, 1, 31, make_transaction(title='C'))
        data = repo.get_month_data(2024, 1)
        all_titles = [t['title'] for day in data.values() for t in day]
        assert set(all_titles) == {'A', 'B', 'C'}

    # ===== UPDATE =====

    def test_update_transaction_modifies_data(self, repo):
        txn = make_transaction(title='Coffee', amount=-5.0)
        repo.add_transaction(2024, 1, 15, txn)
        old = repo.get_day_transactions(2024, 1, 15)[0]
        updated = {**old, 'title': 'Fancy Coffee', 'amount': -6.0}
        result = repo.update_transaction(2024, 1, 15, old, updated)
        assert result is True
        transactions = repo.get_day_transactions(2024, 1, 15)
        assert transactions[0]['title'] == 'Fancy Coffee'
        assert transactions[0]['amount'] == -6.0

    def test_update_transaction_persists_to_disk(self, repo):
        txn = make_transaction(title='Coffee')
        repo.add_transaction(2024, 1, 15, txn)
        old = repo.get_day_transactions(2024, 1, 15)[0]
        updated = {**old, 'title': 'Updated'}
        repo.update_transaction(2024, 1, 15, old, updated)
        fresh = TransactionRepository(repo.data_dir)
        assert fresh.get_day_transactions(2024, 1, 15)[0]['title'] == 'Updated'

    def test_update_transaction_returns_false_if_not_found(self, repo):
        txn = make_transaction(title='Coffee')
        repo.add_transaction(2024, 1, 15, txn)
        ghost = make_transaction(title='Ghost')
        result = repo.update_transaction(2024, 1, 15, ghost, make_transaction(title='New'))
        assert result is False

    def test_update_transaction_preserves_other_transactions(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Coffee'))
        repo.add_transaction(2024, 1, 15, make_transaction(title='Lunch'))
        transactions = repo.get_day_transactions(2024, 1, 15)
        coffee = next(t for t in transactions if t['title'] == 'Coffee')
        updated = {**coffee, 'title': 'Espresso'}
        repo.update_transaction(2024, 1, 15, coffee, updated)
        final = repo.get_day_transactions(2024, 1, 15)
        assert any(t['title'] == 'Espresso' for t in final)
        assert any(t['title'] == 'Lunch' for t in final)

    def test_update_transaction_on_empty_day_returns_false(self, repo):
        result = repo.update_transaction(2024, 1, 15,
                                         make_transaction(), make_transaction(title='New'))
        assert result is False

    # ===== DELETE =====

    def test_delete_transaction_removes_it(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Coffee'))
        txn = repo.get_day_transactions(2024, 1, 15)[0]
        repo.delete_transaction(2024, 1, 15, txn)
        assert repo.get_day_transactions(2024, 1, 15) == []

    def test_delete_transaction_persists_to_disk(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction())
        txn = repo.get_day_transactions(2024, 1, 15)[0]
        repo.delete_transaction(2024, 1, 15, txn)
        fresh = TransactionRepository(repo.data_dir)
        assert fresh.get_day_transactions(2024, 1, 15) == []

    def test_delete_preserves_other_transactions(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Coffee'))
        repo.add_transaction(2024, 1, 15, make_transaction(title='Lunch'))
        transactions = repo.get_day_transactions(2024, 1, 15)
        coffee = next(t for t in transactions if t['title'] == 'Coffee')
        repo.delete_transaction(2024, 1, 15, coffee)
        remaining = repo.get_day_transactions(2024, 1, 15)
        assert len(remaining) == 1
        assert remaining[0]['title'] == 'Lunch'

    def test_delete_last_transaction_removes_day_key(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction())
        txn = repo.get_day_transactions(2024, 1, 15)[0]
        repo.delete_transaction(2024, 1, 15, txn)
        data = repo.get_month_data(2024, 1)
        assert '15' not in data

    # ===== SAVE_MONTH_DATA =====

    def test_save_month_data_persists(self, repo):
        data = {'15': [make_transaction(title='Manual')]}
        repo.save_month_data(2024, 1, data)
        fresh = TransactionRepository(repo.data_dir)
        assert fresh.get_day_transactions(2024, 1, 15)[0]['title'] == 'Manual'

    def test_save_month_data_overwrites_existing(self, repo):
        repo.add_transaction(2024, 1, 15, make_transaction(title='Old'))
        repo.save_month_data(2024, 1, {'15': [make_transaction(title='New')]})
        transactions = repo.get_day_transactions(2024, 1, 15)
        assert len(transactions) == 1
        assert transactions[0]['title'] == 'New'

    # ===== JSON FORMAT =====