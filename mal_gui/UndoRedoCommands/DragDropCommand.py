from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ModelScene import ModelScene

class DragDropCommand(QUndoCommand):
    def __init__(self, scene: ModelScene, item, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

        #Update the Object Explorer when number of items change
        self.scene.mainWindow.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        self.scene.removeItem(self.item)

        #Update the Object Explorer when number of items change
        self.scene.mainWindow.update_childs_in_object_explorer_signal.emit()
