"""
ui/panes/asset/view.py

Asset Pane View - Pure UI for displaying assets.
Updated: DraggableCardContainer replaces plain scroll area.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from ui.shared.draggable_card_container import DraggableCardContainer


class AssetView(QWidget):
    """View: Pure UI for displaying assets"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self._current_data = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.card_container = DraggableCardContainer()
        layout.addWidget(self.card_container)

    def display_assets(self, assets_data):
        self._current_data = assets_data
        self.card_container.clear_cards()

        if not assets_data:
            empty = QLabel("No assets")
            empty.setObjectName("mutedLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.card_container.add_card("__empty__", empty)
            return

        for asset in assets_data:
            card_widget = self._build_card_widget(asset)
            card_id = asset.get('id', asset['name'])
            self.card_container.add_card(card_id, card_widget)

    def _build_card_widget(self, asset):
        inner = QFrame()
        inner.setObjectName("cardFrame")
        layout = QVBoxLayout(inner)

        name_label = QLabel(asset['name'])
        name_label.setObjectName("subtitle")
        layout.addWidget(name_label)

        value_label = QLabel(f"Value: ${asset['value']:,.2f}")
        value_label.setObjectName("positiveLabel")
        layout.addWidget(value_label)

        if 'original_value' in asset and asset['original_value']:
            orig = asset['original_value']
            change = asset['value'] - orig
            change_text = f"{'▲' if change >= 0 else '▼'} ${abs(change):,.2f} from original"
            change_label = QLabel(change_text)
            change_label.setObjectName("positiveLabel" if change >= 0 else "negativeLabel")
            layout.addWidget(change_label)

        return inner

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
