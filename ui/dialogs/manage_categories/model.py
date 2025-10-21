"""
Manage Categories Dialog - Model
Handles all category data operations and business logic
"""


class CategoryManagementModel:
    """Model: Category CRUD operations and validation"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_all_categories(self):
        """Get all categories from data manager"""
        # FIXED: Use the categories list that's already loaded in memory
        return self.data_manager.categories
    
    def get_category_by_name(self, name):
        """Find a category by name"""
        for category in self.get_all_categories():
            if category['name'] == name:
                return category
        return None
    
    def get_category_by_id(self, category_id):
        """Find a category by ID"""
        return self.data_manager.get_category_by_id(category_id)
    
    def add_category(self, name, color, budget=0.0, cat_type='expense'):
        """
        Add a new category
        Returns: (success: bool, message: str)
        """
        # Validation
        if not name or not name.strip():
            return False, "Category name cannot be empty"
        
        # Check for duplicates
        if self.get_category_by_name(name):
            return False, f"Category '{name}' already exists"
        
        # Add category using data manager's method
        new_category = {
            'name': name.strip(),
            'color': color,
            'budget': float(budget) if budget else 0.0,
            'type': cat_type
        }
        
        # Use category_repo to add
        self.data_manager.category_repo.add(new_category)
        
        # Refresh in-memory categories
        self.data_manager.categories = self.data_manager.category_repo.get_all()
        
        return True, "Category added successfully"
    
    def update_category(self, old_name, new_name, color, budget=0.0):
        """
        Update an existing category
        Returns: (success: bool, message: str)
        """
        # Validation
        if not new_name or not new_name.strip():
            return False, "Category name cannot be empty"
        
        # Check if trying to rename a special category
        old_category = self.get_category_by_name(old_name)
        if old_category and old_category.get('special', False):
            return False, "Cannot rename special categories"
        
        # Check for duplicate name (if name changed)
        if old_name != new_name:
            if self.get_category_by_name(new_name):
                return False, f"Category '{new_name}' already exists"
        
        # Update category
        new_category = {
            'name': new_name.strip(),
            'color': color,
            'budget': float(budget) if budget else 0.0
        }
        
        success = self.data_manager.update_category(old_category, new_category)
        
        if success:
            return True, "Category updated successfully"
        else:
            return False, "Category not found"
    
    def delete_category(self, name):
        """
        Delete a category
        Returns: (success: bool, message: str)
        """
        # Check if special category
        category = self.get_category_by_name(name)
        if category and category.get('special', False):
            return False, "Cannot delete special categories (Income, Debt Payment, Transfer)"
        
        if not category:
            return False, "Category not found"
        
        # Delete using data manager's method (soft delete)
        self.data_manager.delete_category(category)
        
        return True, "Category deleted successfully"
    
    def is_special_category(self, name):
        """Check if a category is special (can't be deleted/renamed)"""
        category = self.get_category_by_name(name)
        return category.get('special', False) if category else False
    
    def validate_budget(self, budget_str):
        """
        Validate budget input
        Returns: (valid: bool, value: float, message: str)
        """
        if not budget_str or budget_str.strip() == '':
            return True, 0.0, ""
        
        try:
            budget = float(budget_str)
            if budget < 0:
                return False, 0.0, "Budget cannot be negative"
            return True, budget, ""
        except ValueError:
            return False, 0.0, "Invalid budget amount"