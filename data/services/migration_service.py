"""
Migration Service - Handles data migrations
Single Responsibility: Migrate data between schema versions
"""
import json
import uuid
from pathlib import Path


class MigrationService:
    """Service: Handles data migrations"""
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.config_file = self.data_dir / "config.json"
    
    def check_and_migrate(self):
        """
        Check if old config.json exists and migrate if needed
        Returns: True if migration was performed, False otherwise
        """
        if not self.config_file.exists():
            return False
        
        print("🔄 Migrating from config.json to multi-file structure with UUIDs...")
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Create mappings
            mappings = self._create_id_mappings(config)
            
            # Migrate each data type
            self._migrate_categories(config, mappings)
            self._migrate_accounts(config, mappings)
            self._migrate_assets(config, mappings)
            self._migrate_liabilities(config, mappings)
            self._migrate_recurring(config, mappings)
            self._migrate_transaction_files(mappings)
            
            # Delete old config.json
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
        
        # Categories
        for cat in config.get('categories', []):
            if 'id' not in cat:
                cat['id'] = f"cat-{str(uuid.uuid4())[:8]}"
            mappings['categories'][cat['name']] = cat['id']
        
        # Accounts
        for acc in config.get('accounts', []):
            if 'id' not in acc:
                acc['id'] = f"acc-{str(uuid.uuid4())[:8]}"
            mappings['accounts'][acc['name']] = acc['id']
        
        # Assets
        for ast in config.get('assets', []):
            if 'id' not in ast:
                ast['id'] = f"ast-{str(uuid.uuid4())[:8]}"
            mappings['assets'][ast['name']] = ast['id']
        
        # Liabilities
        for lib in config.get('liabilities', []):
            if 'id' not in lib:
                lib['id'] = f"lib-{str(uuid.uuid4())[:8]}"
            mappings['liabilities'][lib['name']] = lib['id']
        
        return mappings
    
    def _migrate_categories(self, config, mappings):
        """Migrate categories to categories.json"""
        categories = config.get('categories', [])
        categories_file = self.data_dir / "categories.json"
        
        with open(categories_file, 'w') as f:
            json.dump(categories, f, indent=2)
    
    def _migrate_accounts(self, config, mappings):
        """Migrate accounts to accounts.json"""
        accounts = config.get('accounts', [])
        accounts_file = self.data_dir / "accounts.json"
        
        with open(accounts_file, 'w') as f:
            json.dump(accounts, f, indent=2)
    
    def _migrate_assets(self, config, mappings):
        """Migrate assets to assets.json"""
        assets = config.get('assets', [])
        assets_file = self.data_dir / "assets.json"
        
        with open(assets_file, 'w') as f:
            json.dump(assets, f, indent=2)
    
    def _migrate_liabilities(self, config, mappings):
        """Migrate liabilities to liabilities.json"""
        liabilities = config.get('liabilities', [])
        liabilities_file = self.data_dir / "liabilities.json"
        
        with open(liabilities_file, 'w') as f:
            json.dump(liabilities, f, indent=2)
    
    def _migrate_recurring(self, config, mappings):
        """Migrate recurring transactions to recurring_transactions.json"""
        recurring = config.get('recurring_transactions', [])
        recurring_file = self.data_dir / "recurring_transactions.json"
        
        # Update recurring with IDs
        for rec in recurring:
            if 'account' in rec and 'account_id' not in rec:
                rec['account_id'] = mappings['accounts'].get(rec['account'])
            if 'category' in rec and 'category_id' not in rec:
                rec['category_id'] = mappings['categories'].get(rec['category'])
        
        with open(recurring_file, 'w') as f:
            json.dump(recurring, f, indent=2)
    
    def _migrate_transaction_files(self, mappings):
        """Add UUIDs to all transaction files"""
        print("🔄 Adding UUIDs to transaction files...")
        
        month_files = list(self.data_dir.glob("*.json"))
        month_files = [f for f in month_files if f.name not in [
            'config.json', 'categories.json', 'accounts.json', 
            'assets.json', 'liabilities.json', 'recurring_transactions.json',
            'deleted_items.json'
        ]]
        
        for month_file in month_files:
            with open(month_file, 'r') as f:
                month_data = json.load(f)
            
            modified = False
            for day_key, transactions in month_data.items():
                for trans in transactions:
                    # Add category_id
                    if 'category' in trans and 'category_id' not in trans:
                        trans['category_id'] = mappings['categories'].get(trans['category'])
                        modified = True
                    
                    # Add account_id
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