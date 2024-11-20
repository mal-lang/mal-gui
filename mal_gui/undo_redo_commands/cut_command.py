from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..model_scene import ModelScene
    from ..connection_item import IConnectionItem

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
        self.connections: list[IConnectionItem] = []

        # Save connections of all items
        for item in self.items:
            if hasattr(item, 'connections'):
                self.connections.extend(item.connections.copy())

    def redo(self):
        """Perform cut command"""
        self.cut_item_flag = True
        serialized_data = self.scene.serialize_graphics_items(
            self.items, self.cut_item_flag)
        self.clipboard.clear()
        self.clipboard.setText(serialized_data)

        # Remove connections before removing the items
        for connection in self.connections:
            connection.remove_labels()
            self.scene.removeItem(connection)

        for item in self.items:
            self.scene.removeItem(item)

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo cut command"""
        # Add items back to the scene
        for item in self.items:
            self.scene.addItem(item)

        # Restore connections
        for connection in self.connections:
            self.scene.addItem(connection)
            connection.restore_labels()
            connection.update_path()

        self.clipboard.clear()

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
