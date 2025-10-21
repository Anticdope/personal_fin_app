"""
Dashboard View - Pure UI for dashboard display
Clean version with carousel-style navigation
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QStackedWidget, QFrame)
from PySide6.QtCore import Qt, Signal


class DashboardView(QWidget):
    """View: Pure UI for dashboard with carousel navigation"""
    
    # Signals
    manage_categories_clicked = Signal()
    manage_accounts_clicked = Signal()
    dark_mode_toggled = Signal()
    prev_top_clicked = Signal()
    next_top_clicked = Signal()
    prev_bottom_clicked = Signal()
    next_bottom_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        self.setMinimumWidth(450)
        self.setMaximumWidth(600)
        self.setObjectName("dashboardWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Main header with dark mode toggle
        main_header = QHBoxLayout()
        
        title = QLabel("Dashboard")
        title.setObjectName("dashboardTitle")
        
        self.dark_mode_toggle = QPushButton("🌙")
        self.dark_mode_toggle.setFixedSize(70, 70)
        self.dark_mode_toggle.setObjectName("darkModeToggle")
        self.dark_mode_toggle.setToolTip("Toggle Dark Mode")
        self.dark_mode_toggle.clicked.connect(self.dark_mode_toggled.emit)
        
        main_header.addWidget(title)
        main_header.addStretch()
        main_header.addWidget(self.dark_mode_toggle)
        layout.addLayout(main_header)
        
        # TOP PANE SECTION
        top_section = self._create_pane_section("top")
        layout.addWidget(top_section)
        
        # Manage buttons
        manage_layout = QHBoxLayout()
        manage_layout.setSpacing(10)
        
        manage_cat_btn = QPushButton("Manage Categories")
        manage_cat_btn.setObjectName("primaryButton")
        manage_cat_btn.clicked.connect(self.manage_categories_clicked.emit)
        
        manage_acc_btn = QPushButton("Manage Accounts")
        manage_acc_btn.setObjectName("primaryButton")
        manage_acc_btn.clicked.connect(self.manage_accounts_clicked.emit)
        
        manage_layout.addWidget(manage_cat_btn)
        manage_layout.addWidget(manage_acc_btn)
        layout.addLayout(manage_layout)
        
        # BOTTOM PANE SECTION
        bottom_section = self._create_pane_section("bottom")
        layout.addWidget(bottom_section, 1)
    
    def _create_pane_section(self, section_type):
        """Create a pane section with carousel-style navigation"""
        section = QFrame()
        section.setObjectName("paneSection")
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(10)
        
        # Carousel navigation header: [◀] Pane Name [▶]
        header = QHBoxLayout()
        
        # Previous button
        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(50, 50)
        prev_btn.setObjectName("navButton")
        
        # Pane name label (centered)
        if section_type == "top":
            self.top_pane_label = QLabel("Pane")
            self.top_pane_label.setObjectName("paneLabel")
            self.top_pane_label.setAlignment(Qt.AlignCenter)
            label = self.top_pane_label
        else:
            self.bottom_pane_label = QLabel("Pane")
            self.bottom_pane_label.setObjectName("paneLabel")
            self.bottom_pane_label.setAlignment(Qt.AlignCenter)
            label = self.bottom_pane_label
        
        # Next button
        next_btn = QPushButton("▶")
        next_btn.setFixedSize(50, 50)
        next_btn.setObjectName("navButton")
        
        # Connect signals
        if section_type == "top":
            prev_btn.clicked.connect(self.prev_top_clicked.emit)
            next_btn.clicked.connect(self.next_top_clicked.emit)
        else:
            prev_btn.clicked.connect(self.prev_bottom_clicked.emit)
            next_btn.clicked.connect(self.next_bottom_clicked.emit)
        
        header.addWidget(prev_btn)
        header.addWidget(label, 1)  # stretch=1 to center the label
        header.addWidget(next_btn)
        section_layout.addLayout(header)
        
        # Stacked widget for panes
        stacked = QStackedWidget()
        
        if section_type == "top":
            self.top_stacked = stacked
        else:
            self.bottom_stacked = stacked
        
        section_layout.addWidget(stacked)
        
        return section
    
    def add_top_pane(self, pane):
        """Add a pane to the top section"""
        self.top_stacked.addWidget(pane)
    
    def add_bottom_pane(self, pane):
        """Add a pane to the bottom section"""
        self.bottom_stacked.addWidget(pane)
    
    def set_top_pane_index(self, index):
        """Switch to a specific top pane"""
        self.top_stacked.setCurrentIndex(index)
    
    def set_bottom_pane_index(self, index):
        """Switch to a specific bottom pane"""
        self.bottom_stacked.setCurrentIndex(index)
    
    def update_top_pane_label(self, name):
        """Update the top pane label"""
        self.top_pane_label.setText(name)
    
    def update_bottom_pane_label(self, name):
        """Update the bottom pane label"""
        self.bottom_pane_label.setText(name)
    
    def update_dark_mode_button(self, dark_mode):
        """Update dark mode button text"""
        self.dark_mode_toggle.setText("☀️" if dark_mode else "🌙")
    
    def set_dark_mode(self, dark_mode):
        """Update theme"""
        self.dark_mode = dark_mode