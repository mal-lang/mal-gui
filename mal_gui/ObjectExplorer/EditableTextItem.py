from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import QGraphicsTextItem

class EditableTextItem(QGraphicsTextItem):
    lostFocus = Signal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setTextInteractionFlags(Qt.NoTextInteraction)  # Disable editing initially
        self.setFont(QFont("Arial", 12 * 1.2, QFont.Bold))

    def focusOutEvent(self, event):
        self.lostFocus.emit()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
        else:
            super().keyPressEvent(event)

    def selectAllText(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        self.setTextCursor(cursor)
        
    def deselectText(self):
        cursor = self.textCursor()
        cursor.setPosition(0)  # Set cursor position to the start of the document
        self.setTextCursor(cursor)