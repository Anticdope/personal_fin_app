"""
Theme Editor Dialog - View
Allows users to select and preview different theme presets
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QTextEdit, QFrame,
                               QMessageBox, QScrollArea, QWidget)
from PySide6.QtCore import Qt, Signal


class ThemeEditorView(QDialog):
    """View: Theme editor dialog for selecting presets"""
    
    # Signals
    preset_changed = Signal(str)  # preset name
    apply_theme = Signal(str)  # preset name
    save_custom = Signal(str, str)  # name, qss content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Editor")
        self.setModal(True)
        self.resize(900, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Theme Editor")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Preset selector
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Select Preset:")
        preset_label.setObjectName("formLabel")
        
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("formCombo")
        self.preset_combo.addItems([
            "Light (Default)",
            "Dark (Default)",
            "Card Style - Light",
            "Card Style - Dark",
            "Panel Style - Light",
            "Panel Style - Dark",
            "Material Style - Light",
            "Material Style - Dark"
        ])
        self.preset_combo.currentTextChanged.connect(self.preset_changed.emit)
        
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
        
        # Preview section
        preview_label = QLabel("Preview:")
        preview_label.setObjectName("sectionLabel")
        layout.addWidget(preview_label)
        
        # Preview area with example widgets
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        
        self.preview_container = QWidget()
        preview_layout = QVBoxLayout(self.preview_container)
        
        # Example dashboard-like preview
        self._create_preview_widgets(preview_layout)
        
        preview_scroll.setWidget(self.preview_container)
        layout.addWidget(preview_scroll, stretch=2)
        
        # QSS code viewer (optional)
        qss_label = QLabel("Theme Code (QSS):")
        qss_label.setObjectName("sectionLabel")
        layout.addWidget(qss_label)
        
        self.qss_editor = QTextEdit()
        self.qss_editor.setObjectName("codeEditor")
        self.qss_editor.setReadOnly(True)
        layout.addWidget(self.qss_editor, stretch=1)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply Theme")
        self.apply_button.setObjectName("successButton")
        self.apply_button.clicked.connect(self._on_apply)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _create_preview_widgets(self, layout):
        """Create example widgets to preview the theme"""
        # Simulated dashboard pane
        pane1 = QFrame()
        pane1.setObjectName("paneSection")
        pane1_layout = QVBoxLayout(pane1)
        
        pane_title = QLabel("Example Pane")
        pane_title.setObjectName("paneLabel")
        pane1_layout.addWidget(pane_title)
        
        content = QLabel("This is what a dashboard pane looks like with borders, shadows, and background.")
        content.setWordWrap(True)
        pane1_layout.addWidget(content)
        
        layout.addWidget(pane1)
        
        # Card-style example
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        
        card_title = QLabel("Example Card")
        card_title.setObjectName("subtitle")
        card_layout.addWidget(card_title)
        
        card_content = QLabel("Cards contain information in a contained format.")
        card_content.setObjectName("mutedLabel")
        card_layout.addWidget(card_content)
        
        layout.addWidget(card)
        
        # Buttons example
        button_row = QHBoxLayout()
        
        primary_btn = QPushButton("Primary Button")
        primary_btn.setObjectName("primaryButton")
        
        success_btn = QPushButton("Success Button")
        success_btn.setObjectName("successButton")
        
        danger_btn = QPushButton("Danger Button")
        danger_btn.setObjectName("dangerButton")
        
        button_row.addWidget(primary_btn)
        button_row.addWidget(success_btn)
        button_row.addWidget(danger_btn)
        button_row.addStretch()
        
        layout.addLayout(button_row)
        
        # Form example
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        
        form_label = QLabel("Example Form:")
        form_label.setObjectName("formLabel")
        form_layout.addWidget(form_label)
        
        from PySide6.QtWidgets import QLineEdit
        form_input = QLineEdit()
        form_input.setObjectName("formInput")
        form_input.setPlaceholderText("Input field example")
        form_layout.addWidget(form_input)
        
        layout.addWidget(form_frame)
    
    def _on_apply(self):
        """Handle apply button click"""
        preset_name = self.preset_combo.currentText()
        self.apply_theme.emit(preset_name)
    
    def set_qss_preview(self, qss_content):
        """Display QSS code in the editor"""
        self.qss_editor.setPlainText(qss_content)
    
    def apply_preview_style(self, qss_content):
        """Apply style to the preview container"""
        self.preview_container.setStyleSheet(qss_content)
    
    def show_success(self, message):
        """Show success message"""
        QMessageBox.information(self, "Success", message)
    
    def show_error(self, message):
        """Show error message"""
        QMessageBox.warning(self, "Error", message)