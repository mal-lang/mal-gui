from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand
from ..connection_item import AssociationConnectionItem, EntrypointConnectionItem

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

        if isinstance(self.connection, AssociationConnectionItem):
            self.scene.remove_association(self.connection)
        elif isinstance(self.connection, EntrypointConnectionItem):
            self.scene.remove_entrypoint(self.connection)
        else:
            raise ValueError("Unknown connection type")

    def undo(self):
        """Undo delete connection"""

        if isinstance(self.connection, AssociationConnectionItem):
            self.connection = self.scene.add_association_connection(
                self.connection.start_item,
                self.connection.end_item,
                self.connection.right_fieldname
            )
        elif isinstance(self.connection, EntrypointConnectionItem):
            self.connection = self.scene.add_entrypoint_connection(
                self.connection.attack_step_name,
                self.connection.attacker_item,
                self.connection.asset_item
            )
        else:
            raise ValueError("Unknown connection type")
