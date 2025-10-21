"""
Day Pane - Calendar day display widget
Clean version with no inline styles - all styling via QSS
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


class DayPane(QWidget):
    """Widget representing a single day in the calendar"""
    
    def __init__(self, day_number, totals, dark_mode=False, is_today=False):
        super().__init__()
        self.day_number = day_number
        self.totals = totals
        self.dark_mode = dark_mode
        self.is_today = is_today
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        # Main frame
        self.frame = QFrame()
        
        # Set object names for styling
        if self.is_today:
            self.frame.setObjectName("todayFrame")
        else:
            self.frame.setObjectName("dayFrame")
        
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Day number
        day_label = QLabel(str(self.day_number))
        day_label.setObjectName("dayNumber")
        day_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(day_label)
        
        layout.addStretch()
        
        # Pending total (if any)
        if self.totals['pending'] != 0:
            pending_label = QLabel(f"${abs(self.totals['pending']):.2f}")
            pending_label.setObjectName("pendingAmount")
            pending_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(pending_label)
        
        # Posted total (if any)
        if self.totals['posted'] != 0:
            posted_label = QLabel(f"${abs(self.totals['posted']):.2f}")
            if self.totals['posted'] >= 0:
                posted_label.setObjectName("positiveAmount")
            else:
                posted_label.setObjectName("negativeAmount")
            posted_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(posted_label)
        
        # Add frame to widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
    
    def set_dark_mode(self, dark_mode):
        """Update theme for this day pane"""
        self.dark_mode = dark_mode
        # Theme is applied via QSS, no need to manually update styles