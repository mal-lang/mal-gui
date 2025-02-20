from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..connection_item import IConnectionItem
    from ..model_scene import ModelScene

class DeleteConnectionCommand(QUndoCommand):
    def __init__(self, scene: ModelScene, item, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.connection: IConnectionItem = item

    def redo(self):
        """Perform delete connection"""
        self.connection.delete()
        self.connection.remove_labels()
        self.scene.removeItem(self.connection)

    def undo(self):
        """Undo delete connection"""
        self.scene.addItem(self.connection)
        self.connection.restore_labels()
        self.connection.update_path()
