"""
Migration Service - Handles data migrations
Single Responsibility: Migrate data between schema versions
"""
import json
import uuid
from datetime import datetime
from pathlib import Path


# Increment this list as new migrations are added.
# Each entry is a (version_key, method_name) pair run in order.
MIGRATIONS = [
    ("balance_recalc_v1", "_migrate_balance_recalculation"),
]


class MigrationService:
    """Service: Handles data migrations"""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.config_file = self.data_dir / "config.json"
        self._state_file = self.data_dir / "migration_state.json"

        # Repos are injected by run_all_migrations() for versioned migrations
        self._account_repo = None
        self._liability_repo = None
        self._transaction_repo = None

    # =========================================================================
    # PUBLIC ENTRY POINT
    # =========================================================================

    def run_all_migrations(self, account_repo=None, liability_repo=None,
                           transaction_repo=None):
        """
        Run every pending migration in order.
        Call this once from DataManager.__init__() instead of check_and_migrate().

        Repos are optional — only needed for versioned migrations that touch
        account/liability/transaction data.
        """
        self._account_repo = account_repo
        self._liability_repo = liability_repo
        self._transaction_repo = transaction_repo

        # 1. Legacy: config.json → multi-file structure
        self.check_and_migrate()

        # 2. Versioned migrations (idempotent via state file)
        completed = self._get_completed_migrations()
        for version_key, method_name in MIGRATIONS:
            if version_key not in completed:
                print(f"🔄 Running migration: {version_key} ...")
                try:
                    getattr(self, method_name)()
                    self._mark_complete(version_key)
                    print(f"✅ Migration complete: {version_key}")
                except Exception as e:
                    print(f"❌ Migration failed ({version_key}): {e}")
                    raise

    # =========================================================================
    # VERSIONED MIGRATION STATE
    # =========================================================================

    def _get_completed_migrations(self):
        """Return the set of already-completed migration version keys."""
        if not self._state_file.exists():
            return set()
        with open(self._state_file, 'r') as f:
            state = json.load(f)
        return set(state.get("completed", []))

    def _mark_complete(self, version_key):
        """Persist a migration version key as completed."""
        state = {}
        if self._state_file.exists():
            with open(self._state_file, 'r') as f:
                state = json.load(f)
        state.setdefault("completed", []).append(version_key)
        state["last_run"] = datetime.now().isoformat()
        with open(self._state_file, 'w') as f:
            json.dump(state, f, indent=2)

    # =========================================================================
    # VERSIONED MIGRATIONS
    # =========================================================================

    def _migrate_balance_recalculation(self):
        """
        Recalculate all account and liability balances from scratch.

        Fixes balances corrupted by two bugs that have since been fixed:
          1. Pending (future) recurring transactions were immediately applied
             to account balances instead of waiting until their due date.
          2. Transfers were counted as income in the YTD summary (UI display
             bug — did not affect balances, but confirms data integrity check
             is worthwhile).

        Strategy
        --------
        For each account/liability:
          - Reset balance to `starting_balance` (preserved from account creation).
          - If `starting_balance` doesn't exist yet (older accounts), fall back to
            `original_balance` (credit accounts) or 0.0 (debit accounts).
          - Add `starting_balance` as a permanent field going forward.
        Then replay every POSTED transaction file in chronological order,
        applying the correct delta for regular, transfer, and debt-payment types.
        Pending transactions are intentionally skipped.
        """
        if not self._account_repo or not self._liability_repo:
            raise RuntimeError(
                "balance_recalculation migration requires account_repo and "
                "liability_repo — pass them to run_all_migrations()."
            )

        accounts    = self._account_repo.get_all()
        liabilities = self._liability_repo.get_all()

        # Build lookup maps (name → dict, mutated in-place then saved)
        acct_map   = {a['name']: a for a in accounts}
        liab_map   = {l['name']: l for l in liabilities}
        acct_id_map = {a['id']: a for a in accounts if 'id' in a}

        # ── Seed starting balances ────────────────────────────────────────────
        for acct in accounts:
            if 'starting_balance' not in acct:
                if acct.get('type', 'debit').lower() == 'credit':
                    acct['starting_balance'] = acct.get('original_balance', 0.0)
                else:
                    acct['starting_balance'] = 0.0
            acct['balance'] = acct['starting_balance']

        for liab in liabilities:
            if 'starting_balance' not in liab:
                liab['starting_balance'] = liab.get('original_balance',
                                                     liab.get('balance', 0.0))
            liab['balance'] = liab['starting_balance']

        # ── Walk all monthly transaction files in date order ──────────────────
        skip = {
            'categories.json', 'accounts.json', 'assets.json',
            'liabilities.json', 'recurring_transactions.json',
            'deleted_items.json', 'card_order.json',
            'migration_state.json', 'config.json',
        }
        month_files = sorted(
            f for f in self.data_dir.glob("????-??.json")
            if f.name not in skip
        )

        for month_file in month_files:
            try:
                with open(month_file, 'r') as f:
                    month_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                print(f"  ⚠️  Skipping unreadable file: {month_file.name}")
                continue

            for day_key in sorted(month_data.keys(), key=lambda d: int(d)):
                for transaction in month_data[day_key]:
                    if not isinstance(transaction, dict):
                        continue
                    if transaction.get('status') == 'pending':
                        continue  # Applied only when posted

                    category = transaction.get('category', '')

                    # Regular income / expense
                    if category not in ('Transfer', 'Debt Payment'):
                        acct = acct_map.get(transaction.get('account'))
                        if not acct and 'account_id' in transaction:
                            acct = acct_id_map.get(transaction['account_id'])
                        if not acct:
                            continue
                        amount = float(transaction.get('amount', 0))
                        if acct.get('type', 'debit').lower() == 'debit':
                            acct['balance'] += amount
                        else:
                            acct['balance'] -= amount

                    # Transfer
                    elif category == 'Transfer':
                        amount = abs(float(transaction.get('amount', 0)))
                        source = acct_map.get(transaction.get('source_account'))
                        target = acct_map.get(transaction.get('target_account'))
                        if source:
                            source['balance'] -= amount
                        if target:
                            target['balance'] += amount

                    # Debt Payment
                    elif category == 'Debt Payment':
                        amount = abs(float(transaction.get('amount', 0)))
                        source = acct_map.get(transaction.get('source_account'))
                        target_name = transaction.get('target_debt')
                        target_type = transaction.get('target_type', 'credit')
                        if source:
                            source['balance'] -= amount
                        if target_type == 'credit':
                            target = acct_map.get(target_name)
                            if target:
                                target['balance'] -= amount
                        else:
                            target = liab_map.get(target_name)
                            if target:
                                target['balance'] -= amount

        # ── Persist corrected balances ────────────────────────────────────────
        with open(self.data_dir / "accounts.json", 'w') as f:
            json.dump(accounts, f, indent=2)
        with open(self.data_dir / "liabilities.json", 'w') as f:
            json.dump(liabilities, f, indent=2)

        print(f"  ↳ Recalculated {len(accounts)} account(s) and "
              f"{len(liabilities)} liability balance(s)")

    # =========================================================================
    # LEGACY MIGRATION  (config.json → multi-file)
    # =========================================================================

    def check_and_migrate(self):
        """
        Check if old config.json exists and migrate if needed.
        Returns: True if migration was performed, False otherwise.
        """
        if not self.config_file.exists():
            return False

        print("🔄 Migrating from config.json to multi-file structure with UUIDs...")

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            mappings = self._create_id_mappings(config)

            self._migrate_categories(config, mappings)
            self._migrate_accounts(config, mappings)
            self._migrate_assets(config, mappings)
            self._migrate_liabilities(config, mappings)
            self._migrate_recurring(config, mappings)
            self._migrate_transaction_files(mappings)

            self.config_file.unlink()

            print("✅ Migration complete! Old config.json removed.")
            print("📁 New structure: categories.json, accounts.json, assets.json, liabilities.json")

            return True

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("⚠️ Old config.json preserved for safety")
            return False

    def _create_id_mappings(self, config):
        """Create name->id mappings for all data types"""
        mappings = {
            'categories': {},
            'accounts': {},
            'assets': {},
            'liabilities': {}
        }

        for cat in config.get('categories', []):
            if 'id' not in cat:
                cat['id'] = f"cat-{str(uuid.uuid4())[:8]}"
            mappings['categories'][cat['name']] = cat['id']

        for acc in config.get('accounts', []):
            if 'id' not in acc:
                acc['id'] = f"acc-{str(uuid.uuid4())[:8]}"
            mappings['accounts'][acc['name']] = acc['id']

        for ast in config.get('assets', []):
            if 'id' not in ast:
                ast['id'] = f"ast-{str(uuid.uuid4())[:8]}"
            mappings['assets'][ast['name']] = ast['id']

        for lib in config.get('liabilities', []):
            if 'id' not in lib:
                lib['id'] = f"lib-{str(uuid.uuid4())[:8]}"
            mappings['liabilities'][lib['name']] = lib['id']

        return mappings

    def _migrate_categories(self, config, mappings):
        categories = config.get('categories', [])
        with open(self.data_dir / "categories.json", 'w') as f:
            json.dump(categories, f, indent=2)

    def _migrate_accounts(self, config, mappings):
        accounts = config.get('accounts', [])
        with open(self.data_dir / "accounts.json", 'w') as f:
            json.dump(accounts, f, indent=2)

    def _migrate_assets(self, config, mappings):
        assets = config.get('assets', [])
        with open(self.data_dir / "assets.json", 'w') as f:
            json.dump(assets, f, indent=2)

    def _migrate_liabilities(self, config, mappings):
        liabilities = config.get('liabilities', [])
        with open(self.data_dir / "liabilities.json", 'w') as f:
            json.dump(liabilities, f, indent=2)

    def _migrate_recurring(self, config, mappings):
        recurring = config.get('recurring_transactions', [])
        for rec in recurring:
            if 'account' in rec and 'account_id' not in rec:
                rec['account_id'] = mappings['accounts'].get(rec['account'])
            if 'category' in rec and 'category_id' not in rec:
                rec['category_id'] = mappings['categories'].get(rec['category'])
        with open(self.data_dir / "recurring_transactions.json", 'w') as f:
            json.dump(recurring, f, indent=2)

    def _migrate_transaction_files(self, mappings):
        print("🔄 Adding UUIDs to transaction files...")

        skip = {
            'config.json', 'categories.json', 'accounts.json',
            'assets.json', 'liabilities.json', 'recurring_transactions.json',
            'deleted_items.json'
        }
        month_files = [f for f in self.data_dir.glob("*.json") if f.name not in skip]

        for month_file in month_files:
            with open(month_file, 'r') as f:
                month_data = json.load(f)

            modified = False
            for day_key, transactions in month_data.items():
                for trans in transactions:
                    if 'category' in trans and 'category_id' not in trans:
                        trans['category_id'] = mappings['categories'].get(trans['category'])
                        modified = True
                    if 'account' in trans and 'account_id' not in trans:
                        account_name = trans['account']
                        if ' → ' in account_name:
                            parts = account_name.split(' → ')
                            trans['source_account_id'] = mappings['accounts'].get(parts[0].strip())
                            trans['target_account_id'] = mappings['accounts'].get(parts[1].strip())
                        else:
                            trans['account_id'] = mappings['accounts'].get(account_name)
                        modified = True

            if modified:
                with open(month_file, 'w') as f:
                    json.dump(month_data, f, indent=2)

        print(f"✅ Updated {len(month_files)} transaction file(s)")