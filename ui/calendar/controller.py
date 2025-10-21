"""
Calendar Controller - Coordinates Model and View
"""
from PySide6.QtCore import QObject, Signal
from .model import CalendarModel
from .view import CalendarView


class CalendarController(QObject):
    """
    Controller: Coordinates calendar model and view
    Handles navigation and day clicks
    """
    
    # Signals for communication with main window
    day_clicked = Signal(object)  # QDate
    month_changed = Signal()  # Emitted when month changes
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.model = CalendarModel(data_manager)
        self.view = CalendarView(parent)
        
        # Connect view signals to controller methods
        self.view.day_clicked.connect(self._on_day_clicked)
        self.view.prev_month_clicked.connect(self._on_prev_month)
        self.view.next_month_clicked.connect(self._on_next_month)
        
        # Load initial calendar
        self.load_calendar()
    
    def load_calendar(self):
        """Load and display the current month"""
        # Auto-post due transactions
        self.model.data_manager.auto_post_due_transactions()
        
        # Get month data from model
        month_data = self.model.get_current_month_data()
        
        # Update view
        self.view.display_month(month_data)
    
    def refresh_calendar(self):
        """Refresh calendar totals without rebuilding"""
        # Auto-post due transactions
        self.model.data_manager.auto_post_due_transactions()
        
        # For now, just reload everything
        # TODO: Optimize to only refresh totals
        self.load_calendar()
    
    def _on_day_clicked(self, date):
        """Handle day click from view"""
        self.day_clicked.emit(date)
    
    def _on_prev_month(self):
        """Handle previous month button"""
        self.model.navigate_to_previous_month()
        self.load_calendar()
        self.month_changed.emit()
    
    def _on_next_month(self):
        """Handle next month button"""
        self.model.navigate_to_next_month()
        self.load_calendar()
        self.month_changed.emit()
    
    def get_current_date(self):
        """Get current date from model"""
        return self.model.get_current_date()
    
    def set_dark_mode(self, dark_mode):
        """Pass theme change to view"""
        self.view.set_dark_mode(dark_mode)
    
    def get_widget(self):
        """Return the view widget for adding to layouts"""
        return self.view