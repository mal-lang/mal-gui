from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from ..model_scene import ModelScene
    from ..model_scene import AssetItem

class CreateAssociationConnectionCommand(QUndoCommand):

    def __init__(
        self,
        scene: ModelScene,
        start_item: AssetItem,
        end_item: AssetItem,
        field_name,
        parent=None
    ):

        super().__init__(parent)
        self.scene  = scene
        self.start_item = start_item
        self.end_item = end_item
        self.fieldname = field_name
        self.connection = None

    def redo(self):
        """Perform create association connection"""
        self.connection = self.scene.add_association_connection(
            self.start_item, self.end_item, self.fieldname
        )
        self.start_item.asset.add_associated_assets(
            self.fieldname, {self.end_item.asset}
        )

    def undo(self):
        """Undo create association connection"""
        self.connection.remove_labels()
        self.scene.removeItem(self.connection)
        self.start_item.asset.remove_associated_assets(
            self.fieldname, {self.end_item.asset}
        )
