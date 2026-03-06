"""
Tests for ValidationService and all Schema classes
Covers: schema validation, referential integrity checks, batch validation, sanitization
"""
import pytest
from unittest.mock import MagicMock
from data.validation.schemas import (
    CategorySchema, AccountSchema, AssetSchema, LiabilitySchema,
    TransactionSchema, RecurringTransactionSchema, ValidationError
)
from data.validation.validation_service import ValidationService


# ============================================================
# HELPERS - minimal valid data objects for each type
# ============================================================

def valid_category(**overrides):
    data = {'id': 'cat-001', 'name': 'Groceries', 'color': '#FF0000', 'type': 'expense'}
    data.update(overrides)
    return data

def valid_account(**overrides):
    data = {'id': 'acc-001', 'name': 'Checking', 'type': 'debit', 'balance': 1000.0}
    data.update(overrides)
    return data

def valid_asset(**overrides):
    data = {'id': 'ast-001', 'name': 'Car', 'value': 15000.0}
    data.update(overrides)
    return data

def valid_liability(**overrides):
    data = {'id': 'lib-001', 'name': 'Student Loan', 'balance': 20000.0}
    data.update(overrides)
    return data

def valid_transaction(**overrides):
    data = {'title': 'Coffee', 'amount': -5.0, 'category': 'Food', 'status': 'posted', 'account': 'Checking'}
    data.update(overrides)
    return data

def valid_recurring(**overrides):
    data = {
        'id': 'rec-001', 'title': 'Netflix', 'amount': -15.99,
        'category': 'Entertainment', 'account': 'Checking',
        'frequency': 'monthly', 'start_date': '2024-01-01'
    }
    data.update(overrides)
    return data


# ============================================================
# CategorySchema
# ============================================================

class TestCategorySchema:

    def test_valid_category_passes(self):
        valid, errors = CategorySchema.validate(valid_category())
        assert valid is True
        assert errors == []

    def test_all_valid_types_pass(self):
        for t in ['income', 'expense', 'savings', 'special']:
            valid, errors = CategorySchema.validate(valid_category(type=t))
            assert valid, f"Type '{t}' should be valid"

    def test_missing_id_fails(self):
        data = valid_category()
        del data['id']
        valid, errors = CategorySchema.validate(data)
        assert valid is False
        assert any('id' in e for e in errors)

    def test_missing_name_fails(self):
        data = valid_category()
        del data['name']
        valid, errors = CategorySchema.validate(data)
        assert valid is False

    def test_missing_color_fails(self):
        data = valid_category()
        del data['color']
        valid, errors = CategorySchema.validate(data)
        assert valid is False

    def test_missing_type_fails(self):
        data = valid_category()
        del data['type']
        valid, errors = CategorySchema.validate(data)
        assert valid is False

    def test_empty_name_fails(self):
        valid, errors = CategorySchema.validate(valid_category(name=''))
        assert valid is False
        assert any('name' in e for e in errors)

    def test_invalid_color_no_hash_fails(self):
        valid, errors = CategorySchema.validate(valid_category(color='FF0000'))
        assert valid is False
        assert any('color' in e for e in errors)

    def test_invalid_color_wrong_length_fails(self):
        valid, errors = CategorySchema.validate(valid_category(color='#FFF'))
        assert valid is False

    def test_invalid_type_fails(self):
        valid, errors = CategorySchema.validate(valid_category(type='unknown'))
        assert valid is False
        assert any('type' in e for e in errors)

    def test_optional_budget_valid(self):
        valid, errors = CategorySchema.validate(valid_category(budget=100.0))
        assert valid is True

    def test_optional_budget_invalid_string_fails(self):
        valid, errors = CategorySchema.validate(valid_category(budget='lots'))
        assert valid is False
        assert any('budget' in e for e in errors)

    def test_optional_special_flag(self):
        valid, errors = CategorySchema.validate(valid_category(special=True))
        assert valid is True

    def test_special_must_be_bool(self):
        valid, errors = CategorySchema.validate(valid_category(special='yes'))
        assert valid is False


# ============================================================
# AccountSchema
# ============================================================

class TestAccountSchema:

    def test_valid_debit_account_passes(self):
        valid, errors = AccountSchema.validate(valid_account())
        assert valid is True
        assert errors == []

    def test_valid_credit_account_passes(self):
        valid, errors = AccountSchema.validate(valid_account(type='credit'))
        assert valid is True

    def test_missing_id_fails(self):
        data = valid_account()
        del data['id']
        valid, errors = AccountSchema.validate(data)
        assert valid is False

    def test_missing_name_fails(self):
        data = valid_account()
        del data['name']
        valid, errors = AccountSchema.validate(data)
        assert valid is False

    def test_missing_type_fails(self):
        data = valid_account()
        del data['type']
        valid, errors = AccountSchema.validate(data)
        assert valid is False

    def test_missing_balance_fails(self):
        data = valid_account()
        del data['balance']
        valid, errors = AccountSchema.validate(data)
        assert valid is False

    def test_invalid_type_fails(self):
        valid, errors = AccountSchema.validate(valid_account(type='savings'))
        assert valid is False
        assert any('type' in e for e in errors)

    def test_non_numeric_balance_fails(self):
        valid, errors = AccountSchema.validate(valid_account(balance='lots'))
        assert valid is False
        assert any('balance' in e for e in errors)

    def test_negative_balance_is_valid(self):
        valid, errors = AccountSchema.validate(valid_account(balance=-500.0))
        assert valid is True

    def test_zero_balance_is_valid(self):
        valid, errors = AccountSchema.validate(valid_account(balance=0))
        assert valid is True

    def test_optional_starting_balance_valid(self):
        valid, errors = AccountSchema.validate(valid_account(starting_balance=500.0))
        assert valid is True

    def test_optional_starting_balance_invalid_fails(self):
        valid, errors = AccountSchema.validate(valid_account(starting_balance='abc'))
        assert valid is False


# ============================================================
# AssetSchema
# ============================================================

class TestAssetSchema:

    def test_valid_asset_passes(self):
        valid, errors = AssetSchema.validate(valid_asset())
        assert valid is True
        assert errors == []

    def test_missing_id_fails(self):
        data = valid_asset()
        del data['id']
        valid, errors = AssetSchema.validate(data)
        assert valid is False

    def test_missing_name_fails(self):
        data = valid_asset()
        del data['name']
        valid, errors = AssetSchema.validate(data)
        assert valid is False

    def test_missing_value_fails(self):
        data = valid_asset()
        del data['value']
        valid, errors = AssetSchema.validate(data)
        assert valid is False

    def test_non_numeric_value_fails(self):
        valid, errors = AssetSchema.validate(valid_asset(value='priceless'))
        assert valid is False

    def test_zero_value_is_valid(self):
        valid, errors = AssetSchema.validate(valid_asset(value=0))
        assert valid is True

    def test_optional_original_value_valid(self):
        valid, errors = AssetSchema.validate(valid_asset(original_value=20000.0))
        assert valid is True

    def test_optional_original_value_invalid_fails(self):
        valid, errors = AssetSchema.validate(valid_asset(original_value='unknown'))
        assert valid is False


# ============================================================
# LiabilitySchema
# ============================================================

class TestLiabilitySchema:

    def test_valid_liability_passes(self):
        valid, errors = LiabilitySchema.validate(valid_liability())
        assert valid is True
        assert errors == []

    def test_missing_id_fails(self):
        data = valid_liability()
        del data['id']
        valid, errors = LiabilitySchema.validate(data)
        assert valid is False

    def test_missing_name_fails(self):
        data = valid_liability()
        del data['name']
        valid, errors = LiabilitySchema.validate(data)
        assert valid is False

    def test_missing_balance_fails(self):
        data = valid_liability()
        del data['balance']
        valid, errors = LiabilitySchema.validate(data)
        assert valid is False

    def test_non_numeric_balance_fails(self):
        valid, errors = LiabilitySchema.validate(valid_liability(balance='a lot'))
        assert valid is False

    def test_interest_rate_valid(self):
        valid, errors = LiabilitySchema.validate(valid_liability(interest_rate=5.5))
        assert valid is True

    def test_interest_rate_too_high_fails(self):
        valid, errors = LiabilitySchema.validate(valid_liability(interest_rate=101.0))
        assert valid is False
        assert any('interest_rate' in e for e in errors)

    def test_interest_rate_negative_fails(self):
        valid, errors = LiabilitySchema.validate(valid_liability(interest_rate=-1.0))
        assert valid is False

    def test_interest_rate_zero_is_valid(self):
        valid, errors = LiabilitySchema.validate(valid_liability(interest_rate=0.0))
        assert valid is True

    def test_interest_rate_100_is_valid(self):
        valid, errors = LiabilitySchema.validate(valid_liability(interest_rate=100.0))
        assert valid is True

    def test_optional_original_balance_valid(self):
        valid, errors = LiabilitySchema.validate(valid_liability(original_balance=25000.0))
        assert valid is True


# ============================================================
# TransactionSchema
# ============================================================

class TestTransactionSchema:

    def test_valid_regular_transaction_passes(self):
        valid, errors = TransactionSchema.validate(valid_transaction())
        assert valid is True
        assert errors == []

    def test_valid_pending_status(self):
        valid, errors = TransactionSchema.validate(valid_transaction(status='pending'))
        assert valid is True

    def test_invalid_status_fails(self):
        valid, errors = TransactionSchema.validate(valid_transaction(status='cleared'))
        assert valid is False
        assert any('status' in e for e in errors)

    def test_missing_title_fails(self):
        data = valid_transaction()
        del data['title']
        valid, errors = TransactionSchema.validate(data)
        assert valid is False

    def test_empty_title_fails(self):
        valid, errors = TransactionSchema.validate(valid_transaction(title=''))
        assert valid is False

    def test_missing_amount_fails(self):
        data = valid_transaction()
        del data['amount']
        valid, errors = TransactionSchema.validate(data)
        assert valid is False

    def test_non_numeric_amount_fails(self):
        valid, errors = TransactionSchema.validate(valid_transaction(amount='five'))
        assert valid is False

    def test_missing_category_fails(self):
        data = valid_transaction()
        del data['category']
        valid, errors = TransactionSchema.validate(data)
        assert valid is False

    def test_regular_transaction_without_account_fails(self):
        data = valid_transaction()
        del data['account']
        valid, errors = TransactionSchema.validate(data)
        assert valid is False
        assert any('account' in e for e in errors)

    # Transfer transactions
    def test_valid_transfer_passes(self):
        data = {
            'title': 'Move money', 'amount': -500.0, 'category': 'Transfer',
            'status': 'posted', 'from_account': 'Checking', 'to_account': 'Savings'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is True

    def test_transfer_missing_from_account_fails(self):
        data = {
            'title': 'Move money', 'amount': -500.0, 'category': 'Transfer',
            'status': 'posted', 'to_account': 'Savings'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is False
        assert any('from_account' in e for e in errors)

    def test_transfer_missing_to_account_fails(self):
        data = {
            'title': 'Move money', 'amount': -500.0, 'category': 'Transfer',
            'status': 'posted', 'from_account': 'Checking'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is False
        assert any('to_account' in e for e in errors)

    def test_transfer_same_account_fails(self):
        data = {
            'title': 'Move money', 'amount': -500.0, 'category': 'Transfer',
            'status': 'posted', 'from_account': 'Checking', 'to_account': 'Checking'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is False

    # Debt payment transactions
    def test_valid_debt_payment_passes(self):
        data = {
            'title': 'Visa payment', 'amount': -200.0, 'category': 'Debt Payment',
            'status': 'posted', 'from_account': 'Checking', 'liability': 'Visa'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is True

    def test_debt_payment_missing_from_account_fails(self):
        data = {
            'title': 'Visa payment', 'amount': -200.0, 'category': 'Debt Payment',
            'status': 'posted', 'liability': 'Visa'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is False
        assert any('from_account' in e for e in errors)

    def test_debt_payment_missing_liability_fails(self):
        data = {
            'title': 'Visa payment', 'amount': -200.0, 'category': 'Debt Payment',
            'status': 'posted', 'from_account': 'Checking'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is False
        assert any('liability' in e for e in errors)

    def test_debt_payment_same_source_and_target_fails(self):
        data = {
            'title': 'Visa payment', 'amount': -200.0, 'category': 'Debt Payment',
            'status': 'posted', 'from_account': 'Visa', 'liability': 'Visa'
        }
        valid, errors = TransactionSchema.validate(data)
        assert valid is False


# ============================================================
# RecurringTransactionSchema
# ============================================================

class TestRecurringTransactionSchema:

    def test_valid_recurring_passes(self):
        valid, errors = RecurringTransactionSchema.validate(valid_recurring())
        assert valid is True
        assert errors == []

    def test_all_valid_frequencies(self):
        for freq in ['daily', 'weekly', 'biweekly', 'monthly', 'yearly']:
            valid, errors = RecurringTransactionSchema.validate(valid_recurring(frequency=freq))
            assert valid, f"Frequency '{freq}' should be valid"

    def test_invalid_frequency_fails(self):
        valid, errors = RecurringTransactionSchema.validate(valid_recurring(frequency='hourly'))
        assert valid is False
        assert any('frequency' in e for e in errors)

    def test_missing_start_date_fails(self):
        data = valid_recurring()
        del data['start_date']
        valid, errors = RecurringTransactionSchema.validate(data)
        assert valid is False

    def test_invalid_start_date_format_fails(self):
        valid, errors = RecurringTransactionSchema.validate(valid_recurring(start_date='01/01/2024'))
        assert valid is False
        assert any('start_date' in e for e in errors)

    def test_valid_end_date(self):
        valid, errors = RecurringTransactionSchema.validate(valid_recurring(end_date='2024-12-31'))
        assert valid is True

    def test_invalid_end_date_format_fails(self):
        valid, errors = RecurringTransactionSchema.validate(valid_recurring(end_date='Dec 31 2024'))
        assert valid is False
        assert any('end_date' in e for e in errors)

    def test_missing_required_fields_fail(self):
        for field in ['id', 'title', 'amount', 'category', 'account', 'frequency', 'start_date']:
            data = valid_recurring()
            del data[field]
            valid, errors = RecurringTransactionSchema.validate(data)
            assert valid is False, f"Missing '{field}' should fail validation"


# ============================================================
# ValidationError exception
# ============================================================

class TestValidationError:

    def test_validation_error_is_exception(self):
        with pytest.raises(ValidationError):
            raise ValidationError("test error")

    def test_validation_error_message(self):
        with pytest.raises(ValidationError, match="test error"):
            raise ValidationError("test error")


# ============================================================
# ValidationService - schema delegation
# ============================================================

class TestValidationServiceSchemaDelegation:
    """Tests that ValidationService correctly delegates to schemas"""

    def setup_method(self):
        self.category_repo = MagicMock()
        self.account_repo = MagicMock()
        self.asset_repo = MagicMock()
        self.liability_repo = MagicMock()
        self.service = ValidationService(
            self.category_repo, self.account_repo,
            self.asset_repo, self.liability_repo
        )

    def test_validate_category_valid(self):
        valid, errors = self.service.validate_category(valid_category())
        assert valid is True

    def test_validate_category_invalid(self):
        valid, errors = self.service.validate_category(valid_category(name=''))
        assert valid is False

    def test_validate_category_raises_on_error(self):
        with pytest.raises(ValidationError):
            self.service.validate_category(valid_category(name=''), raise_on_error=True)

    def test_validate_account_valid(self):
        valid, errors = self.service.validate_account(valid_account())
        assert valid is True

    def test_validate_account_raises_on_error(self):
        with pytest.raises(ValidationError):
            self.service.validate_account(valid_account(type='savings'), raise_on_error=True)

    def test_validate_asset_valid(self):
        valid, errors = self.service.validate_asset(valid_asset())
        assert valid is True

    def test_validate_asset_raises_on_error(self):
        with pytest.raises(ValidationError):
            self.service.validate_asset(valid_asset(value='abc'), raise_on_error=True)

    def test_validate_liability_valid(self):
        valid, errors = self.service.validate_liability(valid_liability())
        assert valid is True

    def test_validate_liability_raises_on_error(self):
        with pytest.raises(ValidationError):
            self.service.validate_liability(valid_liability(interest_rate=200), raise_on_error=True)

    def test_validate_transaction_valid(self):
        valid, errors = self.service.validate_transaction(valid_transaction())
        assert valid is True

    def test_validate_transaction_raises_on_error(self):
        with pytest.raises(ValidationError):
            self.service.validate_transaction(valid_transaction(status='nope'), raise_on_error=True)

    def test_validate_recurring_transaction_valid(self):
        valid, errors = self.service.validate_recurring_transaction(valid_recurring())
        assert valid is True

    def test_validate_recurring_raises_on_error(self):
        with pytest.raises(ValidationError):
            self.service.validate_recurring_transaction(
                valid_recurring(frequency='never'), raise_on_error=True
            )


# ============================================================
# ValidationService - referential integrity
# ============================================================

class TestValidationServiceReferentialIntegrity:

    def setup_method(self):
        self.category_repo = MagicMock()
        self.account_repo = MagicMock()
        self.asset_repo = MagicMock()
        self.liability_repo = MagicMock()
        self.service = ValidationService(
            self.category_repo, self.account_repo,
            self.asset_repo, self.liability_repo
        )

    def _setup_repos(self, categories=None, accounts=None, assets=None, liabilities=None):
        self.category_repo.get_all.return_value = categories or []
        self.account_repo.get_all.return_value = accounts or []
        self.asset_repo.get_all.return_value = assets or []
        self.liability_repo.get_all.return_value = liabilities or []

    # check_category_exists
    def test_check_category_exists_true(self):
        self._setup_repos(categories=[{'name': 'Food'}])
        assert self.service.check_category_exists('Food') is True

    def test_check_category_exists_false(self):
        self._setup_repos(categories=[])
        assert self.service.check_category_exists('Food') is False

    # check_account_exists
    def test_check_account_exists_true(self):
        self._setup_repos(accounts=[{'name': 'Checking'}])
        assert self.service.check_account_exists('Checking') is True

    def test_check_account_exists_false(self):
        self._setup_repos(accounts=[])
        assert self.service.check_account_exists('Checking') is False

    # check_asset_exists
    def test_check_asset_exists_true(self):
        self._setup_repos(assets=[{'name': 'Car'}])
        assert self.service.check_asset_exists('Car') is True

    def test_check_asset_exists_false(self):
        self._setup_repos(assets=[])
        assert self.service.check_asset_exists('Car') is False

    # check_liability_exists
    def test_check_liability_exists_true(self):
        self._setup_repos(liabilities=[{'name': 'Mortgage'}])
        assert self.service.check_liability_exists('Mortgage') is True

    def test_check_liability_exists_false(self):
        self._setup_repos(liabilities=[])
        assert self.service.check_liability_exists('Mortgage') is False

    # validate_transaction_references - regular
    def test_transaction_references_valid_regular(self):
        self._setup_repos(
            categories=[{'name': 'Food'}],
            accounts=[{'name': 'Checking'}]
        )
        valid, errors = self.service.validate_transaction_references(valid_transaction())
        assert valid is True
        assert errors == []

    def test_transaction_references_missing_category(self):
        self._setup_repos(accounts=[{'name': 'Checking'}])
        valid, errors = self.service.validate_transaction_references(valid_transaction())
        assert valid is False
        assert any('Food' in e for e in errors)

    def test_transaction_references_missing_account(self):
        self._setup_repos(categories=[{'name': 'Food'}])
        valid, errors = self.service.validate_transaction_references(valid_transaction())
        assert valid is False
        assert any('Checking' in e for e in errors)

    def test_special_categories_skip_category_check(self):
        """Transfer and Debt Payment don't need to be in category list"""
        self._setup_repos(accounts=[{'name': 'Checking'}, {'name': 'Savings'}])
        transfer = {
            'title': 'Move', 'amount': -100.0, 'category': 'Transfer',
            'status': 'posted', 'from_account': 'Checking', 'to_account': 'Savings'
        }
        valid, errors = self.service.validate_transaction_references(transfer)
        assert valid is True

    def test_transfer_references_missing_from_account(self):
        self._setup_repos(accounts=[{'name': 'Savings'}])
        transfer = {
            'title': 'Move', 'amount': -100.0, 'category': 'Transfer',
            'status': 'posted', 'from_account': 'Checking', 'to_account': 'Savings'
        }
        valid, errors = self.service.validate_transaction_references(transfer)
        assert valid is False
        assert any('Checking' in e for e in errors)

    def test_transfer_references_missing_to_account(self):
        self._setup_repos(accounts=[{'name': 'Checking'}])
        transfer = {
            'title': 'Move', 'amount': -100.0, 'category': 'Transfer',
            'status': 'posted', 'from_account': 'Checking', 'to_account': 'Savings'
        }
        valid, errors = self.service.validate_transaction_references(transfer)
        assert valid is False
        assert any('Savings' in e for e in errors)

    def test_debt_payment_references_valid_with_liability(self):
        self._setup_repos(
            accounts=[{'name': 'Checking'}],
            liabilities=[{'name': 'Student Loan'}]
        )
        payment = {
            'title': 'Payment', 'amount': -200.0, 'category': 'Debt Payment',
            'status': 'posted', 'from_account': 'Checking', 'liability': 'Student Loan'
        }
        valid, errors = self.service.validate_transaction_references(payment)
        assert valid is True

    def test_debt_payment_references_valid_with_credit_account(self):
        self._setup_repos(accounts=[{'name': 'Checking'}, {'name': 'Visa'}])
        payment = {
            'title': 'Payment', 'amount': -200.0, 'category': 'Debt Payment',
            'status': 'posted', 'from_account': 'Checking', 'liability': 'Visa'
        }
        valid, errors = self.service.validate_transaction_references(payment)
        assert valid is True

    def test_debt_payment_references_missing_liability(self):
        self._setup_repos(accounts=[{'name': 'Checking'}])
        payment = {
            'title': 'Payment', 'amount': -200.0, 'category': 'Debt Payment',
            'status': 'posted', 'from_account': 'Checking', 'liability': 'Visa'
        }
        valid, errors = self.service.validate_transaction_references(payment)
        assert valid is False


# ============================================================
# ValidationService - batch validation
# ============================================================

class TestValidationServiceBatch:

    def setup_method(self):
        self.category_repo = MagicMock()
        self.account_repo = MagicMock()
        self.asset_repo = MagicMock()
        self.liability_repo = MagicMock()
        self.service = ValidationService(
            self.category_repo, self.account_repo,
            self.asset_repo, self.liability_repo
        )
        self.category_repo.get_all.return_value = []
        self.account_repo.get_all.return_value = []

    def test_validate_categories_batch_all_valid(self):
        cats = [valid_category(id=f'cat-00{i}', name=f'Cat {i}') for i in range(3)]
        all_valid, errors = self.service.validate_categories_batch(cats)
        assert all_valid is True
        assert errors == {}

    def test_validate_categories_batch_with_invalid(self):
        cats = [valid_category(), valid_category(name='', id='cat-002')]
        all_valid, errors = self.service.validate_categories_batch(cats)
        assert all_valid is False
        assert 1 in errors

    def test_validate_accounts_batch_all_valid(self):
        accs = [valid_account(id=f'acc-00{i}', name=f'Acc {i}') for i in range(3)]
        all_valid, errors = self.service.validate_accounts_batch(accs)
        assert all_valid is True
        assert errors == {}

    def test_validate_accounts_batch_with_invalid(self):
        accs = [valid_account(), valid_account(type='unknown', id='acc-002')]
        all_valid, errors = self.service.validate_accounts_batch(accs)
        assert all_valid is False
        assert 1 in errors

    def test_validate_transactions_batch_all_valid(self):
        self.account_repo.get_all.return_value = [{'name': 'Checking'}]
        self.category_repo.get_all.return_value = [{'name': 'Food'}]
        txns = [valid_transaction(), valid_transaction(title='Lunch')]
        all_valid, errors = self.service.validate_transactions_batch(txns)
        assert all_valid is True

    def test_validate_transactions_batch_schema_failure_skips_ref_check(self):
        """If schema fails, that index is recorded without doing ref check"""
        txns = [valid_transaction(status='bad')]
        all_valid, errors = self.service.validate_transactions_batch(txns)
        assert all_valid is False
        assert 0 in errors

    def test_validate_transactions_batch_ref_failure(self):
        """Schema passes but ref check fails"""
        self.account_repo.get_all.return_value = []
        self.category_repo.get_all.return_value = [{'name': 'Food'}]
        txns = [valid_transaction()]  # account 'Checking' doesn't exist
        all_valid, errors = self.service.validate_transactions_batch(txns)
        assert all_valid is False
        assert 0 in errors

    def test_empty_batch_returns_valid(self):
        all_valid, errors = self.service.validate_categories_batch([])
        assert all_valid is True
        assert errors == {}


# ============================================================
# ValidationService - sanitization
# ============================================================

class TestValidationServiceSanitization:

    def setup_method(self):
        self.service = ValidationService(
            MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )

    def test_sanitize_category_trims_name(self):
        result = self.service.sanitize_category({'name': '  Groceries  ', 'color': '#FF0000', 'budget': 100, 'special': False})
        assert result['name'] == 'Groceries'

    def test_sanitize_category_trims_color(self):
        result = self.service.sanitize_category({'name': 'Food', 'color': ' #FF0000 ', 'budget': 0, 'special': False})
        assert result['color'] == '#FF0000'

    def test_sanitize_category_converts_budget_to_float(self):
        result = self.service.sanitize_category({'name': 'Food', 'color': '#FF0000', 'budget': '150', 'special': False})
        assert result['budget'] == 150.0
        assert isinstance(result['budget'], float)

    def test_sanitize_category_defaults_budget_to_zero(self):
        result = self.service.sanitize_category({'name': 'Food', 'color': '#FF0000', 'special': False})
        assert result['budget'] == 0.0

    def test_sanitize_account_trims_name(self):
        result = self.service.sanitize_account({'name': '  Checking  ', 'balance': 100.0})
        assert result['name'] == 'Checking'

    def test_sanitize_account_converts_balance_to_float(self):
        result = self.service.sanitize_account({'name': 'Checking', 'balance': '500'})
        assert result['balance'] == 500.0
        assert isinstance(result['balance'], float)

    def test_sanitize_account_converts_starting_balance(self):
        result = self.service.sanitize_account({'name': 'Checking', 'balance': 100.0, 'starting_balance': '200'})
        assert result['starting_balance'] == 200.0

    def test_sanitize_transaction_trims_title(self):
        result = self.service.sanitize_transaction({'title': '  Coffee  ', 'amount': -5.0, 'category': 'Food', 'status': 'posted'})
        assert result['title'] == 'Coffee'

    def test_sanitize_transaction_converts_amount_to_float(self):
        result = self.service.sanitize_transaction({'title': 'Coffee', 'amount': '-5', 'category': 'Food', 'status': 'posted'})
        assert result['amount'] == -5.0
        assert isinstance(result['amount'], float)

    def test_sanitize_transaction_defaults_status_to_posted(self):
        result = self.service.sanitize_transaction({'title': 'Coffee', 'amount': -5.0, 'category': 'Food'})
        assert result['status'] == 'posted'

    def test_sanitize_transaction_trims_account(self):
        result = self.service.sanitize_transaction({'title': 'x', 'amount': -1.0, 'category': 'y', 'status': 'posted', 'account': '  Checking  '})
        assert result['account'] == 'Checking'

    def test_sanitize_asset_trims_name(self):
        result = self.service.sanitize_asset({'name': '  Car  ', 'value': 15000.0})
        assert result['name'] == 'Car'

    def test_sanitize_asset_converts_value_to_float(self):
        result = self.service.sanitize_asset({'name': 'Car', 'value': '15000'})
        assert result['value'] == 15000.0

    def test_sanitize_asset_converts_original_value(self):
        result = self.service.sanitize_asset({'name': 'Car', 'value': 15000.0, 'original_value': '20000'})
        assert result['original_value'] == 20000.0

    def test_sanitize_liability_trims_name(self):
        result = self.service.sanitize_liability({'name': '  Mortgage  ', 'balance': 200000.0})
        assert result['name'] == 'Mortgage'

    def test_sanitize_liability_converts_balance_to_float(self):
        result = self.service.sanitize_liability({'name': 'Mortgage', 'balance': '200000'})
        assert result['balance'] == 200000.0

    def test_sanitize_liability_converts_interest_rate(self):
        result = self.service.sanitize_liability({'name': 'Mortgage', 'balance': 200000.0, 'interest_rate': '3.5'})
        assert result['interest_rate'] == 3.5