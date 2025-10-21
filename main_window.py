"""
Main Window - Updated to use MVC dialog controllers
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

from data_manager import DataManager
from ui.calendar.controller import CalendarController
from ui.dashboard.controller import DashboardController

# NEW: Import MVC dialog controllers instead of old dialogs
from ui.dialogs.manage_categories import CategoryManagementController
from ui.dialogs.manage_accounts import AccountManagementController
from ui.dialogs.restore import RestoreController


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.data_manager = DataManager()
        self.dark_mode = False
        
        # Auto-post due transactions on startup
        self.data_manager.auto_post_due_transactions()
        
        # Create controllers
        self.calendar_controller = CalendarController(self.data_manager, self)
        self.dashboard_controller = DashboardController(self.data_manager, self)
        
        self.setup_ui()
        self.connect_signals()
        self.initialize_display()
    
    def setup_ui(self):
        """Setup the UI structure"""
        self.setWindowTitle("Budget Tracker")
        self.setMinimumSize(1920, 1278)
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        restore_action = file_menu.addAction("Restore Deleted Items")
        restore_action.triggered.connect(self.open_restore_dialog)
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        edit_theme_action = view_menu.addAction("Edit Theme")
        edit_theme_action.triggered.connect(self.open_theme_editor)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add calendar widget
        calendar_widget = self.calendar_controller.get_widget()
        main_layout.addWidget(calendar_widget, stretch=3)
        
        # Add collapse button
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setObjectName("collapseButton")
        self.collapse_btn.setMaximumWidth(30)
        self.collapse_btn.clicked.connect(self.toggle_dashboard)
        main_layout.addWidget(self.collapse_btn)
        
        # Add dashboard widget
        dashboard_widget = self.dashboard_controller.get_widget()
        main_layout.addWidget(dashboard_widget, stretch=1)
    
    def connect_signals(self):
        """Connect signals between components"""
        # Calendar signals
        self.calendar_controller.day_clicked.connect(self.open_day_transactions)
        self.calendar_controller.month_changed.connect(self.on_month_changed)
        
        # Dashboard signals
        self.dashboard_controller.manage_categories_clicked.connect(self.manage_categories)
        self.dashboard_controller.manage_accounts_clicked.connect(self.manage_accounts)
        self.dashboard_controller.dark_mode_toggled.connect(self.toggle_dark_mode)
    
    def initialize_display(self):
        """Initialize the display with current month data"""
        # Load dashboard panes
        self.dashboard_controller.load_panes()
        
        # Update dashboard with current month
        current_date = self.calendar_controller.get_current_date()
        self.dashboard_controller.update_dashboard(current_date.year(), current_date.month())
    
    def open_day_transactions(self, date):
        """Open transaction dialog for a specific day"""
        # NEW: Use MVC controller
        from ui.dialogs.transaction import TransactionController
        
        controller = TransactionController(date, self.data_manager, self)
        controller.set_dark_mode(self.dark_mode)
        controller.exec()
        
        # Refresh after dialog closes
        self.refresh_all()
    
    def manage_categories(self):
        """Open category management dialog"""
        # NEW: Use MVC controller instead of dialog directly
        controller = CategoryManagementController(self.data_manager, self)
        controller.set_dark_mode(self.dark_mode)
        controller.exec()
        
        # Refresh after dialog closes
        self.refresh_all()
    
    def manage_accounts(self):
        """Open account management dialog"""
        # NEW: Use MVC controller instead of dialog directly
        controller = AccountManagementController(self.data_manager, self)
        controller.set_dark_mode(self.dark_mode)
        controller.exec()
        
        # Refresh after dialog closes
        self.refresh_all()
    
    def open_restore_dialog(self):
        """Open the restore deleted items dialog"""
        # NEW: Use MVC controller instead of dialog directly
        controller = RestoreController(self.data_manager, self)
        controller.set_dark_mode(self.dark_mode)
        restored = controller.exec()
        
        # Refresh if restore was successful
        if restored:
            # Force reload data from files
            self.data_manager.categories = self.data_manager.category_repo.get_all()
            self.data_manager.accounts = self.data_manager.account_repo.get_all()
            self.data_manager.assets = self.data_manager.asset_repo.get_all()
            self.data_manager.liabilities = self.data_manager.liability_repo.get_all()
            
            self.refresh_all()
    
    def open_theme_editor(self):
        """Open the theme editor dialog"""
        from ui.dialogs.theme_editor.controller import ThemeEditorController
        controller = ThemeEditorController(self.theme_manager, self)
        controller.exec()
    
    def on_month_changed(self):
        """Handle month change from calendar"""
        current_date = self.calendar_controller.get_current_date()
        self.dashboard_controller.update_dashboard(current_date.year(), current_date.month())
    
    def toggle_dashboard(self):
        """Toggle dashboard visibility"""
        dashboard_widget = self.dashboard_controller.get_widget()
        if dashboard_widget.isVisible():
            dashboard_widget.hide()
            self.collapse_btn.setText("▶")
        else:
            dashboard_widget.show()
            self.collapse_btn.setText("◀")
    
    def toggle_dark_mode(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        theme_name = "dark" if self.dark_mode else "light"
        self.theme_manager.load_theme(theme_name)
        
        # Update all components
        self.calendar_controller.set_dark_mode(self.dark_mode)
        self.dashboard_controller.set_dark_mode(self.dark_mode)
    
    def refresh_all(self):
        """Refresh all components"""
        current_date = self.calendar_controller.get_current_date()
        self.calendar_controller.load_calendar()  # Fixed: was update_calendar()
        self.dashboard_controller.update_dashboard(current_date.year(), current_date.month())