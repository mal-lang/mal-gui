from __future__ import annotations
import json
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QPointF

from maltoolbox.model import AttackerAttachment

from ..connection_item import AssociationConnectionItem, EntrypointConnectionItem

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
        self.pasted_items = []
        self.pasted_connections: list[AssociationConnectionItem] = []
        self.pasted_entrypoints: list[EntrypointConnectionItem] = []
        self.clipboard = clipboard

    def redo(self):
        """Perform paste command"""
        print("\nPaste Redo is Called")
        serialized_data = self.clipboard.text()
        if serialized_data:
            deserialized_data = \
                self.scene.deserialize_graphics_items(serialized_data)
            print(json.dumps(deserialized_data, indent = 2))
            new_item_map = {}  # Map old assetId to new item

            # First pass: create items with new assetIds
            for data in deserialized_data:
                asset_type = data['asset_type']
                old_asset_sequence_id = data['asset_sequence_id']
                asset_properties = data['asset_properties']

                position_tuple = data['position']
                position = QPointF(position_tuple[0], position_tuple[1])

                # AddAsset Equivalent - Start - To Be Discussed
                if asset_type == "Attacker":
                    new_item = self.scene.add_attacker(position)
                else:
                    new_item = self.scene.add_asset(asset_type, position)
                    # we can assign the properties to new asset
                    for property_key, property_value in asset_properties:
                        setattr(
                            new_item.asset,
                            property_key,
                            float(property_value)
                        )

                self.pasted_items.append(new_item)
                # Map old assetId to new item
                new_item_map[old_asset_sequence_id] = new_item

                #AddAsset Equivalent - End

            #Adjust the position of all assetItems with offset values
            # Find the top-leftmost position among the items to be pasted
            min_x = min(item.pos().x() for item in self.pasted_items)
            min_y = min(item.pos().y() for item in self.pasted_items)
            top_left = QPointF(min_x, min_y)

            # Calculate the offset from the top-leftmost
            # position to the paste position
            offset = self.position - top_left

            for item in self.pasted_items:
                item.setPos(item.pos() + offset)
                # TODO After this newAsset.extras and position
                # should be filled - To be discussed
                self.scene.addItem(item)

            # Second pass: re-establish connections with new assetSequenceIds
            for data in deserialized_data:
                for entrypoint in data['entrypoints']:
                    print(f'ENTRYPOINT: {entrypoint}')
                    old_start_id, old_end_id, label = entrypoint
                    new_attacker_item = new_item_map[old_start_id]
                    new_asset_item = new_item_map[old_end_id]
                    new_connection = self.scene\
                        .add_entrypoint_connection(
                            label, new_attacker_item, new_asset_item
                        )
                    self.pasted_entrypoints.append(new_connection)
                    new_attacker_item.attackerAttachment.add_entry_point(
                        new_asset_item.asset,
                        label
                    )

                added_assoc_labels = set()
                for assoc in data['associations']:
                    print(data)
                    print(f'CONN: {assoc}')
                    old_start_id = data['asset_sequence_id']
                    (_, old_end_id, assoc_type,
                     left_field_name, right_field_name, label) = assoc

                    new_start_item = new_item_map[old_start_id]
                    new_end_item = new_item_map[old_end_id]

                    if label in added_assoc_labels:
                        continue

                    added_assoc_labels.add(label)

                    # Avoid Self reference
                    if new_start_item != new_end_item:
                        new_connection = self.scene\
                            .add_association_connection(
                                label, new_start_item, new_end_item
                            )

                        self.pasted_connections.append(new_connection)
                        print(f'ASSOC TYPE {assoc_type}')
                        association = getattr(self.scene.lcs.ns, assoc_type)()
                        left_asset = new_start_item.asset
                        right_asset = new_end_item.asset
                        setattr(association, left_field_name, [left_asset])
                        setattr(association, right_field_name, [right_asset])
                        self.scene.model.add_association(association)
                        new_connection.association = association

        # Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()

    def undo(self):
        """Undo paste command"""
        print("\nPaste Undo is Called")
        if self.pasted_items:
            print("Undo - Pasted Asset found")
            for conn in self.pasted_connections:
                conn.remove_labels()
                self.scene.removeItem(conn)
                self.scene.model.remove_association(conn.association)
            for item in self.pasted_items:
                self.scene.removeItem(item)
                self.scene.model.remove_asset(item.asset)
            self.pasted_items = []
            self.pasted_connections = []

        # Update the Object Explorer when number of items change
        self.scene.main_window.update_childs_in_object_explorer_signal.emit()
