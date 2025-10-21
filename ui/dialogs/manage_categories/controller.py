"""
Manage Categories Dialog - Controller
Coordinates between Model and View (Updated for card-based view)
"""
from PySide6.QtCore import Qt
from .model import CategoryManagementModel
from .view import CategoryManagementView


class CategoryManagementController:
    """Controller: Orchestrates category management operations"""
    
    def __init__(self, data_manager, parent=None):
        self.model = CategoryManagementModel(data_manager)
        self.view = CategoryManagementView(parent)
        
        self.connect_signals()
        self.load_categories()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        # Button clicks
        self.view.add_button.clicked.connect(self.on_add_clicked)
        self.view.update_button.clicked.connect(self.on_update_clicked)
        self.view.clear_button.clicked.connect(self.view.clear_form)
        
        # Color picker
        self.view.color_button.clicked.connect(self.view.open_color_picker)
        
        # Card signals
        self.view.edit_requested.connect(self.on_edit_requested)
        self.view.delete_requested.connect(self.on_delete_requested)
    
    def load_categories(self):
        """Load and display all categories"""
        categories = self.model.get_all_categories()
        self.view.populate_categories(categories)
    
    def on_add_clicked(self):
        """Handle add button click"""
        # Get form data
        data = self.view.get_form_data()
        
        # Validate budget
        valid, budget_value, error_msg = self.model.validate_budget(data['budget'])
        if not valid:
            self.view.show_error(error_msg)
            return
        
        # Add category
        success, message = self.model.add_category(
            data['name'],
            data['color'],
            budget_value,
            data['type']
        )
        
        if success:
            self.view.show_success(message)
            self.load_categories()
            self.view.clear_form()
        else:
            self.view.show_error(message)
    
    def on_edit_requested(self, category):
        """Handle edit request from card"""
        # Check if special category
        if category.get('special', False):
            self.view.show_error("Special categories cannot be edited")
            return
        
        # Populate form with category data
        self.view.set_form_data(category)
    
    def on_update_clicked(self):
        """Handle update button click"""
        # Get current category being edited
        if not self.view.current_category:
            self.view.show_error("No category selected")
            return
        
        old_name = self.view.current_category['name']
        
        # Get form data
        data = self.view.get_form_data()
        
        # Validate budget
        valid, budget_value, error_msg = self.model.validate_budget(data['budget'])
        if not valid:
            self.view.show_error(error_msg)
            return
        
        # Update category
        success, message = self.model.update_category(
            old_name,
            data['name'],
            data['color'],
            budget_value
        )
        
        if success:
            self.view.show_success(message)
            self.load_categories()
            self.view.clear_form()
        else:
            self.view.show_error(message)
    
    def on_delete_requested(self, category):
        """Handle delete request from card"""
        category_name = category['name']
        
        # Confirm deletion
        if not self.view.confirm_delete(category_name):
            return
        
        # Delete category
        success, message = self.model.delete_category(category_name)
        
        if success:
            self.view.show_success(message)
            self.load_categories()
            self.view.clear_form()
        else:
            self.view.show_error(message)
    
    def exec(self):
        """Show dialog and return result"""
        return self.view.exec()
    
    def set_dark_mode(self, enabled):
        """Pass theme change to view"""
        self.view.set_dark_mode(enabled)