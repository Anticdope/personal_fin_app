import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_account():
    """Create a sample debit account"""
    return {
        'id': 'acc-test123',
        'name': 'Test Checking',
        'type': 'debit',
        'balance': 1000.0,
        'closed': False
    }


@pytest.fixture
def sample_credit_account():
    """Create a sample credit account with debt fields"""
    return {
        'id': 'acc-credit123',
        'name': 'Test Credit Card',
        'type': 'credit',
        'balance': 500.0,
        'original_balance': 1000.0,
        'interest_rate': 18.99,
        'minimum_payment': 25.0,
        'payment_due_day': 15,
        'closed': False
    }


@pytest.fixture
def sample_liability():
    """Create a sample liability"""
    return {
        'id': 'lib-test123',
        'name': 'Car Loan',
        'balance': 15000.0,
        'original_balance': 20000.0,
        'interest_rate': 5.5,
        'minimum_payment': 350.0,
        'payment_due_day': 1
    }


@pytest.fixture
def sample_transaction():
    """Create a sample transaction"""
    return {
        'id': 'txn-test123',
        'title': 'Grocery Shopping',
        'amount': -50.0,
        'category': 'Groceries',
        'account': 'Test Checking',
        'account_id': 'acc-test123',
        'status': 'posted'
    }


@pytest.fixture
def sample_transfer():
    """Create a sample transfer transaction"""
    return {
        'id': 'txn-transfer123',
        'title': 'Transfer to Savings',
        'amount': 100.0,
        'category': 'Transfer',
        'source_account': 'Test Checking',
        'target_account': 'Test Savings',
        'status': 'posted'
    }


@pytest.fixture
def sample_debt_payment():
    """Create a sample debt payment transaction"""
    return {
        'id': 'txn-debt123',
        'title': 'Credit Card Payment',
        'amount': 100.0,
        'category': 'Debt Payment',
        'source_account': 'Test Checking',
        'target_debt': 'Test Credit Card',
        'target_type': 'credit',
        'status': 'posted'
    }