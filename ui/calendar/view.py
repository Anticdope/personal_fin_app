"""
Calendar View - Pure UI for calendar display
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from ui.panes.day_pane import DayPane


class CalendarView(QWidget):
    """View: Pure UI for displaying calendar grid"""
    
    # Signals
    day_clicked = Signal(object)  # QDate
    prev_month_clicked = Signal()
    next_month_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.day_panes = {}  # Store day panes for updates
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header with month navigation
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(60, 60)
        self.prev_btn.setStyleSheet(self._get_nav_button_style())
        self.prev_btn.clicked.connect(self.prev_month_clicked.emit)
        
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        self._update_month_label_style()
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(60, 60)
        self.next_btn.setStyleSheet(self._get_nav_button_style())
        self.next_btn.clicked.connect(self.next_month_clicked.emit)
        
        header_layout.addWidget(self.prev_btn)
        header_layout.addWidget(self.month_label, 1)
        header_layout.addWidget(self.next_btn)
        
        layout.addWidget(header)
        
        # Calendar grid
        self.calendar_grid = QWidget()
        self.grid_layout = QGridLayout(self.calendar_grid)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.calendar_grid, 1)
    
    def display_month(self, month_data):
        """
        Display the calendar month
        month_data: dict with month_label, year, month, days
        """
        # Update month label
        self.month_label.setText(month_data['month_label'])
        
        # Clear existing grid
        self._clear_grid()
        
        # Add day headers
        self._add_day_headers()
        
        # Add day panes
        self.day_panes = {}
        for day_info in month_data['days']:
            day_pane = DayPane(
                day_info['day_number'],
                day_info['totals'],
                self.dark_mode,
                day_info['is_today']
            )
            
            # Connect click event
            date = day_info['date']
            day_pane.mousePressEvent = lambda event, d=date: self.day_clicked.emit(d)
            
            # Add to grid
            self.grid_layout.addWidget(day_pane, day_info['row'], day_info['col'])
            self.day_panes[day_info['day_number']] = day_pane
        
        # Make grid expand proportionally
        for i in range(7):
            self.grid_layout.setColumnStretch(i, 1)
        for i in range(1, 7):  # Skip header row
            self.grid_layout.setRowStretch(i, 1)
    
    def refresh_day_totals(self, day_totals_map):
        """
        Refresh day pane totals without rebuilding
        day_totals_map: dict {day_number: totals_dict}
        """
        for day_number, totals in day_totals_map.items():
            if day_number in self.day_panes:
                self.day_panes[day_number].update_totals(totals)
    
    def _clear_grid(self):
        """Remove all widgets from grid"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _add_day_headers(self):
        """Add day name headers to grid"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        header_color = "#B0B0B0" if self.dark_mode else "#34495E"
        
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                f"font-weight: bold; color: {header_color}; "
                f"font-size: 18px; padding: 10px;"
            )
            self.grid_layout.addWidget(label, 0, i)
    
    def _get_nav_button_style(self):
        """Get navigation button style"""
        return """
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 30px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """
    
    def _update_month_label_style(self):
        """Update month label styling based on theme"""
        month_color = "#FFFFFF" if self.dark_mode else "#2C3E50"
        self.month_label.setStyleSheet(
            f"font-size: 36px; font-weight: bold; color: {month_color};"
        )
    
    def set_dark_mode(self, dark_mode):
        """Update theme"""
        self.dark_mode = dark_mode
        self._update_month_label_style()
        
        # Update all day panes
        for day_pane in self.day_panes.values():
            day_pane.set_dark_mode(dark_mode)