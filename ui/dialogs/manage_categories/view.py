"""
Manage Categories Dialog - View (Enhanced with Card Layout)
Pure UI for category management
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLineEdit, QLabel, QMessageBox, QColorDialog,
                               QFrame, QScrollArea, QWidget, QComboBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class CategoryManagementView(QDialog):
    """View: Pure UI for managing categories with card layout"""
    
    # Signals for user actions
    add_requested = Signal()
    edit_requested = Signal(dict)
    delete_requested = Signal(dict)
    color_picker_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Categories")
        self.setModal(True)
        self.resize(800, 700)
        self.dark_mode = False
        self.selected_color = "#808080"
        self.current_category = None  # Track currently selected category for edit
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Manage Categories")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Add/Edit form
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        
        form_title = QLabel("Add/Edit Category")
        form_title.setObjectName("subtitle")
        form_layout.addWidget(form_title)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setObjectName("formLabel")
        self.name_input = QLineEdit()
        self.name_input.setObjectName("formInput")
        self.name_input.setPlaceholderText("Category name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        type_label.setObjectName("formLabel")
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("formCombo")
        self.type_combo.addItems(["Expense", "Income", "Savings"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        form_layout.addLayout(type_layout)
        
        # Color picker
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        color_label.setObjectName("formLabel")
        self.color_button = QPushButton("Choose Color")
        self.color_button.setObjectName("colorButton")
        self.color_preview = QLabel("●")
        self.color_preview.setObjectName("colorPreview")
        self.color_preview.setStyleSheet("font-size: 24px;")
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        form_layout.addLayout(color_layout)
        
        # Budget input
        budget_layout = QHBoxLayout()
        budget_label = QLabel("Budget:")
        budget_label.setObjectName("formLabel")
        self.budget_input = QLineEdit()
        self.budget_input.setObjectName("formInput")
        self.budget_input.setPlaceholderText("Optional monthly budget")
        budget_layout.addWidget(budget_label)
        budget_layout.addWidget(self.budget_input)
        form_layout.addLayout(budget_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Category")
        self.add_button.setObjectName("primaryButton")
        
        self.update_button = QPushButton("Update Category")
        self.update_button.setObjectName("successButton")
        self.update_button.setVisible(False)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("secondaryButton")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        form_layout.addLayout(button_layout)
        
        layout.addWidget(form_frame)
        
        # Categories list label
        list_label = QLabel("Your Categories:")
        list_label.setObjectName("sectionLabel")
        layout.addWidget(list_label)
        
        # Categories list (scrollable cards)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_container)
        self.categories_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.categories_container)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Default color
        self.update_color_preview(self.selected_color)
    
    def populate_categories(self, categories):
        """Display categories as cards (excluding default/special categories)"""
        # Clear existing
        while self.categories_layout.count():
            child = self.categories_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Filter out special/default categories
        custom_categories = [cat for cat in categories if not cat.get('special', False)]
        
        if not custom_categories:
            no_categories = QLabel("No custom categories yet. Default categories (General Income, General Expense, General Savings) are always available.")
            no_categories.setObjectName("mutedLabel")
            no_categories.setAlignment(Qt.AlignCenter)
            no_categories.setWordWrap(True)
            self.categories_layout.addWidget(no_categories)
            return
        
        for category in custom_categories:
            card = self.create_category_card(category)
            self.categories_layout.addWidget(card)
    
    def create_category_card(self, category):
        """Create a card widget for a category"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        # Header with color indicator and name
        header = QHBoxLayout()
        
        color_indicator = QLabel("●")
        color_indicator.setStyleSheet(f"color: {category['color']}; font-size: 60px;")
        
        name_label = QLabel(category['name'])
        name_label.setObjectName("subtitle")
        
        # Type badge
        cat_type = category.get('type', 'expense')
        type_badge = QLabel(f"({cat_type.capitalize()})")
        type_badge.setObjectName("mutedLabel")
        
        # Special category badge
        if category.get('special', False):
            special_badge = QLabel("[Default]")
            special_badge.setObjectName("mutedLabel")
            header.addWidget(color_indicator)
            header.addWidget(name_label)
            header.addWidget(type_badge)
            header.addWidget(special_badge)
        else:
            header.addWidget(color_indicator)
            header.addWidget(name_label)
            header.addWidget(type_badge)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Budget info
        budget = category.get('budget', 0)
        if budget > 0:
            budget_label = QLabel(f"Budget: ${budget:,.2f}/month")
            budget_label.setObjectName("mutedLabel")
            layout.addWidget(budget_label)
        
        # Buttons (only if not special)
        if not category.get('special', False):
            buttons = QHBoxLayout()
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, c=category: self.edit_requested.emit(c))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("dangerButton")
            delete_btn.clicked.connect(lambda checked, c=category: self.delete_requested.emit(c))
            
            buttons.addWidget(edit_btn)
            buttons.addWidget(delete_btn)
            buttons.addStretch()
            layout.addLayout(buttons)
        
        return frame
    
    def get_form_data(self):
        """Get current form values"""
        return {
            'name': self.name_input.text().strip(),
            'color': self.selected_color,
            'budget': self.budget_input.text().strip(),
            'type': self.type_combo.currentText().lower()
        }
    
    def set_form_data(self, category):
        """Populate form with category data"""
        self.current_category = category
        self.name_input.setText(category['name'])
        self.selected_color = category['color']
        self.update_color_preview(self.selected_color)
        self.budget_input.setText(str(category.get('budget', 0)) if category.get('budget') else "")
        
        # Set type
        cat_type = category.get('type', 'expense').capitalize()
        index = self.type_combo.findText(cat_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Disable type for special categories
        if category.get('special', False):
            self.type_combo.setEnabled(False)
        else:
            self.type_combo.setEnabled(True)
        
        # Switch to edit mode
        self.add_button.setVisible(False)
        self.update_button.setVisible(True)
    
    def clear_form(self):
        """Clear all form inputs"""
        self.current_category = None
        self.name_input.clear()
        self.budget_input.clear()
        self.selected_color = "#808080"
        self.update_color_preview(self.selected_color)
        self.type_combo.setCurrentIndex(0)  # Default to Expense
        self.type_combo.setEnabled(True)  # Re-enable
        
        # Switch to add mode
        self.add_button.setVisible(True)
        self.update_button.setVisible(False)
    
    def update_color_preview(self, color):
        """Update the color preview indicator"""
        self.color_preview.setStyleSheet(f"color: {color}; font-size: 24px;")
    
    def open_color_picker(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_preview(self.selected_color)
    
    def show_error(self, message):
        """Display error message"""
        QMessageBox.warning(self, "Error", message)
    
    def show_success(self, message):
        """Display success message"""
        QMessageBox.information(self, "Success", message)
    
    def confirm_delete(self, category_name):
        """Ask user to confirm deletion"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete category '{category_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def set_dark_mode(self, enabled):
        """Update theme"""
        self.dark_mode = enabled