from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand
from ..object_explorer import AssetItem, AttackerItem
from ..connection_item import AssociationConnectionItem, EntrypointConnectionItem

if TYPE_CHECKING:
    from ..model_scene import ModelScene
    from ..connection_item import IConnectionItem

class DeleteCommand(QUndoCommand):
    def __init__(
            self,
            scene: ModelScene,
            items,
            parent=None
        ):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.connections: list[IConnectionItem] = []

        # Save connections of all items
        for item in self.items:
            if hasattr(item, 'connections'):
                self.connections.extend(item.connections.copy())

    def redo(self):
        """Perform delete"""
        # Store the connections before removing the items
        for connection in self.connections:
            connection.remove_labels()
            self.scene.removeItem(connection)

        for item in self.items:
            self.scene.removeItem(item)

            if isinstance(item, AssetItem):
                self.scene.model.remove_asset(item.asset)
            if isinstance(item, AttackerItem):
                self.scene.model.remove_attacker(item.attacker)

        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo delete"""
        # Add items back to the scene
        for item in self.items:
            if isinstance(item, AssetItem):
                self.scene.recreate_asset(item, item.pos())
            if isinstance(item, AttackerItem):
                self.scene.model.add_attacker(item.attacker)

        # Restore connections
        for connection in self.connections:

            if isinstance(connection, EntrypointConnectionItem):
                self.scene.add_entrypoint_connection(
                    connection.attack_step_name,
                    connection.attacker_item,
                    connection.asset_item
                )
                connection.attacker_item.attacker.add_entry_point(
                    connection.asset_item.asset, connection.attack_step_name
                )


            elif isinstance(connection, AssociationConnectionItem):
                self.scene.add_association_connection(
                    connection.start_item,
                    connection.end_item,
                    connection.right_fieldname
                )
                connection.start_item.asset.add_associated_assets(
                    connection.right_fieldname, {connection.end_item.asset}
                )


        #Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
