"""
tests/test_repositories/test_category_repository.py

Tests for CategoryRepository - covers default category seeding,
_ensure_default_categories, update/delete behavior, and persistence.
"""
import pytest
from data.repositories.category_repository import CategoryRepository


@pytest.fixture
def repo(tmp_path):
    return CategoryRepository(tmp_path)


def make_category(**overrides):
    data = {'name': 'Groceries', 'color': '#FF0000', 'type': 'expense', 'budget': 0.0}
    data.update(overrides)
    return data


# ===== ADD =====

class TestAdd:

    def test_add_assigns_id_if_missing(self, repo):
        cat = repo.add(make_category())
        assert 'id' in cat
        assert cat['id'].startswith('cat-')

    def test_add_preserves_existing_id(self, repo):
        cat = repo.add(make_category(id='cat-custom'))
        assert cat['id'] == 'cat-custom'

    def test_add_defaults_type_to_expense(self, repo):
        cat = repo.add({'name': 'Misc', 'color': '#000000', 'budget': 0.0})
        assert cat['type'] == 'expense'

    def test_add_preserves_provided_type(self, repo):
        cat = repo.add(make_category(type='savings'))
        assert cat['type'] == 'savings'

    def test_add_persists_to_disk(self, repo):
        repo.add(make_category(name='Dining'))
        fresh = CategoryRepository(repo.data_dir)
        assert fresh.get_by_name('Dining') is not None


# ===== GET =====

class TestGet:

    def test_get_by_id_returns_category(self, repo):
        cat = repo.add(make_category(id='cat-001'))
        result = repo.get_by_id('cat-001')
        assert result is not None
        assert result['name'] == 'Groceries'

    def test_get_by_id_returns_none_if_not_found(self, repo):
        assert repo.get_by_id('nonexistent') is None

    def test_get_by_name_returns_category(self, repo):
        repo.add(make_category(name='Dining'))
        assert repo.get_by_name('Dining') is not None

    def test_get_by_name_returns_none_if_not_found(self, repo):
        assert repo.get_by_name('Ghost') is None


# ===== UPDATE =====

class TestUpdate:

    def test_update_modifies_category(self, repo):
        old = repo.add(make_category(name='Food'))
        new = {**old, 'budget': 500.0}
        repo.update(old, new)
        result = repo.get_by_id(old['id'])
        assert result['budget'] == 500.0

    def test_update_preserves_id(self, repo):
        old = repo.add(make_category())
        new = {'name': 'Updated', 'color': '#00FF00', 'type': 'expense', 'budget': 0.0}
        repo.update(old, new)
        assert repo.get_by_id(old['id']) is not None

    def test_update_preserves_special_flag(self, repo):
        old = repo.add(make_category(special=True))
        new = {**old, 'special': False}
        repo.update(old, new)
        result = repo.get_by_id(old['id'])
        assert result['special'] is True

    def test_update_preserves_type(self, repo):
        old = repo.add(make_category(type='savings'))
        new = {**old, 'type': 'expense'}
        repo.update(old, new)
        result = repo.get_by_id(old['id'])
        assert result['type'] == 'savings'

    def test_update_returns_false_if_not_found(self, repo):
        ghost = make_category(id='cat-ghost')
        assert repo.update(ghost, ghost) is False

    def test_update_persists_to_disk(self, repo):
        old = repo.add(make_category())
        new = {**old, 'budget': 999.0}
        repo.update(old, new)
        fresh = CategoryRepository(repo.data_dir)
        result = fresh.get_by_id(old['id'])
        assert result['budget'] == 999.0


# ===== DELETE =====

class TestDelete:

    def test_delete_removes_category(self, repo):
        cat = repo.add(make_category(name='Dining'))
        repo.delete(cat)
        assert repo.get_by_name('Dining') is None

    def test_delete_preserves_other_categories(self, repo):
        c1 = repo.add(make_category(name='Dining'))
        c2 = repo.add(make_category(name='Gas'))
        repo.delete(c1)
        assert repo.get_by_name('Gas') is not None

    def test_delete_persists_to_disk(self, repo):
        cat = repo.add(make_category(name='Dining'))
        repo.delete(cat)
        fresh = CategoryRepository(repo.data_dir)
        assert fresh.get_by_name('Dining') is None