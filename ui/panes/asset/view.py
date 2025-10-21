"""
Asset Pane View - Pure UI for displaying assets
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt


class AssetView(QWidget):
    """View: Pure UI for displaying assets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scrollable asset container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.asset_container = QWidget()
        self.asset_layout = QVBoxLayout(self.asset_container)
        self.asset_layout.setSpacing(10)
        self.asset_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.asset_container)
        layout.addWidget(scroll)
    
    def display_assets(self, assets_data):
        """
        Display all assets
        assets_data: list of dicts with asset info
        """
        # Clear existing
        self._clear_assets()
        
        if not assets_data:
            no_assets = QLabel("No assets")
            no_assets.setObjectName("mutedLabel")
            no_assets.setAlignment(Qt.AlignCenter)
            self.asset_layout.addWidget(no_assets)
            return
        
        for asset in assets_data:
            asset_element = self.create_asset_element(asset)
            self.asset_layout.addWidget(asset_element)
    
    def create_asset_element(self, asset):
        """Create a widget for a single asset"""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        
        # Name
        name_label = QLabel(asset['name'])
        name_label.setObjectName("subtitle")
        layout.addWidget(name_label)
        
        # Current value
        value_label = QLabel(f"Value: ${asset['value']:,.2f}")
        value_label.setObjectName("positiveLabel")
        layout.addWidget(value_label)
        
        # Original value
        original_label = QLabel(f"Original: ${asset['original_value']:,.2f}")
        original_label.setObjectName("mutedLabel")
        layout.addWidget(original_label)
        
        # Change
        change = asset['change']
        if change != 0:
            change_label = QLabel(f"Change: ${change:+,.2f} ({asset['change_percent']:+.1f}%)")
            if change >= 0:
                change_label.setObjectName("positiveLabel")
            else:
                change_label.setObjectName("negativeLabel")
            layout.addWidget(change_label)
        
        return frame
    
    def _clear_assets(self):
        """Clear all asset widgets"""
        while self.asset_layout.count():
            child = self.asset_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_dark_mode(self, dark_mode):
        """Update theme for this pane"""
        self.dark_mode = dark_mode
    
    def get_widget_name(self):
        """Return pane display name"""
        return "Assets"