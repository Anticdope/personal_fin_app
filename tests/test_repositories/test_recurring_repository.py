"""
Tests for RecurringRepository
Covers: add, get, update, delete, persistence
"""
import pytest
from data.repositories.recurring_repository import RecurringRepository


@pytest.fixture
def repo(tmp_path):
    return RecurringRepository(tmp_path)


def make_pattern(**overrides):
    data = {
        'title': 'Netflix',
        'amount': -15.99,
        'category': 'Entertainment',
        'account': 'Checking',
        'frequency': 'monthly',
        'start_date': '2024-01-15',
    }
    data.update(overrides)
    return data


class TestRecurringRepository:

    def test_get_all_empty_initially(self, repo):
        assert repo.get_all() == []

    def test_add_assigns_id(self, repo):
        result = repo.add(make_pattern())
        assert 'id' in result
        assert result['id'] is not None

    def test_add_preserves_existing_id(self, repo):
        pattern = make_pattern()
        pattern['id'] = 'my-custom-id'
        result = repo.add(pattern)
        assert result['id'] == 'my-custom-id'

    def test_add_persists_to_disk(self, repo, tmp_path):
        repo.add(make_pattern())
        fresh = RecurringRepository(tmp_path)
        assert len(fresh.get_all()) == 1

    def test_add_multiple_patterns(self, repo):
        repo.add(make_pattern(title='Netflix'))
        repo.add(make_pattern(title='Spotify'))
        patterns = repo.get_all()
        assert len(patterns) == 2

    def test_get_by_id_finds_pattern(self, repo):
        added = repo.add(make_pattern(title='Netflix'))
        result = repo.get_by_id(added['id'])
        assert result is not None
        assert result['title'] == 'Netflix'

    def test_get_by_id_returns_none_if_not_found(self, repo):
        assert repo.get_by_id('nonexistent-id') is None

    def test_update_modifies_pattern(self, repo):
        added = repo.add(make_pattern(title='Netflix'))
        updated = {**added, 'title': 'Netflix Premium', 'amount': -22.99}
        result = repo.update(added['id'], updated)
        assert result is True
        retrieved = repo.get_by_id(added['id'])
        assert retrieved['title'] == 'Netflix Premium'
        assert retrieved['amount'] == -22.99

    def test_update_preserves_id(self, repo):
        added = repo.add(make_pattern())
        original_id = added['id']
        updated = {**added, 'title': 'Changed'}
        repo.update(original_id, updated)
        assert repo.get_by_id(original_id) is not None

    def test_update_nonexistent_returns_false(self, repo):
        result = repo.update('nonexistent-id', make_pattern())
        assert result is False

    def test_update_persists_to_disk(self, repo, tmp_path):
        added = repo.add(make_pattern(title='Netflix'))
        updated = {**added, 'title': 'Netflix Premium'}
        repo.update(added['id'], updated)
        fresh = RecurringRepository(tmp_path)
        pattern = fresh.get_by_id(added['id'])
        assert pattern['title'] == 'Netflix Premium'

    def test_delete_removes_pattern(self, repo):
        added = repo.add(make_pattern())
        repo.delete(added['id'])
        assert repo.get_by_id(added['id']) is None

    def test_delete_preserves_other_patterns(self, repo):
        p1 = repo.add(make_pattern(title='Netflix'))
        p2 = repo.add(make_pattern(title='Spotify'))
        repo.delete(p1['id'])
        assert repo.get_by_id(p2['id']) is not None

    def test_delete_persists_to_disk(self, repo, tmp_path):
        added = repo.add(make_pattern())
        repo.delete(added['id'])
        fresh = RecurringRepository(tmp_path)
        assert len(fresh.get_all()) == 0

    def test_delete_nonexistent_id_does_not_raise(self, repo):
        repo.delete('nonexistent-id')  # Should not raise

    def test_data_persists_across_instances(self, repo, tmp_path):
        repo.add(make_pattern(title='Netflix'))
        repo.add(make_pattern(title='Spotify'))
        fresh = RecurringRepository(tmp_path)
        titles = [p['title'] for p in fresh.get_all()]
        assert 'Netflix' in titles
        assert 'Spotify' in titles