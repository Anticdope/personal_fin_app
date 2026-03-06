"""
ui/shared/draggable_card_container.py

Reusable drag-and-drop card container.
Drop this into any pane to get scrollable, reorderable cards.
"""
from PySide6.QtWidgets import (QScrollArea, QWidget, QVBoxLayout, QFrame,
                               QSizePolicy, QApplication)
from PySide6.QtCore import Qt, Signal, QPoint, QMimeData, QTimer
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor


class DropIndicator(QFrame):
    """Thin line shown between cards during a drag"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)
        self.setObjectName("dropIndicator")
        self.setStyleSheet("background-color: #3498DB; border-radius: 2px;")
        self.hide()


class DraggableCard(QFrame):
    """
    Wrapper that makes any QFrame draggable.
    Pass your existing cardFrame widget as child_widget.
    """
    drag_started = Signal(object)   # emits self
    drag_ended   = Signal(object)   # emits self

    def __init__(self, child_widget, card_id, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.child_widget = child_widget
        self._drag_start_pos = None
        self._dragging = False

        self.setObjectName("cardFrame")
        self.setCursor(Qt.OpenHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(child_widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_start_pos:
            distance = (event.position().toPoint() - self._drag_start_pos).manhattanLength()
            if distance >= QApplication.startDragDistance() and not self._dragging:
                self._dragging = True
                self.setCursor(Qt.ClosedHandCursor)
                self.drag_started.emit(self)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self.setCursor(Qt.OpenHandCursor)
            self.drag_ended.emit(self)
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)


class DraggableCardContainer(QScrollArea):
    """
    Drop-in replacement for QScrollArea + QVBoxLayout container.

    Usage in a pane view:
        self.card_container = DraggableCardContainer()
        layout.addWidget(self.card_container)

        # Add a card:
        self.card_container.add_card(card_id, card_widget)

        # Get current order:
        order = self.card_container.get_order()  # list of card_ids

        # Restore a saved order:
        self.card_container.set_order(saved_order)

    Signals:
        order_changed(list[str])  — emitted after every successful reorder
    """
    order_changed = Signal(list)   # list of card_ids in new order

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setObjectName("cardScrollArea")

        self._inner = QWidget()
        self._inner.setObjectName("cardContainerInner")
        self._layout = QVBoxLayout(self._inner)
        self._layout.setSpacing(10)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setAlignment(Qt.AlignTop)
        # State - must be initialized BEFORE setWidget triggers eventFilter
        self._cards = []
        self._dragging_card = None
        self._drop_index = -1

        self.setWidget(self._inner)

        self._drop_indicator = DropIndicator(self._inner)

        # Enable mouse tracking on inner widget so we get move events
        self._inner.setMouseTracking(True)
        self._inner.installEventFilter(self)

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def add_card(self, card_id: str, widget: QWidget):
        """Append a card to the container."""
        card = DraggableCard(widget, card_id, self._inner)
        card.drag_started.connect(self._on_drag_started)
        card.drag_ended.connect(self._on_drag_ended)
        self._cards.append(card)
        self._rebuild_layout()

    def clear_cards(self):
        """Remove all cards (does not delete wrapped widgets)."""
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
        self._drop_indicator.hide()

    def get_order(self) -> list:
        """Return current card_ids in display order."""
        return [c.card_id for c in self._cards]

    def set_order(self, order: list):
        """Reorder cards to match a saved order list of card_ids."""
        id_to_card = {c.card_id: c for c in self._cards}
        new_cards = []
        for card_id in order:
            if card_id in id_to_card:
                new_cards.append(id_to_card.pop(card_id))
        # Append any cards not in the saved order at the end
        new_cards.extend(id_to_card.values())
        self._cards = new_cards
        self._rebuild_layout()

    # ------------------------------------------------------------------ #
    #  Internal drag logic
    # ------------------------------------------------------------------ #

    def _rebuild_layout(self):
        """Rebuild layout from self._cards list."""
        # Remove all items
        while self._layout.count():
            self._layout.takeAt(0)

        for card in self._cards:
            card.setParent(self._inner)
            self._layout.addWidget(card)

        self._layout.addStretch()

    def _on_drag_started(self, card: DraggableCard):
        self._dragging_card = card
        card.setProperty("dragging", True)
        card.setStyleSheet("QFrame#cardFrame { opacity: 0.5; }")
        self._drop_indicator.show()

    def _on_drag_ended(self, card: DraggableCard):
        self._drop_indicator.hide()

        if self._dragging_card and self._drop_index >= 0:
            # Perform the reorder
            self._cards.remove(self._dragging_card)
            insert_at = min(self._drop_index, len(self._cards))
            self._cards.insert(insert_at, self._dragging_card)
            self._rebuild_layout()
            self.order_changed.emit(self.get_order())

        if self._dragging_card:
            self._dragging_card.setStyleSheet("")
            self._dragging_card = None

        self._drop_index = -1

    def eventFilter(self, obj, event):
        """Track mouse position over inner widget during drag."""
        from PySide6.QtCore import QEvent
        if obj is self._inner and self._dragging_card:
            if event.type() == QEvent.MouseMove:
                self._update_drop_position(event.position().toPoint())
        return super().eventFilter(obj, event)

    def mouseMoveEvent(self, event):
        """Also track moves on the scroll area itself."""
        if self._dragging_card:
            # Convert to inner widget coordinates
            local = self._inner.mapFromGlobal(
                self.mapToGlobal(event.position().toPoint())
            )
            self._update_drop_position(local)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Catch release on scroll area (not just on cards)."""
        if self._dragging_card:
            self._on_drag_ended(self._dragging_card)
        super().mouseReleaseEvent(event)

    def _update_drop_position(self, local_pos: QPoint):
        """Move the drop indicator to the nearest gap between cards."""
        if not self._cards:
            return

        best_index = len(self._cards)
        best_dist = float('inf')

        for i, card in enumerate(self._cards):
            if card is self._dragging_card:
                continue
            card_center_y = card.pos().y() + card.height() // 2
            dist = abs(local_pos.y() - card_center_y)
            if dist < best_dist:
                best_dist = dist
                best_index = i if local_pos.y() < card_center_y else i + 1

        self._drop_index = best_index

        # Position the indicator
        if best_index == 0:
            first = self._cards[0]
            y = first.pos().y() - 4
        elif best_index >= len(self._cards):
            last = self._cards[-1]
            y = last.pos().y() + last.height() + 1
        else:
            above = self._cards[best_index - 1]
            below = self._cards[best_index]
            y = (above.pos().y() + above.height() + below.pos().y()) // 2

        self._drop_indicator.setGeometry(
            0, y, self._inner.width(), 3
        )
        self._drop_indicator.raise_()
