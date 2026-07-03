from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QUndoCommand
from ..object_explorer import AssetItem, AttackerItem
from ..connection_item import (
    AssociationConnectionItem,
    EntrypointConnectionItem,
    GoalConnectionItem,
    MetaDetectorConnectionItem,
)

if TYPE_CHECKING:
    from ..model_scene import ModelScene
    from ..connection_item import IConnectionItem


class DeleteCommand(QUndoCommand):
    def __init__(self, scene: ModelScene, items, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = items
        self.connections: list[IConnectionItem] = []

        # Save connections of all items
        for item in self.items:
            if hasattr(item, "connections"):
                self.connections.extend(item.connections.copy())

    def redo(self):
        """Perform delete"""
        print("REDO delete")
        # Store the connections before removing the items
        for connection in self.connections:
            connection.remove_labels()
            self.scene.removeItem(connection)

            if isinstance(connection, EntrypointConnectionItem):
                step_full_name = (
                    connection.asset_item.asset.name + ":" + connection.attack_step_name
                )
                try:
                    connection.attacker_item.entry_points.remove(step_full_name)
                except ValueError:
                    print(
                        f"Entrypoint {step_full_name} not found in attacker {connection.attacker_item.name}"
                    )

            if isinstance(connection, GoalConnectionItem):
                step_full_name = (
                    connection.asset_item.asset.name + ":" + connection.attack_step_name
                )
                try:
                    connection.attacker_item.goals.remove(step_full_name)
                except ValueError:
                    print(
                        f"Entrypoint {step_full_name} not found in attacker {connection.attacker_item.name}"
                    )
            if isinstance(connection, MetaDetectorConnectionItem):
                asset_name = connection.asset_item.asset.name
                try:
                    connection.meta_detector_item.connected_assets.remove(asset_name)
                except ValueError:
                    print(
                        f"Connection to {asset_name} not found in meta detector {connection.meta_detector_item.name}"
                    )
                connection.meta_detector_item.connected_asset_labels.pop(
                    asset_name, None
                )

        for item in self.items:
            if isinstance(item, AssetItem):
                print("Deleting from model")
                self.scene.remove_asset(item)
            if isinstance(item, AttackerItem):
                self.scene.remove_attacker(item)

        # Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo delete"""
        print("UNDO delete")
        # Add items back to the scene
        for item in self.items:
            if isinstance(item, AssetItem):
                self.scene.recreate_asset(item, item.pos())
            if isinstance(item, AttackerItem):
                print("Can not undo delete attacker")

        # Restore connections
        for connection in self.connections:
            if isinstance(connection, EntrypointConnectionItem):
                self.scene.add_entrypoint_connection(
                    connection.attack_step_name,
                    connection.attacker_item,
                    connection.asset_item,
                )
                step_full_name = (
                    connection.asset_item.asset.name + ":" + connection.attack_step_name
                )
                connection.attacker_item.entry_points.append(step_full_name)

            if isinstance(connection, GoalConnectionItem):
                self.scene.add_goal_connection(
                    connection.attack_step_name,
                    connection.attacker_item,
                    connection.asset_item,
                )
                step_full_name = (
                    connection.asset_item.asset.name + ":" + connection.attack_step_name
                )
                connection.attacker_item.goals.append(step_full_name)
            elif isinstance(connection, MetaDetectorConnectionItem):
                self.scene.add_meta_detector_connection(
                    connection.meta_detector_item,
                    connection.asset_item,
                    connection.label_value,
                )
                asset_name = connection.asset_item.asset.name
                if asset_name not in connection.meta_detector_item.connected_assets:
                    connection.meta_detector_item.connected_assets.append(asset_name)
                connection.meta_detector_item.connected_asset_labels[asset_name] = (
                    connection.label_value
                )

            elif isinstance(connection, AssociationConnectionItem):
                self.scene.add_association_connection(
                    connection.start_item,
                    connection.end_item,
                    connection.right_fieldname,
                )
                connection.start_item.asset.add_associated_assets(
                    connection.right_fieldname, {connection.end_item.asset}
                )

        # Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
