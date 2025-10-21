"""
Category Repository - Handles category data persistence
Single Responsibility: File I/O for categories only
UPDATED: Now includes validation before save
"""
import json
import uuid
from pathlib import Path


class CategoryRepository:
    """Repository: Manages category data persistence with validation"""
    
    def __init__(self, data_dir, validation_service=None):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "categories.json"
        self.validation_service = validation_service
    
    def get_all(self):
        """
        Load all categories from file
        Returns list of category dicts
        """
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                categories = json.load(f)
                # Ensure default categories exist with types
                return self._ensure_default_categories(categories)
        else:
            # Return defaults
            return self._get_default_categories()
    
    def save_all(self, categories):
        """
        Save all categories to file
        """
        with open(self.file_path, 'w') as f:
            json.dump(categories, f, indent=2)
    
    def get_by_id(self, category_id):
        """Get a category by ID"""
        categories = self.get_all()
        for category in categories:
            if category.get('id') == category_id:
                return category
        return None
    
    def get_by_name(self, name):
        """Get a category by name"""
        categories = self.get_all()
        for category in categories:
            if category.get('name') == name:
                return category
        return None
    
    def add(self, category):
        """Add a new category"""
        categories = self.get_all()
        
        # Ensure ID exists
        if 'id' not in category:
            category['id'] = f"cat-{str(uuid.uuid4())[:8]}"
        
        # Ensure type exists (default to expense)
        if 'type' not in category:
            category['type'] = 'expense'
        
        categories.append(category)
        self.save_all(categories)
        return category
    
    def update(self, old_category, new_category):
        """Update an existing category"""
        categories = self.get_all()
        
        for i, cat in enumerate(categories):
            if cat == old_category:
                # Preserve ID and special flag
                new_category['id'] = old_category.get('id')
                new_category['special'] = old_category.get('special', False)
                new_category['type'] = old_category.get('type', 'expense')  # Preserve type
                categories[i] = new_category
                self.save_all(categories)
                return True
        return False
    
    def delete(self, category):
        """Delete a category"""
        categories = self.get_all()
        categories.remove(category)
        self.save_all(categories)
    
    def _get_default_categories(self):
        """Get default categories with types"""
        return [
            {
                "id": f"cat-{str(uuid.uuid4())[:8]}", 
                "name": "General Income", 
                "color": "#27AE60", 
                "type": "income",
                "special": True,
                "budget": 0.0
            },
            {
                "id": f"cat-{str(uuid.uuid4())[:8]}", 
                "name": "General Expense", 
                "color": "#E74C3C", 
                "type": "expense",
                "special": True,
                "budget": 0.0
            },
            {
                "id": f"cat-{str(uuid.uuid4())[:8]}", 
                "name": "General Savings", 
                "color": "#3498DB", 
                "type": "savings",
                "special": True,
                "budget": 0.0
            },
            {
                "id": f"cat-{str(uuid.uuid4())[:8]}", 
                "name": "Transfer", 
                "color": "#95A5A6", 
                "type": "special",
                "special": True,
                "budget": 0.0
            },
            {
                "id": f"cat-{str(uuid.uuid4())[:8]}", 
                "name": "Debt Payment", 
                "color": "#E67E22", 
                "type": "special",
                "special": True,
                "budget": 0.0
            }
        ]
    
    def _ensure_default_categories(self, categories):
        """Ensure default categories exist in the list"""
        default_categories = {
            "General Income": {"color": "#27AE60", "type": "income", "special": True, "budget": 0.0},
            "General Expense": {"color": "#E74C3C", "type": "expense", "special": True, "budget": 0.0},
            "General Savings": {"color": "#3498DB", "type": "savings", "special": True, "budget": 0.0},
            "Transfer": {"color": "#95A5A6", "type": "special", "special": True, "budget": 0.0},
            "Debt Payment": {"color": "#E67E22", "type": "special", "special": True, "budget": 0.0}
        }
        
        existing_names = [cat['name'] for cat in categories]
        
        # Add missing defaults at the beginning
        for name, props in default_categories.items():
            if name not in existing_names:
                categories.insert(0, {
                    "id": f"cat-{str(uuid.uuid4())[:8]}",
                    "name": name,
                    **props
                })
        
        # Ensure all existing categories have correct type field
        for cat in categories:
            if cat['name'] in default_categories:
                # Update default category to have correct type
                cat['type'] = default_categories[cat['name']]['type']
                cat['special'] = True
            elif 'type' not in cat:
                # Legacy custom categories default to expense
                cat['type'] = 'expense'
        
        return categories