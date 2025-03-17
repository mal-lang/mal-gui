from __future__ import annotations

import pickle
import base64
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QGraphicsScene,
    QMenu,
    QApplication,
    QGraphicsLineItem,
    QDialog,
    QGraphicsRectItem
)
from PySide6.QtGui import QTransform,QAction,QUndoStack,QPen
from PySide6.QtCore import QLineF, Qt, QPointF,QRectF

from maltoolbox.model import Model, AttackerAttachment

from .connection_item import AssociationConnectionItem,EntrypointConnectionItem
from .connection_dialog import AssociationConnectionDialog,EntrypointConnectionDialog
from .object_explorer import AssetItem, AttackerItem, EditableTextItem, ItemBase
from .assets_container import AssetsContainer, AssetsContainerRectangleBox

from .undo_redo_commands import (
    CutCommand,
    CopyCommand,
    PasteCommand,
    DeleteCommand,
    MoveCommand,
    DragDropAttackerCommand,
    DragDropAssetCommand,
    CreateAssociationConnectionCommand,
    CreateEntrypointConnectionCommand,
    DeleteConnectionCommand,
    ContainerizeAssetsCommand
)

if TYPE_CHECKING:
    from object_explorer.asset_factory import AssetFactory
    from .main_window import MainWindow
    from maltoolbox.language import LanguageGraph
    from maltoolbox.model import ModelAsset
    from .connection_item import IConnectionItem

class ModelScene(QGraphicsScene):
    def __init__(
            self,
            asset_factory: AssetFactory,
            lang_graph: LanguageGraph,
            model: Model,
            main_window: MainWindow
        ):
        super().__init__()

        self.asset_factory = asset_factory
        self.undo_stack = QUndoStack(self)
        self.clipboard = QApplication.clipboard()
        self.main_window = main_window

        # # Assign the MAL language graph, language classes factory, and
        # # instance model
        self.lang_graph = lang_graph
        self.model = model

        self._asset_id_to_item = {}
        self._attacker_id_to_item = {}

        self.copied_item = None
        self.cut_item_flag = False

        self.line_item = None
        self.start_item = None
        self.end_item = None

        self.moving_item = None
        self.start_pos = None

        self.show_association_checkbox_status = False

        #For multiple select and handle
        self.selection_rect = None
        self.origin = QPointF()
        self.is_dragging_item = False
        self.dragged_items = []
        self.initial_positions = {}

        #Container
        self.container_box = None

    def dragEnterEvent(self, event):
        """Overrides base method"""
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Overrides base method"""
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Overrides base method"""
        print("dropEvent")
        if event.mimeData().hasFormat('text/plain'):
            print("format is text/plain")
            item_type = event.mimeData().text()
            print("dropped item type = " + item_type)
            pos = event.scenePos()

            if item_type == "Attacker":
                # Perform drag and drop of Asset
                self.undo_stack.push(
                    DragDropAttackerCommand(self, pos)
                )
            else:
                # Perform drag and drop of Asset
                self.undo_stack.push(
                    DragDropAssetCommand(self, item_type, pos)
                )
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        """Overrides base method"""
        print(event.button())
        clicked_item = self.itemAt(event.scenePos(), QTransform())

        if (
            event.button() == Qt.LeftButton
            and QApplication.keyboardModifiers() == Qt.ShiftModifier
        ):
            print("Scene Mouse Press event Shift+Left Mouse Button")

            if isinstance(clicked_item, EditableTextItem):
                # If clicked on EditableTextItem,
                # get its parent which is ItemBase1
                clicked_item = clicked_item.parentItem()

            if isinstance(clicked_item, ItemBase):
                self.start_item = clicked_item
                self.line_item = QGraphicsLineItem()
                self.line_item.setLine(
                    QLineF(event.scenePos(), event.scenePos())
                )
                self.addItem(self.line_item)
                print(f"Start item set: {self.start_item}")
                # Without return Item was moving with mouse.
                return

        elif event.button() == Qt.LeftButton:
            print("Item left click", clicked_item)

            if isinstance(clicked_item, EditableTextItem):
                clicked_item = clicked_item.parentItem()

            if isinstance(
                clicked_item, (ItemBase, AssetsContainer)
            ):

                if clicked_item.isSelected():
                    print("Item is already selected")
                    self.moving_item = clicked_item
                    self.start_pos = clicked_item.pos()
                    self.dragged_items = [i for i in self.selectedItems() if isinstance(i, (AssetItem, AttackerItem))]
                    self.initial_positions = {i: i.pos() for i in self.dragged_items}
                else:
                    print("Item is not selected")
                    self.clearSelection()
                    clicked_item.setSelected(True)
                    self.moving_item = clicked_item
                    self.start_pos = clicked_item.pos()
                    self.dragged_items = [clicked_item]
                    self.initial_positions = {clicked_item: clicked_item.pos()}
            else:
                self.clearSelection()  # Deselect all items if clicking outside any item
                self.origin = event.scenePos()
                self.selection_rect = QGraphicsRectItem(QRectF(self.origin, self.origin))
                self.selection_rect.setPen(QPen(Qt.blue, 2, Qt.DashLine))
                self.addItem(self.selection_rect)

        elif event.button() == Qt.RightButton:
            print("Item right click", clicked_item)

            if clicked_item and isinstance(clicked_item, ItemBase):
                if not clicked_item.isSelected():
                    self.clearSelection()
                    clicked_item.setSelected(True)

        self.show_items_details()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Overrides base method"""
        if self.line_item and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Move event")
            self.line_item.setLine(QLineF(self.line_item.line().p1(), event.scenePos()))
        elif self.moving_item and not QApplication.keyboardModifiers() == Qt.ShiftModifier:
            new_pos = event.scenePos()
            delta = new_pos - self.start_pos
            for item in self.dragged_items:
                item.setPos(self.initial_positions[item] + delta)
        elif self.selection_rect and not self.moving_item:
            rect = QRectF(self.origin, event.scenePos()).normalized()
            self.selection_rect.setRect(rect)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Overrides base method"""
        released_item = self.itemAt(event.scenePos(), QTransform())

        if (
            event.button() == Qt.LeftButton
            and self.line_item
            and QApplication.keyboardModifiers() == Qt.ShiftModifier
        ):

            print("Entered Release with Shift")

            # Temporarily remove the line item to avoid interference
            self.removeItem(self.line_item)
            print(f"item is: {released_item}")

            if isinstance(released_item, EditableTextItem):
                # If clicked on EditableTextItem, get its parent which is AssetItem
                released_item = released_item.parentItem()
                if isinstance(released_item, (AssetItem, AttackerItem)):
                    self.end_item = released_item
                else:
                    self.end_item = None
            else:
                self.end_item = released_item


            # Create and show the connection dialog
            if self.end_item:

                if (
                    isinstance(self.start_item, AssetItem)
                    and isinstance(self.end_item, AssetItem)
                ):
                    # Asset to asset connection

                    dialog = AssociationConnectionDialog(
                        self.start_item,
                        self.end_item,
                        self.lang_graph,
                        self.model
                    )

                    if dialog.exec() == QDialog.Accepted:
                        selected_item = dialog.association_list_widget.currentItem()
                        if selected_item:
                            print("Selected Association Text is: "+ selected_item.text())
                            # connection = AssociationConnectionItem(selected_item.text(),self.start_item, self.end_item,self)
                            # self.addItem(connection)
                            command = CreateAssociationConnectionCommand(
                                self, self.start_item, self.end_item, dialog.field_name
                            )
                            self.undo_stack.push(command)
                        else:
                            print("No end item found")
                            self.removeItem(self.line_item)
                else:

                    if (
                        isinstance(self.start_item, AttackerItem)
                        and isinstance(self.end_item, AttackerItem)
                    ):
                        raise TypeError("Start and end item can not both be type 'Attacker'")

                    attacker_item = (
                        self.start_item
                        if isinstance(self.start_item, AttackerItem)
                        else self.end_item
                    )
                    asset_item = (
                        self.end_item
                        if isinstance(self.start_item, AttackerItem)
                        else self.start_item
                    )

                    dialog = EntrypointConnectionDialog(
                        attacker_item, asset_item, self.lang_graph, self.model
                    )
                    if dialog.exec() == QDialog.Accepted:
                        selected_item = dialog.attack_step_list_widget.currentItem()
                        if selected_item:
                            print("Selected Entrypoint Text is: "+ selected_item.text())
                            command = CreateEntrypointConnectionCommand(
                                self, attacker_item, asset_item, selected_item.text(),
                            )
                            self.undo_stack.push(command)
                        else:
                            print("No end item found")
                            self.removeItem(self.line_item)
            else:
                print("No end item found")
                self.removeItem(self.line_item)

            self.line_item = None
            self.start_item = None
            self.end_item = None

        elif event.button() == Qt.LeftButton:

            if self.selection_rect:
                items = self.items(self.selection_rect.rect(), Qt.IntersectsItemShape)
                for item in items:
                    if isinstance(item, (AssetItem, AttackerItem)):
                        item.setSelected(True)
                self.removeItem(self.selection_rect)
                self.selection_rect = None

            elif self.moving_item and not QApplication.keyboardModifiers() == Qt.ShiftModifier:
                end_positions = {item: item.pos() for item in self.dragged_items}
                if self.initial_positions != end_positions:
                    command = MoveCommand(self, self.dragged_items, self.initial_positions, end_positions)
                    self.undo_stack.push(command)
            self.moving_item = None

        self.show_items_details()
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Overrides base method"""
        item = self.itemAt(event.scenePos(), QTransform())
        if item:
            if isinstance(item, (AssetItem, EditableTextItem)):
                if isinstance(item, EditableTextItem):
                    # If right-clicked on EditableTextItem, get its parent which is AssetItem
                    item = item.parentItem()
                item.setSelected(True)
                print("Found Asset", item)
                # self.show_asset_context_menu(event.screenPos(), item)
                self.show_asset_context_menu(event.screenPos())

            elif isinstance(item, (AssociationConnectionItem, EntrypointConnectionItem)):
                print("Found Connection Item", item)
                self.show_connection_item_context_menu(event.screenPos(), item)

            elif isinstance(item, AssetsContainer):
                print("Found Assets Container item",item)
                self.show_assets_container_context_menu(event.screenPos(), item)

            elif isinstance(item, AssetsContainerRectangleBox):
                print("Found Assets Container Box",item)
                self.show_assets_container_box_context_menu(event.screenPos(), item)
        else:
            self.show_scene_context_menu(event.screenPos(),event.scenePos())

    def assign_position_to_assets_without_positions(
            self, assets_without_position,x_max,y_max
        ):
        """Assign position to assets that don't have any"""

        distance_between_two_assets_vertically = 200

        for i, asset in enumerate(assets_without_position):
            x_pos = x_max
            y_pos = y_max + (i* distance_between_two_assets_vertically)
            print("In x_pos= "+ str(x_pos))
            print("In y_pos= "+ str(y_pos))
            asset.setPos(QPointF(x_pos,y_pos))

    def draw_model(self):
        """Draw all assets in the model"""

        assets_without_position = []
        x_max = 0
        y_max = 0

        for asset in self.model.assets.values():

            if 'position' in asset.extras:
                pos = QPointF(
                    asset.extras['position']['x'],
                    asset.extras['position']['y']
                )

                # Storing x_max and y_max to be used at the end
                # for moving the assets without position
                if x_max< asset.extras['position']['x']:
                    x_max = asset.extras['position']['x']
                    print("x_max = "+ str(x_max))
                if y_max < asset.extras['position']['y']:
                    y_max = asset.extras['position']['y']
                    print("y_max = "+ str(y_max))

            else:
                pos = QPointF(0,0)

            new_item = self.asset_factory.create_asset_item(asset, pos)
            self._asset_id_to_item[asset.id] = new_item
            self.addItem(new_item)

            # extract assets without position
            if 'position' not in asset.extras:
                assets_without_position.append(new_item)

        self.assign_position_to_assets_without_positions(
            assets_without_position,x_max, y_max
        )

        for asset in self.model.assets.values():
            for fieldname, assets in asset.associated_assets.items():
                for associated_asset in assets:

                    self.add_association_connection(
                        self._asset_id_to_item[asset.id],
                        self._asset_id_to_item[associated_asset.id],
                        fieldname
                    )

        for attacker in self.model.attackers:
            new_item = self.asset_factory.create_attacker_item(
                attacker, QPointF(0,0)
            )
            self._attacker_id_to_item[attacker.id] = new_item
            self.addItem(new_item)

            for (entry_point_asset, entry_point_attack_steps) in attacker.entry_points:
                for attack_step in entry_point_attack_steps:
                    self.add_entrypoint_connection(
                        attack_step,
                        new_item,
                        self._asset_id_to_item[entry_point_asset.id]
                    )


# based on connectionType use attacker or
# add_association_connection

    def add_association_connection(
        self,
        start_item,
        end_item,
        fieldname: str
    ):
        """Add associations to the scene"""

        connection = AssociationConnectionItem(
            fieldname,
            start_item,
            end_item,
            self
        )

        self.addItem(connection)
        connection.restore_labels()
        connection.update_path()
        return connection

    def add_entrypoint_connection(
        self,
        attack_step_name,
        attacker_item,
        asset_item
    ):
        """Add attacker entrypoints to the scene"""

        connection = EntrypointConnectionItem(
            attack_step_name,
            attacker_item,
            asset_item,
            self
        )

        self.addItem(connection)
        connection.restore_labels()
        connection.update_path()
        return connection

    def recreate_asset(
            self,
            asset_item: AssetItem,
            position: QPointF
        ) -> AssetItem:
        """Rebuild existing asset and add to model and scene"""
        # Create new asset from the old asset object
        # and add it to the model
        asset_item.asset = self.model.add_asset(
            asset_type=asset_item.asset.type,
            name=asset_item.asset.name,
            asset_id=asset_item.asset.id,
            defenses=asset_item.asset.defenses,
            extras=asset_item.asset.extras,
        )
        asset_item.setPos(position)
        self.addItem(asset_item)
        self._asset_id_to_item[asset_item.asset.id] = asset_item
        return asset_item

    def create_asset(
            self, asset_type: str, position: QPointF, name=None, asset_id=None
        ) -> AssetItem:
        """Add new asset to model and to scene"""
        new_asset = self.model.add_asset(
            asset_type=asset_type, name=name, asset_id=asset_id
        )
        new_asset_item = self.asset_factory.create_asset_item(
            new_asset, position
        )
        self.addItem(new_asset_item)
        self._asset_id_to_item[new_asset.id] = new_asset_item
        return new_asset_item

    def remove_asset(self, asset_item: AssetItem):
        self.model.remove_asset(asset_item.asset)
        self.removeItem(asset_item)
        del self._asset_id_to_item[asset_item.asset.id]

    def create_attacker(self, position, name = None, attacker_id = None):
        """Add new attacker to the model and scene"""
        new_attacker_attachment = (
            AttackerAttachment(id=attacker_id, name=name)
        )
        self.model.add_attacker(new_attacker_attachment)
        new_item = self.asset_factory.create_attacker_item(
            new_attacker_attachment, position
        )
        self.addItem(new_item)
        self._attacker_id_to_item[new_attacker_attachment.id] = new_item
        return new_item

    def remove_attacker(self, attacker_item: AttackerItem):
        self.model.remove_attacker(attacker_item.attacker)
        self.removeItem(attacker_item)
        del self._attacker_id_to_item[attacker_item.attacker.id]

    def cut_assets(self, selected_assets: list[AssetItem]):
        print("Cut Asset is called..")
        command = CutCommand(self, selected_assets, self.clipboard)
        self.undo_stack.push(command)

    def copy_assets(self, selected_assets: list[AssetItem]):
        print("Copy Asset is called..")
        command = CopyCommand(self, selected_assets, self.clipboard)
        self.undo_stack.push(command)

    def paste_assets(self, position):
        print("Paste is called")
        command = PasteCommand(self, position, self.clipboard)
        self.undo_stack.push(command)

    def delete_assets(self, selected_assets: list[AssetItem]):
        print("Delete asset is called..")
        command = DeleteCommand(self, selected_assets)
        self.undo_stack.push(command)

    def containerize_assets(self, selected_assets: list[AssetItem]):
        print("Containerization of assets requested..")
        command = ContainerizeAssetsCommand(self,selected_assets)
        self.undo_stack.push(command)

    def decontainerize_assets(self, currently_selected_container: AssetsContainer):
        # Add items back to the scene
        current_position_of_container = currently_selected_container.scenePos()
        available_connections_in_item: list[IConnectionItem] = []

        for item_entry in currently_selected_container.containerized_assets_list:
            item: AssetItem = item_entry['item']
            original_position_of_item = current_position_of_container  + item_entry['offset']
            self.addItem(item)
            item.setPos(original_position_of_item)

            if hasattr(item, 'connections'):
                available_connections_in_item.extend(item.connections.copy())

        # Restore connections
        for connection in available_connections_in_item:
            self.addItem(connection)
            connection.restore_labels()
            connection.update_path()

        self.removeItem(currently_selected_container)

    def expand_container(self, currently_selected_container):
        """Expand container, move the assets out of it"""
        contained_item_for_bounding_rect_calc = []

        #copied below logic from containerize_assetsCommandUndo

        current_centroid_position_of_container = \
            currently_selected_container.scenePos()

        for item_entry in currently_selected_container.containerized_assets_list:
            item = item_entry['item']
            offset_position_of_item = \
                current_centroid_position_of_container + item_entry['offset']
            self.addItem(item)
            item.setPos(offset_position_of_item)

            # Update connections so association lines are visible properly
            self.update_connections(item)

            #Store the item in a list for later bounding rect calculation
            contained_item_for_bounding_rect_calc.append(item)

        # # Restore connections - Avoiding this because container and asset
        #  may be connected and may get duplicated - So its Future Work
        # for connection in self.connections:
        #     self.scene.addItem(connection)
        #     connection.restore_labels()
        #     connection.update_path()

        rectangle_bounding_all_containerized_assets = self\
            .calc_surrounding_rect_for_grouped_assets_in_container(
                contained_item_for_bounding_rect_calc
            )

        self.container_box = AssetsContainerRectangleBox(
            rectangle_bounding_all_containerized_assets
        )

        self.addItem(self.container_box)
        self.container_box.associatied_compressed_container = \
            currently_selected_container
        # self.removeItem(currently_selected_container)
        currently_selected_container.setVisible(False)

        #MAKE COMPRESSED CONTAINER BOX HEADER FOR EXPANDED CONTAINER BOX - START

        # currently_selected_container.setVisible(True)
        # containerBoxRect = self.container_box.rect()
        # new_pos = QPointF(containerBoxRect.left(), containerBoxRect.top() - currently_selected_container.boundingRect().height())
        # currently_selected_container.setPos(new_pos)
        # currentlySelectedContainerWidth = containerBoxRect.width()
        # currently_selected_container.setScale(currentlySelectedContainerWidth / currently_selected_container.boundingRect().width())

        #MAKE COMPRESSED CONTAINER BOX HEADER FOR EXPANDED CONTAINER BOX - END

    def compress_container(self,currently_selected_container_box):
        compressed_container = \
            currently_selected_container_box.associatied_compressed_container
        current_centroid_position_of_container = compressed_container.scenePos()
        for item_entry in compressed_container.containerized_assets_list:
            item = item_entry['item']
            item.setPos(current_centroid_position_of_container)
            self.update_connections(item)
        compressed_container.setVisible(True)

        self.removeItem(currently_selected_container_box)

    def serialize_entrypoints(
            self,
            entrypoints: list[IConnectionItem],
            selected_ids: set[int]
    ):
        """Serialize selected attacker entrypoints"""

        serialized_entrypoints = []
        for conn in entrypoints:
            # Copy entrypoints where both item are selected
            if not isinstance(conn, EntrypointConnectionItem):
                continue

            # If entry points
            both_items_selected = (
                conn.asset_item.asset.id\
                    in selected_ids and
                conn.attacker_item.attacker.id \
                    in selected_ids
            )
            if not both_items_selected:
                continue

            serialized_entrypoints.append(
                (
                    conn.attacker_item.attacker.id,
                    conn.asset_item.asset.id,
                    conn.attack_step_name
                )
            )

        return serialized_entrypoints

    def serialize_graphics_items(self, items: list[ItemBase], cut_intended):
        """Serialize all selected items"""
        serialized_items = []

        # Set of selected item IDs
        selected_attacker_ids = {
            item.attacker.id for item
            in items if isinstance(item, AttackerItem)
            and item.attacker.id is not None
        }

        selected_asset_ids = {
            item.asset.id for item
            in items if isinstance(item, AssetItem)
            and item.asset.id is not None
        }

        selected_ids = selected_attacker_ids | selected_asset_ids

        for item in items:
            item_id = None
            if isinstance(item, AssetItem):
                item_id = item.asset.id
            if isinstance(item, AttackerItem):
                item_id = item.attacker.id

            item_details = {
                'title': item.title,
                'id': item_id,
                'position': (item.pos().x(), item.pos().y()),
            }

            if isinstance(item, AttackerItem):
                item_details['type'] = "attacker"
                item_details['entrypoints'] = self.serialize_entrypoints(
                    item.connections, selected_ids
                )
            elif isinstance(item, AssetItem):
                item_details['type'] = "asset"
                item_details['properties'] = next(
                    iter(item.asset._to_dict().values())
                )

            serialized_items.append(item_details)

        serialized_data = pickle.dumps(serialized_items)
        base64_serialized_data = \
            base64.b64encode(serialized_data).decode('utf-8')
        return base64_serialized_data

    def deserialize_graphics_items(self, asset_text):
        # Fix padding if necessary - I was getting padding error
        padding_needed = len(asset_text) % 4
        if padding_needed:
            asset_text += '=' * (4 - padding_needed)

        serialized_data = base64.b64decode(asset_text)
        deserialized_data = pickle.loads(serialized_data)

        return deserialized_data

    def delete_connection(self, connection_item_to_be_deleted):
        print("Delete Connection is called..")
        command = DeleteConnectionCommand(self, connection_item_to_be_deleted)
        self.undo_stack.push(command)

    def show_asset_context_menu(self, position):
        print("Asset Context menu activated")
        menu = QMenu()
        asset_cut_action = QAction("Cut Asset", self)
        asset_copy_action = QAction("Copy Asset", self)
        asset_delete_action = QAction("Delete Asset", self)
        asset_containerization_action = QAction("Group Asset(s)", self)

        menu.addAction(asset_cut_action)
        menu.addAction(asset_copy_action)
        menu.addAction(asset_delete_action)
        menu.addAction(asset_containerization_action)
        action = menu.exec(position)

        selected_items = self.selectedItems()  # Get all selected items

        if action == asset_cut_action:
            self.cut_assets(selected_items)
        if action == asset_copy_action:
            self.copy_assets(selected_items)
        if action == asset_delete_action:
            self.delete_assets(selected_items)
        if action == asset_containerization_action:
            self.containerize_assets(selected_items)

    def show_connection_item_context_menu(self, position, connection_item):
        print("AssociationConnectionItem Context menu activated")
        menu = QMenu()
        print("Deleting connection")
        connection_item_delete_action = QAction("Delete Connection", self)

        menu.addAction(connection_item_delete_action)
        action = menu.exec(position)

        #In future we may want more option. So "if" condition.
        if action == connection_item_delete_action:
            self.delete_connection(connection_item)

    def show_assets_container_context_menu(
            self, position, currently_selected_container
        ):
        print("Assets Container Context menu activated")
        menu = QMenu()
        assets_ungroup_action = QAction("Ungroup Asset(s)", self)
        assets_expand_container_action = QAction("Expand Container", self)

        menu.addAction(assets_ungroup_action)
        menu.addAction(assets_expand_container_action)
        action = menu.exec(position)

        if action == assets_ungroup_action:
            self.decontainerize_assets(currently_selected_container)
        elif action == assets_expand_container_action:
            self.expand_container(currently_selected_container)

    def show_assets_container_box_context_menu(
            self, position,currently_selected_container_box
        ):
        print("Assets Container Box Context menu activated")
        menu = QMenu()
        assets_compress_container_box_action = \
            QAction("Compress Container Box", self)
        menu.addAction(assets_compress_container_box_action)

        action = menu.exec(position)

        if action == assets_compress_container_box_action:
            self.compress_container(currently_selected_container_box)

    def show_scene_context_menu(self, screenPos, scene_pos):
        print("Scene Context menu activated")
        menu = QMenu()
        asset_paste_action = menu.addAction("Paste Asset")
        action = menu.exec(screenPos)

        if action == asset_paste_action:
            # self.requestpasteAsset.emit(scene_pos)
            self.paste_assets(scene_pos)

    def set_show_assoc_checkbox_status(self, is_enabled):
        self.show_association_checkbox_status = is_enabled

    def get_show_assoc_checkbox_status(self):
        return self.show_association_checkbox_status

    def show_items_details(self):
        selected_items = self.selectedItems()
        if len(selected_items) == 1:
            item = selected_items[0]
            if isinstance(item, AssetItem):
                # self.main_window is a reference to main window
                self.main_window.item_details_window\
                    .update_item_details_window(item)
                if item.asset_type == 'Attacker':
                    print("Attacker Selected")
                    self.main_window.update_attack_steps_window(item)
                    self.main_window.update_properties_window(None)
                    self.main_window.update_asset_relations_window(None)
                else:
                    self.main_window.update_properties_window(item)
                    self.main_window.update_attack_steps_window(None)
                    self.main_window.update_asset_relations_window(item)
        else:
            self.main_window.item_details_window\
                .update_item_details_window(None)
            self.main_window.update_properties_window(None)
            self.main_window.update_attack_steps_window(None)
            self.main_window.update_asset_relations_window(None)

    def calc_surrounding_rect_for_grouped_assets_in_container(
            self,
            contained_item_for_bounding_rect_calc
        ):
        """Calculate the surrounding rect for assets in container"""

        if not contained_item_for_bounding_rect_calc:
            return QRectF()

        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        margin = 10.0
        for item in contained_item_for_bounding_rect_calc:
            # Get the item's bounding rectangle in scene coordinates
            item_bounding_rect = item.mapRectToScene(item.boundingRect())

            # Update the bounding box dimensions
            min_x = min(min_x, item_bounding_rect.left())
            max_x = max(max_x, item_bounding_rect.right())
            min_y = min(min_y, item_bounding_rect.top())
            max_y = max(max_y, item_bounding_rect.bottom())

        # Expand the rectangle by the margin on all sides
        min_x -= margin
        max_x += margin
        min_y -= margin
        max_y += margin

        return QRectF(QPointF(min_x, min_y), QPointF(max_x, max_y))

    def update_connections(self, item: AssetItem):
        if hasattr(item, 'connections'):
            for connection in item.connections:
                connection.update_path()
