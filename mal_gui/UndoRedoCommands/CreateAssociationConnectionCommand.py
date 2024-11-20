from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ModelScene import ModelScene
class CreateAssociationConnectionCommand(QUndoCommand):
    def __init__(
        self,
        scene: ModelScene,
        startItem,
        endItem,
        associationText,
        selectedItemAssociation,
        parent=None
    ):
        super().__init__(parent)
        self.scene  = scene
        self.startItem = startItem
        self.endItem = endItem
        self.associationText = associationText
        self.connection = None
        self.association = selectedItemAssociation

    def redo(self):
        self.connection = self.scene.add_association_connection(
            self.associationText,
            self.startItem,
            self.endItem
        )
        self.scene.model.add_association(self.association)

    def undo(self):
        self.connection.removeLabels()
        self.scene.removeItem(self.connection)
        self.scene.model.remove_association(self.association)
