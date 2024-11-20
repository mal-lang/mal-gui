from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..ModelScene import ModelScene

class CopyCommand(QUndoCommand):
    def __init__(self, scene: ModelScene, items, clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.clipboard = clipboard

    def redo(self):
        self.cutItemFlag = False
        serializedData = \
            self.scene.serialize_graphics_items(self.items, self.cutItemFlag)
        self.clipboard.clear()
        self.clipboard.setText(serializedData)

    def undo(self):
        self.clipboard.clear()
