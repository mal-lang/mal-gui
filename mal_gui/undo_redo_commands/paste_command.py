from __future__ import annotations
import json
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QPointF

from ..connection_item import AssociationConnectionItem, EntrypointConnectionItem
from ..object_explorer import ItemBase, AssetItem, AttackerItem

if TYPE_CHECKING:
    from ..model_scene import ModelScene

class PasteCommand(QUndoCommand):
    def __init__(
            self,
            scene: ModelScene,
            position,
            clipboard,
            parent=None
        ):

        super().__init__(parent)
        self.scene = scene
        self.position = position

        self.original_id_to_item: dict[int, ItemBase] = {}
        self.pasted_connections: list[AssociationConnectionItem] = []
        self.pasted_entrypoints: list[EntrypointConnectionItem] = []

        self.clipboard = clipboard
        self.has_performed_undo = False

    def redo(self):
        """Perform paste command"""

        print("\nPaste Redo is Called")

        serialized_data = self.clipboard.text()
        deserialized_data = (
            self.scene.deserialize_graphics_items(serialized_data)
        )
        print(json.dumps(deserialized_data, indent = 2))

        # First pass: create items with new assetIds
        for data in deserialized_data:

            item_type = data['type']
            old_id = data['id']
            position_tuple = data['position']
            position = QPointF(position_tuple[0], position_tuple[1])

            if item_type == "attacker":
                new_item = self.scene.create_attacker(position)

            elif item_type == "asset":
                asset_type = data['properties']['type']
                asset_name = data['properties']['name']

                new_asset_id = None

                if old_id in self.original_id_to_item:
                    # If undo -> redo, it should recreate undone paste
                    new_item = self.scene.recreate_asset(
                        self.original_id_to_item[old_id], position
                    )

                else:
                    new_item = self.scene.create_asset(
                        asset_type,
                        position,
                        name=asset_name,
                        asset_id=new_asset_id
                    )

            else:
                raise TypeError(f"Unknown item type {item_type}")

            self.original_id_to_item[old_id] = new_item

        # Adjust the position of all assetItems with offset values
        # Find the top-leftmost position among the items to be pasted
        min_x = min(
            item.pos().x() for item in self.original_id_to_item.values())
        min_y = min(
            item.pos().y() for item in self.original_id_to_item.values())
        top_left = QPointF(min_x, min_y)

        # Calculate the offset from the top-leftmost
        # position to the paste position
        offset = self.position - top_left

        for item in self.original_id_to_item.values():
            item.setPos(item.pos() + offset)
            self.scene.addItem(item)

        # Second pass: re-establish connections with new assetSequenceIds
        for data in deserialized_data:
            item_type = data['type']
            old_id = data['id']
            position_tuple = data['position']
            item = self.original_id_to_item[old_id]

            if isinstance(item, AssetItem):
                # Must be an asset
                associated_assets = data['properties']['associated_assets']
                for fieldname, assets in associated_assets.items():
                    for asset_id in assets:
                        right_item = self.original_id_to_item[asset_id]
                        item.asset.add_associated_assets(
                            fieldname, {right_item.asset}
                        )
                        con = self.scene.add_association_connection(
                            item, right_item, fieldname
                        )
                        self.pasted_connections.append(con)

            elif isinstance(item, AttackerItem):
                # Add attacker entrypoints
                for entrypoint in data['entrypoints']:
                    print(f'ENTRYPOINT: {entrypoint}')

                    old_start_id, old_end_id, label = entrypoint
                    new_attacker_item: AttackerItem = (
                        self.original_id_to_item[old_start_id]
                    )
                    new_asset_item: AssetItem = (
                        self.original_id_to_item[old_end_id]
                    )

                    new_connection = self.scene\
                        .add_entrypoint_connection(
                            label, new_attacker_item, new_asset_item
                        )

                    self.pasted_entrypoints.append(new_connection)
                    new_attacker_item.attacker.add_entry_point(
                        new_asset_item.asset, label
                    )

        # Update the Object Explorer when number of items change
        self.has_performed_undo = False
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo paste command"""

        print("\nPaste Undo is Called")
        if self.original_id_to_item:
            print("Undo - Pasted Asset found")

            for conn in self.pasted_connections:
                conn.remove_labels()
                self.scene.removeItem(conn)

            for conn in self.pasted_entrypoints:
                conn.remove_labels()
                self.scene.removeItem(conn)

            for item in self.original_id_to_item.values():
                if isinstance(item, AssetItem):
                    self.scene.remove_asset(item)
                elif isinstance(item, AttackerItem):
                    self.scene.remove_attacker(item)

        self.has_performed_undo = True
        self.pasted_connections = []
        self.pasted_entrypoints = []

        # Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
