"""
run_tests.py - Test runner script

Place this in your project root directory
"""
import subprocess
import sys

def run_tests():
    """Run all tests with coverage"""
    
    print("=" * 70)
    print("RUNNING ALL TESTS FOR PERSONAL FINANCE MANAGER")
    print("=" * 70)
    print()
    
    # Run tests with verbose output and coverage
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--cov=data',
        '--cov=ui',
        '--cov-report=term-missing',
        '--cov-report=html',
    ])
    
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED - See details above")
    print("=" * 70)
    print()
    print("📊 Coverage report generated in: htmlcov/index.html")
    print()
    
    return result.returncode


if __name__ == '__main__':
    sys.exit(run_tests())


"""
================================================================================
SETUP INSTRUCTIONS
================================================================================

1. Install pytest and coverage:
   pip install pytest pytest-cov

2. Create test directory structure:
   mkdir tests
   mkdir tests/test_services
   mkdir tests/test_repositories
   mkdir tests/test_models

3. Add __init__.py files:
   touch tests/__init__.py
   touch tests/test_services/__init__.py
   touch tests/test_repositories/__init__.py
   touch tests/test_models/__init__.py

4. Copy the test files from artifacts:
   - conftest.py → tests/conftest.py
   - test_transaction_service.py → tests/test_services/
   - test_debt_payoff_model.py → tests/test_services/

5. Run tests:
   python run_tests.py

   OR run specific tests:
   pytest tests/test_services/test_transaction_service.py -v
   pytest tests/test_services/test_debt_payoff_model.py -v

6. Run with coverage:
   pytest tests/ --cov=data --cov-report=html

7. View coverage report:
   Open htmlcov/index.html in your browser

================================================================================
WHAT THE TESTS WILL FIND
================================================================================

The tests I created will catch these types of bugs:

1. ✅ Balance Calculation Bugs:
   - Credit vs Debit account logic errors
   - Wrong sign handling for expenses/income
   - Transfer calculation errors
   - Debt payment application bugs

2. ✅ Debt Payoff Calculation Bugs:
   - Amortization formula errors
   - Interest calculation mistakes
   - Edge cases (zero balance, overpayment, etc.)
   - Payment < interest scenarios

3. ✅ Data Aggregation Bugs:
   - Missing debts in summary
   - Wrong total calculations
   - Zero-balance handling

4. ✅ Transaction Reversal Bugs:
   - Incorrect reversal logic
   - Balance not returning to original state

================================================================================
EXPECTED OUTPUT
================================================================================

When you run the tests, you'll see something like:

tests/test_services/test_transaction_service.py::TestTransactionService::test_debit_account_expense_decreases_balance PASSED
tests/test_services/test_transaction_service.py::TestTransactionService::test_credit_account_expense_increases_balance FAILED

FAILED tests indicate BUGS in your code that need to be fixed!

================================================================================
NEXT STEPS AFTER RUNNING TESTS
================================================================================

1. Run the tests and see which ones fail
2. Upload the test output showing failures
3. I'll help you fix the bugs that the tests revealed
4. Re-run tests to verify fixes
5. Repeat until all tests pass ✅

================================================================================
"""