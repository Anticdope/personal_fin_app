"""
Tests for RecurringService
Covers: CRUD operations, pattern generation, frequency calculations,
auto-posting, auto_post_due_transactions, deletion of future transactions
"""
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, call
from data.services.recurring_service import RecurringService
from data.repositories.recurring_repository import RecurringRepository
from data.repositories.transaction_repository import TransactionRepository


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def repos(tmp_path):
    recurring_repo = RecurringRepository(tmp_path)
    transaction_repo = TransactionRepository(tmp_path)
    return recurring_repo, transaction_repo


@pytest.fixture
def service(repos):
    return RecurringService(*repos)


def make_pattern(**overrides):
    data = {
        'id': 'rec-001',
        'title': 'Netflix',
        'amount': -15.99,
        'category': 'Entertainment',
        'account': 'Checking',
        'frequency': 'monthly',
        'start_date': '2024-01-15',
    }
    data.update(overrides)
    return data


# ============================================================
# generate_pending_transactions - frequency correctness
# ============================================================

class TestGeneratePendingTransactions:

    def test_monthly_generates_correct_dates(self, service):
        pattern = make_pattern(start_date='2024-01-15', frequency='monthly')
        start = date(2024, 1, 15)
        end = date(2024, 3, 15)
        generated = service.generate_pending_transactions(pattern, start, end)
        dates = [g['date'] for g in generated]
        assert date(2024, 1, 15) in dates
        assert date(2024, 2, 15) in dates
        assert date(2024, 3, 15) in dates
        assert len(dates) == 3

    def test_weekly_generates_correct_dates(self, service):
        pattern = make_pattern(start_date='2024-01-01', frequency='weekly')
        start = date(2024, 1, 1)
        end = date(2024, 1, 22)
        generated = service.generate_pending_transactions(pattern, start, end)
        dates = [g['date'] for g in generated]
        assert date(2024, 1, 1) in dates
        assert date(2024, 1, 8) in dates
        assert date(2024, 1, 15) in dates
        assert date(2024, 1, 22) in dates
        assert len(dates) == 4

    def test_biweekly_generates_correct_dates(self, service):
        pattern = make_pattern(start_date='2024-01-01', frequency='biweekly')
        start = date(2024, 1, 1)
        end = date(2024, 2, 1)
        generated = service.generate_pending_transactions(pattern, start, end)
        dates = [g['date'] for g in generated]
        assert date(2024, 1, 1) in dates
        assert date(2024, 1, 15) in dates
        assert date(2024, 1, 29) in dates
        assert len(dates) == 3

    def test_daily_generates_correct_dates(self, service):
        pattern = make_pattern(start_date='2024-01-01', frequency='daily')
        start = date(2024, 1, 1)
        end = date(2024, 1, 5)
        generated = service.generate_pending_transactions(pattern, start, end)
        assert len(generated) == 5

    def test_yearly_generates_correct_dates(self, service):
        pattern = make_pattern(start_date='2024-01-15', frequency='yearly')
        start = date(2024, 1, 15)
        end = date(2026, 1, 15)
        generated = service.generate_pending_transactions(pattern, start, end)
        dates = [g['date'] for g in generated]
        assert date(2024, 1, 15) in dates
        assert date(2025, 1, 15) in dates
        assert date(2026, 1, 15) in dates
        assert len(dates) == 3

    def test_monthly_wraps_year_correctly(self, service):
        pattern = make_pattern(start_date='2024-11-15', frequency='monthly')
        start = date(2024, 11, 15)
        end = date(2025, 2, 15)
        generated = service.generate_pending_transactions(pattern, start, end)
        dates = [g['date'] for g in generated]
        assert date(2024, 11, 15) in dates
        assert date(2024, 12, 15) in dates
        assert date(2025, 1, 15) in dates
        assert date(2025, 2, 15) in dates

    def test_does_not_generate_before_pattern_start(self, service):
        pattern = make_pattern(start_date='2024-03-01', frequency='monthly')
        start = date(2024, 1, 1)
        end = date(2024, 4, 1)
        generated = service.generate_pending_transactions(pattern, start, end)
        dates = [g['date'] for g in generated]
        assert date(2024, 1, 1) not in dates
        assert date(2024, 2, 1) not in dates
        assert date(2024, 3, 1) in dates

    def test_respects_pattern_end_date(self, service):
        pattern = make_pattern(start_date='2024-01-01', frequency='monthly', end_date='2024-02-01')
        start = date(2024, 1, 1)
        end = date(2024, 6, 1)
        generated = service.generate_pending_transactions(pattern, start, end)
        dates = [g['date'] for g in generated]
        assert date(2024, 3, 1) not in dates
        assert len(dates) == 2

    def test_generates_pending_status_transactions(self, service):
        pattern = make_pattern(start_date='2024-01-15', frequency='monthly')
        start = date(2024, 1, 15)
        end = date(2024, 1, 15)
        generated = service.generate_pending_transactions(pattern, start, end)
        assert generated[0]['transaction']['status'] == 'pending'

    def test_generated_transaction_has_recurring_id(self, service):
        pattern = make_pattern(id='rec-abc', start_date='2024-01-15', frequency='monthly')
        start = date(2024, 1, 15)
        end = date(2024, 1, 15)
        generated = service.generate_pending_transactions(pattern, start, end)
        assert generated[0]['transaction']['recurring_id'] == 'rec-abc'

    def test_generated_transaction_has_auto_post_date(self, service):
        pattern = make_pattern(start_date='2024-01-15', frequency='monthly')
        start = date(2024, 1, 15)
        end = date(2024, 1, 15)
        generated = service.generate_pending_transactions(pattern, start, end)
        assert generated[0]['transaction']['auto_post_date'] == '2024-01-15'

    def test_generated_transactions_saved_to_repo(self, repos, service):
        _, transaction_repo = repos
        pattern = make_pattern(start_date='2024-01-15', frequency='monthly')
        start = date(2024, 1, 15)
        end = date(2024, 1, 15)
        service.generate_pending_transactions(pattern, start, end)
        saved = transaction_repo.get_day_transactions(2024, 1, 15)
        assert any(t['title'] == 'Netflix' for t in saved)

    def test_empty_range_generates_nothing(self, service):
        pattern = make_pattern(start_date='2024-06-01', frequency='monthly')
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        generated = service.generate_pending_transactions(pattern, start, end)
        assert generated == []

    def test_unknown_frequency_generates_one_then_stops(self, service):
        pattern = make_pattern(start_date='2024-01-01', frequency='hourly')
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        generated = service.generate_pending_transactions(pattern, start, end)
        assert len(generated) == 1


# ============================================================
# post_pending_transactions
# ============================================================

class TestPostPendingTransactions:

    def test_posts_due_pending_transaction(self, repos, service):
        _, transaction_repo = repos
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-001',
            'auto_post_date': yesterday
        }
        today = date.today()
        transaction_repo.add_transaction(today.year, today.month, today.day, transaction)
        posted = service.post_pending_transactions(today.year, today.month, today.day)
        assert len(posted) == 1
        assert posted[0]['status'] == 'posted'

    def test_does_not_post_future_pending_transaction(self, repos, service):
        _, transaction_repo = repos
        future = (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-001',
            'auto_post_date': future
        }
        today = date.today()
        transaction_repo.add_transaction(today.year, today.month, today.day, transaction)
        posted = service.post_pending_transactions(today.year, today.month, today.day)
        assert len(posted) == 0

    def test_skips_already_posted_transactions(self, repos, service):
        _, transaction_repo = repos
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'posted', 'recurring_id': 'rec-001',
            'auto_post_date': yesterday
        }
        today = date.today()
        transaction_repo.add_transaction(today.year, today.month, today.day, transaction)
        posted = service.post_pending_transactions(today.year, today.month, today.day)
        assert len(posted) == 0

    def test_skips_manual_pending_without_auto_post_date(self, repos, service):
        _, transaction_repo = repos
        transaction = {
            'title': 'Manual', 'amount': -50.0,
            'category': 'Food', 'account': 'Checking',
            'status': 'pending'
            # No auto_post_date
        }
        today = date.today()
        transaction_repo.add_transaction(today.year, today.month, today.day, transaction)
        posted = service.post_pending_transactions(today.year, today.month, today.day)
        assert len(posted) == 0

    def test_returns_empty_for_day_with_no_transactions(self, service):
        posted = service.post_pending_transactions(2024, 1, 1)
        assert posted == []


# ============================================================
# delete_future_recurring_transactions
# ============================================================

class TestDeleteFutureRecurringTransactions:

    def test_deletes_future_pending_transactions(self, repos, service):
        _, transaction_repo = repos
        future = date.today() + timedelta(days=30)
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-001',
            'auto_post_date': future.strftime('%Y-%m-%d')
        }
        transaction_repo.add_transaction(future.year, future.month, future.day, transaction)
        deleted_count = service.delete_future_recurring_transactions('rec-001', date.today())
        assert deleted_count >= 1
        saved = transaction_repo.get_day_transactions(future.year, future.month, future.day)
        assert not any(t.get('recurring_id') == 'rec-001' for t in saved)

    def test_does_not_delete_posted_transactions(self, repos, service):
        _, transaction_repo = repos
        future = date.today() + timedelta(days=30)
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'posted', 'recurring_id': 'rec-001',
            'auto_post_date': future.strftime('%Y-%m-%d')
        }
        transaction_repo.add_transaction(future.year, future.month, future.day, transaction)
        service.delete_future_recurring_transactions('rec-001', date.today())
        saved = transaction_repo.get_day_transactions(future.year, future.month, future.day)
        assert any(t.get('recurring_id') == 'rec-001' for t in saved)

    def test_does_not_delete_different_recurring_id(self, repos, service):
        _, transaction_repo = repos
        future = date.today() + timedelta(days=30)
        transaction = {
            'title': 'Spotify', 'amount': -9.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-999',
            'auto_post_date': future.strftime('%Y-%m-%d')
        }
        transaction_repo.add_transaction(future.year, future.month, future.day, transaction)
        service.delete_future_recurring_transactions('rec-001', date.today())
        saved = transaction_repo.get_day_transactions(future.year, future.month, future.day)
        assert any(t.get('recurring_id') == 'rec-999' for t in saved)


# ============================================================
# CRUD - get_all, add, update, delete recurring patterns
# ============================================================

class TestRecurringCRUD:

    def test_get_all_returns_empty_initially(self, service):
        assert service.get_all_recurring() == []

    def test_add_pattern_assigns_id(self, service):
        pattern_id = service.add_recurring_pattern(make_pattern())
        assert pattern_id is not None
        assert len(pattern_id) > 0

    def test_add_pattern_persists(self, service):
        service.add_recurring_pattern(make_pattern(title='Spotify'))
        patterns = service.get_all_recurring()
        assert any(p['title'] == 'Spotify' for p in patterns)

    def test_add_pattern_returns_id(self, service):
        pattern_id = service.add_recurring_pattern(make_pattern())
        patterns = service.get_all_recurring()
        assert any(p['id'] == pattern_id for p in patterns)

    def test_update_pattern_modifies_data(self, service):
        pattern_id = service.add_recurring_pattern(make_pattern(title='Netflix'))
        updated = make_pattern(title='Netflix Updated', amount=-20.0)
        service.update_recurring_pattern(pattern_id, updated)
        patterns = service.get_all_recurring()
        pattern = next(p for p in patterns if p['id'] == pattern_id)
        assert pattern['amount'] == -20.0

    def test_update_pattern_preserves_id(self, service):
        pattern_id = service.add_recurring_pattern(make_pattern())
        service.update_recurring_pattern(pattern_id, make_pattern(title='Updated'))
        patterns = service.get_all_recurring()
        assert any(p['id'] == pattern_id for p in patterns)

    def test_delete_pattern_removes_it(self, service):
        pattern_id = service.add_recurring_pattern(make_pattern())
        service.delete_recurring_pattern(pattern_id)
        patterns = service.get_all_recurring()
        assert not any(p['id'] == pattern_id for p in patterns)

    def test_delete_pattern_preserves_others(self, service):
        id1 = service.add_recurring_pattern(make_pattern(title='Netflix'))
        id2 = service.add_recurring_pattern(make_pattern(title='Spotify'))
        service.delete_recurring_pattern(id1)
        patterns = service.get_all_recurring()
        assert any(p['id'] == id2 for p in patterns)

    def test_multiple_patterns_can_be_added(self, service):
        service.add_recurring_pattern(make_pattern(title='Netflix'))
        service.add_recurring_pattern(make_pattern(title='Spotify'))
        service.add_recurring_pattern(make_pattern(title='Hulu'))
        assert len(service.get_all_recurring()) == 3


# ============================================================
# auto_post_due_transactions
# ============================================================

class TestAutoPostDueTransactions:

    def test_auto_post_returns_count(self, service):
        count = service.auto_post_due_transactions()
        assert isinstance(count, int)
        assert count >= 0

    def test_auto_post_posts_overdue_transactions(self, repos, service):
        _, transaction_repo = repos
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = date.today()
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-001',
            'auto_post_date': yesterday
        }
        transaction_repo.add_transaction(today.year, today.month, today.day, transaction)
        count = service.auto_post_due_transactions()
        assert count >= 1

    def test_auto_post_does_not_post_future_transactions(self, repos, service):
        _, transaction_repo = repos
        future = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        today = date.today()
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-001',
            'auto_post_date': future
        }
        transaction_repo.add_transaction(today.year, today.month, today.day, transaction)
        count = service.auto_post_due_transactions()
        assert count == 0

    def test_auto_post_checks_previous_month(self, repos, service):
        _, transaction_repo = repos
        today = date.today()
        if today.month == 1:
            prev_year, prev_month = today.year - 1, 12
        else:
            prev_year, prev_month = today.year, today.month - 1
        prev_date = date(prev_year, prev_month, 1)
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-001',
            'auto_post_date': prev_date.strftime('%Y-%m-%d')
        }
        transaction_repo.add_transaction(prev_year, prev_month, 1, transaction)
        count = service.auto_post_due_transactions()
        assert count >= 1

    def test_auto_post_with_no_transactions_returns_zero(self, service):
        count = service.auto_post_due_transactions()
        assert count == 0

    def test_auto_post_updates_status_to_posted(self, repos, service):
        _, transaction_repo = repos
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = date.today()
        transaction = {
            'title': 'Netflix', 'amount': -15.99,
            'category': 'Entertainment', 'account': 'Checking',
            'status': 'pending', 'recurring_id': 'rec-001',
            'auto_post_date': yesterday
        }
        transaction_repo.add_transaction(today.year, today.month, today.day, transaction)
        service.auto_post_due_transactions()
        saved = transaction_repo.get_day_transactions(today.year, today.month, today.day)
        netflix = next(t for t in saved if t['title'] == 'Netflix')
        assert netflix['status'] == 'posted'