from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import QGraphicsTextItem

class EditableTextItem(QGraphicsTextItem):
    lostFocus = Signal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        #  Disable editing initially
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setFont(QFont("Arial", 12 * 1.2, QFont.Bold))

    def focusOutEvent(self, event):
        """Overrides base method"""
        self.lostFocus.emit()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Overrides base method"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
        else:
            super().keyPressEvent(event)

    def select_all_text(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        self.setTextCursor(cursor)

    def deselect_text(self):
        cursor = self.textCursor()

        # Set cursor position to the start of the document
        cursor.setPosition(0)
        self.setTextCursor(cursor)
