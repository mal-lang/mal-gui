from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..ModelScene import ModelScene

class CutCommand(QUndoCommand):
    def __init__(
            self,
            scene: ModelScene,
            items,
            clipboard,
            parent=None
        ):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.clipboard = clipboard
        self.connections = []

        # Save connections of all items
        for item in self.items:
            if hasattr(item, 'connections'):
                self.connections.extend(item.connections.copy())

    def redo(self):
        self.cutItemFlag = True
        serializedData = self.scene.serialize_graphics_items(self.items, self.cutItemFlag)
        self.clipboard.clear()
        self.clipboard.setText(serializedData)

        # Remove connections before removing the items
        for connection in self.connections:
            connection.removeLabels()
            self.scene.removeItem(connection)

        for item in self.items:
            self.scene.removeItem(item)

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        # Add items back to the scene
        for item in self.items:
            self.scene.addItem(item)

        # Restore connections
        for connection in self.connections:
            self.scene.addItem(connection)
            connection.restoreLabels()
            connection.updatePath()

        self.clipboard.clear()

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
