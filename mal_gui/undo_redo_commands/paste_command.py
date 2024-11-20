from __future__ import annotations
import json
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QPointF

from ..connection_item import AssociationConnectionItem

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
        self.clipboard = clipboard

    def redo(self):
        """Perform paste command"""
        print("\nPaste Redo is Called")
        serialized_data = self.clipboard.text()
        print("\nSerializedData = " + str(len(serialized_data)))
        print("\nSerializedData = " + str(serialized_data))
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
                    # newAttackerAttachment = AttackerAttachment()
                    # self.scene.model.add_attacker(newAttackerAttachment)

                    new_item = self.scene.asset_factory.get_asset(asset_type)
                    # new_item.asset_name = "Attacker"
                    # new_item.type_text_item.setPlainText(str("Attacker"))
                    new_item.setPos(position)
                    # self.scene._attacker_id_to_item[newAttackerAttachment.id] = new_item
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
                for conn in data['connections']:
                    print(f'CONN: {conn}')
                    old_start_id = data['asset_sequence_id']
                    old_end_id, old_label = conn[1], conn[2]
                    new_start_item = new_item_map[old_start_id]
                    new_end_item = new_item_map[old_end_id]

                    #Avoid Self reference
                    if new_start_item != new_end_item:
                        new_connection = AssociationConnectionItem(old_label,
                            new_start_item,
                            new_end_item,
                            self.scene
                        )
                        self.scene.addItem(new_connection)
                        self.pasted_connections.append(new_connection)
                        assoc_type = old_label.split('-->')[1]
                        print(f'ASSOC TYPE {assoc_type}')
                        association = getattr(self.scene.lcs.ns, assoc_type)()
                        left_asset = new_start_item.asset
                        right_asset = new_end_item.asset
                        print(
                            f'LEFT ASSET NAME:{left_asset.name}'
                            f'ID:{left_asset.id}'
                            f'TYPE:{left_asset.type}'
                        )
                        print(
                            f'RIGHT ASSET NAME:{right_asset.name}'
                            f'ID:{right_asset.id}'
                            f'TYPE:{right_asset.type}'
                        )
                        left_field_name, right_field_name = \
                            self.scene.model.get_association_field_names(
                                association
                            )
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
