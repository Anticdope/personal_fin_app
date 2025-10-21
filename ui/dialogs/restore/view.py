"""
Restore Dialog - View
Pure UI for restoring deleted items
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QMessageBox, QTabWidget, QWidget,
                               QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal
from datetime import datetime


class RestoreView(QDialog):
    """View: Pure UI for restoring deleted items"""
    
    # Signals for user actions
    restore_requested = Signal(str, int)  # item_type, index
    permanently_delete_requested = Signal(str, int)  # item_type, index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Restore Deleted Items")
        self.setModal(True)
        self.resize(800, 600)
        self.dark_mode = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Restore Deleted Items")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Tab widget for different item types
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.categories_tab = self.create_list_tab()
        self.accounts_tab = self.create_list_tab()
        self.transactions_tab = self.create_list_tab()
        self.assets_tab = self.create_list_tab()
        self.liabilities_tab = self.create_list_tab()
        
        self.tab_widget.addTab(self.categories_tab, "Categories")
        self.tab_widget.addTab(self.accounts_tab, "Accounts")
        self.tab_widget.addTab(self.transactions_tab, "Transactions")
        self.tab_widget.addTab(self.assets_tab, "Assets")
        self.tab_widget.addTab(self.liabilities_tab, "Liabilities")
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def create_list_tab(self):
        """Create a scrollable list widget for a tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def display_deleted_items(self, deleted_items):
        """Display all deleted items in their respective tabs"""
        self.display_categories(deleted_items.get('categories', []))
        self.display_accounts(deleted_items.get('accounts', []))
        self.display_transactions(deleted_items.get('transactions', []))
        self.display_assets(deleted_items.get('assets', []))
        self.display_liabilities(deleted_items.get('liabilities', []))
    
    def display_categories(self, categories):
        """Display deleted categories"""
        self._populate_tab(self.categories_tab, categories, 'category')
    
    def display_accounts(self, accounts):
        """Display deleted accounts"""
        self._populate_tab(self.accounts_tab, accounts, 'account')
    
    def display_transactions(self, transactions):
        """Display deleted transactions"""
        self._populate_tab(self.transactions_tab, transactions, 'transaction')
    
    def display_assets(self, assets):
        """Display deleted assets"""
        self._populate_tab(self.assets_tab, assets, 'asset')
    
    def display_liabilities(self, liabilities):
        """Display deleted liabilities"""
        self._populate_tab(self.liabilities_tab, liabilities, 'liability')
    
    def _populate_tab(self, tab_widget, items, item_type):
        """Populate a tab with deleted items"""
        # Get the scroll area's content widget
        scroll = tab_widget.findChild(QScrollArea)
        scroll_content = scroll.widget()
        layout = scroll_content.layout()
        
        # Clear existing items
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not items:
            no_items = QLabel(f"No deleted {item_type}s")
            no_items.setObjectName("mutedLabel")
            no_items.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_items)
            return
        
        # Add each deleted item
        for index, deleted_item in enumerate(items):
            item_widget = self._create_item_widget(deleted_item, item_type, index)
            layout.addWidget(item_widget)
    
    def _create_item_widget(self, deleted_item, item_type, index):
        """Create widget for a single deleted item"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        # Get item data
        item = deleted_item.get('item', {})
        deleted_at = deleted_item.get('deleted_at', '')
        
        # Header with item name
        header = QHBoxLayout()
        
        if item_type == 'transaction':
            name = item.get('title', 'Untitled')
            amount = item.get('amount', 0)
            name_label = QLabel(f"{name} (${amount:.2f})")
        else:
            name = item.get('name', 'Unknown')
            name_label = QLabel(name)
        
        name_label.setObjectName("subtitle")
        header.addWidget(name_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Details
        details = QHBoxLayout()
        
        # Format deletion date
        try:
            dt = datetime.fromisoformat(deleted_at)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = deleted_at
        
        deleted_label = QLabel(f"Deleted: {date_str}")
        deleted_label.setObjectName("mutedLabel")
        details.addWidget(deleted_label)
        
        # Show additional info based on type
        if item_type == 'transaction' and 'date' in deleted_item:
            date_info = deleted_item['date']
            trans_date = QLabel(f"Date: {date_info['year']}-{date_info['month']:02d}-{date_info['day']:02d}")
            trans_date.setObjectName("mutedLabel")
            details.addWidget(trans_date)
        
        details.addStretch()
        layout.addLayout(details)
        
        # Buttons
        buttons = QHBoxLayout()
        
        restore_btn = QPushButton("Restore")
        restore_btn.setObjectName("successButton")
        restore_btn.clicked.connect(
            lambda: self.restore_requested.emit(item_type, index)
        )
        
        delete_btn = QPushButton("Delete Permanently")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(
            lambda: self.permanently_delete_requested.emit(item_type, index)
        )
        
        buttons.addWidget(restore_btn)
        buttons.addWidget(delete_btn)
        buttons.addStretch()
        layout.addLayout(buttons)
        
        return frame
    
    def show_error(self, message):
        """Display error message"""
        QMessageBox.warning(self, "Error", message)
    
    def show_success(self, message):
        """Display success message"""
        QMessageBox.information(self, "Success", message)
    
    def confirm_permanent_delete(self, item_name):
        """Ask user to confirm permanent deletion"""
        reply = QMessageBox.warning(
            self,
            "Confirm Permanent Delete",
            f"Are you sure you want to permanently delete '{item_name}'?\n\n"
            f"This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def set_dark_mode(self, enabled):
        """Update theme"""
        self.dark_mode = enabled