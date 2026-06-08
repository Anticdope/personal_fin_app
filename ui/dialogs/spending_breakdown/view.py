"""
Spending Breakdown Dialog - View
Scrollable breakdown of spending by category with per-transaction detail
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class SpendingBreakdownView(QDialog):
    """View: Scrollable spending breakdown dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spending Breakdown")
        self.setModal(True)
        self.resize(600, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(20, 20, 20, 16)

        # Title + total row (fixed, outside scroll)
        self.header_frame = QFrame()
        self.header_frame.setObjectName("formFrame")
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(12, 12, 12, 12)
        header_layout.setSpacing(4)

        self.title_label = QLabel()
        self.title_label.setObjectName("dialogTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title_label)

        self.total_label = QLabel()
        self.total_label.setObjectName("negativeLabel")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(self.total_label)

        layout.addWidget(self.header_frame)
        layout.addSpacing(12)

        # Scrollable category list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addStretch()

        scroll.setWidget(self.content)
        layout.addWidget(scroll)

        layout.addSpacing(12)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryButton")
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def display_breakdown(self, data):
        """Populate the dialog with breakdown data."""
        self.title_label.setText(f"Spending Breakdown — {data['month_label']}")
        self.total_label.setText(f"Total Spent: ${data['total']:,.2f}")

        # Clear existing category blocks (leave the stretch)
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for cat in data['categories']:
            block = self._make_category_block(cat)
            self.content_layout.insertWidget(self.content_layout.count() - 1, block)

    def _make_category_block(self, cat):
        """Build a collapsible-style card for one category."""
        frame = QFrame()
        frame.setObjectName("cardFrame")
        layout = QVBoxLayout(frame)
        layout.setSpacing(0)
        layout.setContentsMargins(12, 10, 12, 10)

        # ── Category header row ──────────────────────────────────────────────
        header = QHBoxLayout()

        # Colour dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {cat['color']}; font-size: 14px;")
        dot.setFixedWidth(20)
        header.addWidget(dot)

        name_label = QLabel(cat['name'])
        name_label.setObjectName("subtitle")
        header.addWidget(name_label)

        header.addStretch()

        total_label = QLabel(f"${cat['total']:,.2f}")
        total_label.setObjectName("negativeLabel")
        total_label.setStyleSheet("font-weight: bold;")
        header.addWidget(total_label)

        layout.addLayout(header)

        # ── Divider ──────────────────────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("divider")
        layout.addSpacing(6)
        layout.addWidget(divider)
        layout.addSpacing(4)

        # ── Transaction rows ─────────────────────────────────────────────────
        for tx in cat['transactions']:
            tx_row = QHBoxLayout()
            tx_row.setSpacing(8)

            date_label = QLabel(tx['date'])
            date_label.setObjectName("mutedLabel")
            date_label.setFixedWidth(52)
            tx_row.addWidget(date_label)

            desc_label = QLabel(tx['description'])
            desc_label.setObjectName("formLabel")
            desc_label.setWordWrap(True)
            tx_row.addWidget(desc_label, 1)

            amt_label = QLabel(f"${tx['amount']:,.2f}")
            amt_label.setObjectName("negativeLabel")
            amt_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amt_label.setFixedWidth(80)
            tx_row.addWidget(amt_label)

            layout.addLayout(tx_row)

        return frame

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode