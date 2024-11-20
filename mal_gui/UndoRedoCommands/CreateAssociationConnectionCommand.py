from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ModelScene import ModelScene
class CreateAssociationConnectionCommand(QUndoCommand):
    def __init__(
        self,
        scene: ModelScene,
        start_item,
        end_item,
        association_text,
        selected_item_association,
        parent=None
    ):
        super().__init__(parent)
        self.scene  = scene
        self.start_item = start_item
        self.end_item = end_item
        self.association_text = association_text
        self.connection = None
        self.association = selected_item_association

    def redo(self):
        """Perform create association connection"""
        self.connection = self.scene.add_association_connection(
            self.association_text,
            self.start_item,
            self.end_item
        )
        self.scene.model.add_association(self.association)

    def undo(self):
        """Undo create association connection"""
        self.connection.remove_labels()
        self.scene.removeItem(self.connection)
        self.scene.model.remove_association(self.association)
