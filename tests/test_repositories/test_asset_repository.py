"""
tests/test_repositories/test_asset_repository.py

Tests for AssetRepository - covers validation paths, default field population,
update/delete behavior, and persistence.
"""
import pytest
from unittest.mock import MagicMock
from data.repositories.asset_repository import AssetRepository


@pytest.fixture
def repo(tmp_path):
    return AssetRepository(tmp_path)


@pytest.fixture
def repo_with_validation(tmp_path):
    validation = MagicMock()
    validation.validate_asset.return_value = (True, [])
    validation.validate_assets_batch.return_value = (True, {})
    return AssetRepository(tmp_path, validation_service=validation)


def make_asset(**overrides):
    data = {'name': 'Car', 'value': 15000.0}
    data.update(overrides)
    return data


# ===== DEFAULT FIELD POPULATION =====

class TestDefaultFields:

    def test_add_assigns_id_if_missing(self, repo):
        asset = repo.add(make_asset())
        assert 'id' in asset
        assert asset['id'].startswith('ast-')

    def test_add_preserves_existing_id(self, repo):
        asset = repo.add({'id': 'ast-custom', 'name': 'Car', 'value': 15000.0})
        assert asset['id'] == 'ast-custom'

    def test_add_defaults_value_to_zero(self, repo):
        asset = repo.add({'name': 'Mystery Asset'})
        assert asset['value'] == 0.0

    def test_add_preserves_provided_value(self, repo):
        asset = repo.add(make_asset(value=50000.0))
        assert asset['value'] == 50000.0


# ===== GET OPERATIONS =====

class TestGetOperations:

    def test_get_all_empty_initially(self, repo):
        assert repo.get_all() == []

    def test_get_by_id_returns_asset(self, repo):
        repo.add({'id': 'ast-001', 'name': 'House', 'value': 300000.0})
        result = repo.get_by_id('ast-001')
        assert result is not None
        assert result['name'] == 'House'

    def test_get_by_id_returns_none_if_not_found(self, repo):
        assert repo.get_by_id('nonexistent') is None

    def test_get_by_name_returns_asset(self, repo):
        repo.add(make_asset(name='Boat'))
        assert repo.get_by_name('Boat') is not None

    def test_get_by_name_returns_none_if_not_found(self, repo):
        assert repo.get_by_name('Ghost') is None


# ===== UPDATE =====

class TestUpdate:

    def test_update_modifies_value(self, repo):
        old = repo.add(make_asset())
        new = {**old, 'value': 12000.0}
        repo.update(old, new)
        assert repo.get_by_id(old['id'])['value'] == 12000.0

    def test_update_preserves_id(self, repo):
        old = repo.add(make_asset())
        new = {'name': 'New Car', 'value': 12000.0}
        repo.update(old, new)
        result = repo.get_by_id(old['id'])
        assert result is not None

    def test_update_returns_false_if_not_found(self, repo):
        ghost = {'id': 'ast-ghost', 'name': 'Ghost', 'value': 0.0}
        assert repo.update(ghost, ghost) is False

    def test_update_persists_to_disk(self, repo):
        old = repo.add(make_asset())
        new = {**old, 'value': 9999.0}
        repo.update(old, new)
        fresh = AssetRepository(repo.data_dir)
        assert fresh.get_by_id(old['id'])['value'] == 9999.0


# ===== DELETE =====

class TestDelete:

    def test_delete_removes_asset(self, repo):
        asset = repo.add(make_asset())
        repo.delete(asset)
        assert repo.get_by_name('Car') is None

    def test_delete_preserves_other_assets(self, repo):
        a1 = repo.add(make_asset(name='Car'))
        a2 = repo.add(make_asset(name='Boat'))
        repo.delete(a1)
        assert repo.get_by_name('Boat') is not None

    def test_delete_persists_to_disk(self, repo):
        asset = repo.add(make_asset())
        repo.delete(asset)
        fresh = AssetRepository(repo.data_dir)
        assert fresh.get_by_name('Car') is None


# ===== VALIDATION PATHS =====

class TestValidationPaths:

    def test_add_calls_validate(self, repo_with_validation):
        repo_with_validation.add(make_asset())
        repo_with_validation.validation_service.validate_asset.assert_called()

    def test_add_raises_on_validation_failure(self, tmp_path):
        validation = MagicMock()
        validation.validate_asset.return_value = (False, ['value must be numeric'])
        repo = AssetRepository(tmp_path, validation_service=validation)
        with pytest.raises(ValueError, match='validation failed'):
            repo.add(make_asset())

    def test_update_calls_validate(self, repo_with_validation):
        old = repo_with_validation.add(make_asset())
        new = {**old, 'value': 10000.0}
        repo_with_validation.update(old, new)
        assert repo_with_validation.validation_service.validate_asset.call_count >= 2

    def test_update_raises_on_validation_failure(self, tmp_path):
        repo_no_val = AssetRepository(tmp_path)
        old = repo_no_val.add(make_asset())

        validation = MagicMock()
        validation.validate_asset.return_value = (False, ['value invalid'])
        validation.validate_assets_batch.return_value = (True, {})
        repo = AssetRepository(tmp_path, validation_service=validation)
        with pytest.raises(ValueError, match='validation failed'):
            repo.update(old, {**old, 'value': -1.0})

    def test_save_all_raises_on_validation_failure(self, tmp_path):
        validation = MagicMock()
        validation.validate_asset.return_value = (False, ['name missing'])
        validation.validate_assets_batch.return_value = (True, {})  # save_all uses per-item validation
        # Actually save_all loops individually in asset_repository
        repo = AssetRepository(tmp_path, validation_service=validation)
        with pytest.raises(ValueError, match='validation failed'):
            repo.save_all([make_asset()])

    def test_no_validation_service_does_not_raise(self, repo):
        asset = repo.add(make_asset())
        assert asset is not None


# ===== PERSISTENCE =====

class TestPersistence:

    def test_data_persists_across_instances(self, repo):
        repo.add(make_asset(name='House'))
        fresh = AssetRepository(repo.data_dir)
        assert fresh.get_by_name('House') is not None

    def test_multiple_assets_persist(self, repo):
        repo.add(make_asset(name='Car'))
        repo.add(make_asset(name='Boat'))
        fresh = AssetRepository(repo.data_dir)
        assert len(fresh.get_all()) == 2