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

from .ConnectionItem import AssociationConnectionItem,EntrypointConnectionItem
from .ConnectionDialog import AssociationConnectionDialog,EntrypointConnectionDialog
from .ObjectExplorer.AssetBase import AssetBase
from .ObjectExplorer.EditableTextItem import EditableTextItem
from .AssetsContainer.AssetsContainer import AssetsContainer
from .AssetsContainer.AssetsContainerRectangleBox import AssetsContainerRectangleBox

from .UndoRedoCommands.CutCommand import CutCommand
from .UndoRedoCommands.CopyCommand import CopyCommand
from .UndoRedoCommands.PasteCommand import PasteCommand
from .UndoRedoCommands.DeleteCommand import DeleteCommand
from .UndoRedoCommands.MoveCommand import MoveCommand
from .UndoRedoCommands.DragDropCommand import DragDropCommand
from .UndoRedoCommands.CreateAssociationConnectionCommand import CreateAssociationConnectionCommand
from .UndoRedoCommands.CreateEntrypointConnectionCommand import CreateEntrypointConnectionCommand
from .UndoRedoCommands.DeleteConnectionCommand import DeleteConnectionCommand
from .UndoRedoCommands.ContainerizeAssetsCommand import ContainerizeAssetsCommand

from maltoolbox.model import Model, AttackerAttachment

if TYPE_CHECKING:
    from MainWindow import MainWindow
    from maltoolbox.language import LanguageGraph

class ModelScene(QGraphicsScene):
    def __init__(
            self,
            asset_factory,
            lang_graph: LanguageGraph,
            lcs,
            model: Model,
            main_window: MainWindow
        ):
        super().__init__()

        self.asset_factory = asset_factory
        self.undo_stack = QUndoStack(self)
        self.clipboard = QApplication.clipboard()
        self.main_window = main_window

        # # Create the MAL language graph, language classes factory, and
        # # instance model
        # self.lang_graph = LanguageGraph.from_mar_archive("langs/org.mal-lang.coreLang-1.0.0.mar")
        # self.lcs = LanguageClassesFactory(self.lang_graph)
        # self.model = Model("Untitled Model", self.lcs)

        # # Assign the MAL language graph, language classes factory, and
        # # instance model
        self.lang_graph = lang_graph
        self.lcs = lcs
        self.model = model

        self._asset_id_to_item = {}
        self._attacker_id_to_item = {}

        self.copied_item = None
        self.cut_item_flag = False

        self.line_item = None
        self.start_item = None
        self.end_item = None

        # self.objdetails = {}

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
            itemType = event.mimeData().text()
            print("dropped item type = "+ itemType)
            pos = event.scenePos()

            if itemType == "Attacker":
                self.add_attacker(pos)
            else:
                self.add_asset(itemType, pos)
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        """Overrides base method"""
        print(event.button())
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Press event")
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, (AssetBase,EditableTextItem)):
                if isinstance(item, EditableTextItem):
                    # If clicked on EditableTextItem, get its parent which is AssetBase
                    asset_item = item.parentItem()
                    if isinstance(asset_item, AssetBase):
                        self.start_item = asset_item
                    else:
                        return  # Ignore clicks on items that are not AssetBase or its EditableTextItem
                else:
                    self.start_item = item
                self.line_item = QGraphicsLineItem()
                self.line_item.setLine(QLineF(event.scenePos(), event.scenePos()))
                self.addItem(self.line_item)
                print(f"Start item set: {self.start_item}")
                return #Fix: Without this return the AssetBaseItem was moving along while drawing line.
        elif event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos(), QTransform())
            if item and isinstance(item, (AssetBase, EditableTextItem,AssetsContainer)):
                if isinstance(item, EditableTextItem):
                    asset_item = item.parentItem()
                    if isinstance(asset_item, AssetBase):
                        item = asset_item
                    else:
                        return
                if item.isSelected():
                    print("Item is already selected")
                    self.moving_item = item
                    self.start_pos = item.pos()
                    self.dragged_items = [i for i in self.selectedItems() if isinstance(i, AssetBase)]
                    self.initial_positions = {i: i.pos() for i in self.dragged_items}
                else:
                    print("Item is not selected")
                    self.clearSelection()
                    item.setSelected(True)
                    self.moving_item = item
                    self.start_pos = item.pos()
                    self.dragged_items = [item]
                    self.initial_positions = {item: item.pos()}
            else:
                self.clearSelection()  # Deselect all items if clicking outside any item
                self.origin = event.scenePos()
                self.selection_rect = QGraphicsRectItem(QRectF(self.origin, self.origin))
                self.selection_rect.setPen(QPen(Qt.blue, 2, Qt.DashLine))
                self.addItem(self.selection_rect)
        elif event.button() == Qt.RightButton:
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            print("Item", item)
            if item and isinstance(item, AssetBase):
                if not item.isSelected():
                    self.clearSelection()
                    item.setSelected(True)

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
        if event.button() == Qt.LeftButton and self.line_item and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Entered Release with Shift")
            print("Scene Mouse Release event")

            # Temporarily remove the line item to avoid interference
            self.removeItem(self.line_item)

            item = self.itemAt(event.scenePos(), QTransform())
            print(f"item is: {item}")
            if isinstance(item, (AssetBase,EditableTextItem)) and item != self.start_item:
                print(f"End item found: {item}")
                if isinstance(item, EditableTextItem):
                    # If clicked on EditableTextItem, get its parent which is AssetBase
                    asset_item = item.parentItem()
                    if isinstance(asset_item, AssetBase):
                        self.end_item = asset_item
                    else:
                        self.end_item = None
                else:
                    self.end_item = item

                # Create and show the connection dialog
                if self.end_item:
                    if self.start_item.assetType != 'Attacker' and self.end_item.assetType != 'Attacker':
                        dialog = AssociationConnectionDialog(self.start_item, self.end_item,self.lang_graph, self.lcs,self.model)
                        if dialog.exec() == QDialog.Accepted:
                            selected_item = dialog.associationListWidget.currentItem()
                            if selected_item:
                                print("Selected Association Text is: "+ selected_item.text())
                                # connection = AssociationConnectionItem(selected_item.text(),self.start_item, self.end_item,self)
                                # self.addItem(connection)
                                command = CreateAssociationConnectionCommand(
                                    self,
                                    self.start_item,
                                    self.end_item,
                                    selected_item.text(),
                                    selected_item.association
                                )
                                self.undo_stack.push(command)
                            else:
                                print("No end item found")
                                self.removeItem(self.line_item)
                    else:

                        if self.start_item.assetType == self.end_item.assetType:
                            raise TypeError("Start and end item can not both be type 'Attacker'")

                        attacker_item = self.start_item if self.start_item.assetType == 'Attacker' else self.end_item
                        asset_item = self.end_item if self.start_item.assetType == 'Attacker' else self.start_item

                        dialog = EntrypointConnectionDialog(
                            attacker_item, asset_item, self.lang_graph, self.lcs,self.model)
                        if dialog.exec() == QDialog.Accepted:
                            selected_item = dialog.attackStepListWidget.currentItem()
                            if selected_item:
                                print("Selected Entrypoint Text is: "+ selected_item.text())
                                command = CreateEntrypointConnectionCommand(
                                    self,
                                    attacker_item,
                                    asset_item,
                                    selected_item.text(),
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
                    if isinstance(item, AssetBase):
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
            if isinstance(item, (AssetBase,EditableTextItem)):
                if isinstance(item, EditableTextItem):
                    # If right-clicked on EditableTextItem, get its parent which is AssetBase
                    item = item.parentItem()
                item.setSelected(True)
                print("Found Asset", item)
                # self.show_asset_context_menu(event.screenPos(), item)
                self.show_asset_context_menu(event.screenPos())
            elif isinstance(item, (AssociationConnectionItem,EntrypointConnectionItem)):
                print("Found Connection Item", item)
                self.show_connection_item_context_menu(event.screenPos(), item)
            elif isinstance(item,AssetsContainer):
                print("Found Assets Container item",item)
                self.show_assets_container_context_menu(event.screenPos(), item)
            elif isinstance(item,AssetsContainerRectangleBox):
                print("Found Assets Container Box",item)
                self.show_assets_container_box_context_menu(event.screenPos(), item)
        else:
            self.show_scene_context_menu(event.screenPos(),event.scenePos())

    def add_asset(self, itemType, position, name = None):
        new_asset = getattr(self.lcs.ns, itemType)(name = name)
        self.model.add_asset(new_asset)
        # new_asset.extras = {
        #     "position" :
        #     {
        #         "x": position.x(),
        #         "y": position.y()
        #     }
        # }
        new_item = self.create_item(
            itemType,
            position,
            new_asset.name
        )
        new_item.asset = new_asset
        self._asset_id_to_item[new_asset.id] = new_item
        return new_item

    def assign_position_to_assets_without_positions(
            self, assets_without_position,x_max,y_max
        ):
        """
        Assign position to assets that don't have any
        """
        distance_between_two_assets_vertically = 200
        
        for i, asset in enumerate(assets_without_position):  
            x_pos = x_max
            y_pos = y_max + (i* distance_between_two_assets_vertically)
            print("In x_pos= "+ str(x_pos))
            print("In y_pos= "+ str(y_pos))
            asset.setPos(QPointF(x_pos,y_pos))

    def draw_model(self):

        assets_without_position = []
        x_max = 0
        y_max = 0

        for asset in self.model.assets:

            if 'position' in asset.extras:
                pos = QPointF(asset.extras['position']['x'],
                    asset.extras['position']['y'])

                #Storing x_max and y_max to be used at the end for moving the assets without position
                if x_max< asset.extras['position']['x']:
                    x_max = asset.extras['position']['x']
                    print("x_max = "+ str(x_max))
                if y_max < asset.extras['position']['y']:
                    y_max = asset.extras['position']['y']
                    print("y_max = "+ str(y_max))

            else:
                pos = QPointF(0,0)

            new_item = self.create_item(
                asset.type,
                pos,
                asset.name
            )
            new_item.asset = asset
            self._asset_id_to_item[asset.id] = new_item

            # extract assets without position
            if 'position' not in asset.extras:
                assets_without_position.append(new_item)

        self.assign_position_to_assets_without_positions(assets_without_position,x_max, y_max)

        for assoc in self.model.associations:
            lest_field_name, right_field_name = \
                self.model.get_association_field_names(
                    assoc
                )
            left_field = getattr(assoc, lest_field_name)
            right_field = getattr(assoc, right_field_name)

            for left_asset in left_field:
                for right_asset in right_field:
                    assoc_text = str(left_asset.name) + "." + \
                        lest_field_name + "-->" + \
                        assoc.__class__.__name__ + "-->" + \
                        right_asset.name  + "." + \
                        right_field_name

                    self.add_association_connection(
                        assoc_text,
                        self._asset_id_to_item[left_asset.id],
                        self._asset_id_to_item[right_asset.id]
                    )

# based on connectionType use attacker or
# add_association_connection

    def add_association_connection(
        self,
        assoc_text,
        start_item,
        end_item
    ):

        connection = AssociationConnectionItem(
            assoc_text,
            start_item,
            end_item,
            self
        )

        self.addItem(connection)
        connection.restoreLabels()
        connection.updatePath()
        return connection

    def add_entrypoint_connection(
        self,
        attack_step_name,
        attacker_item,
        asset_item
    ):

        connection = EntrypointConnectionItem(
            attack_step_name,
            attacker_item,
            asset_item,
            self
        )

        self.addItem(connection)
        connection.restoreLabels()
        connection.updatePath()
        return connection

    def add_attacker(self, position, name = None):
        newAttackerAttachment = AttackerAttachment()
        self.model.add_attacker(newAttackerAttachment)
        new_item = self.create_item(
            "Attacker",
            position,
            newAttackerAttachment.name
        )
        new_item.attackerAttachment = newAttackerAttachment
        self._attacker_id_to_item[newAttackerAttachment.id] = new_item

    def create_item(self, itemType, position, name):
        new_item = self.asset_factory.getAsset(itemType)
        new_item.assetName = name
        new_item.typeTextItem.setPlainText(str(name))
        new_item.setPos(position)
        # self.addItem(new_item)
        self.undo_stack.push(DragDropCommand(self, new_item))  # Add the drop as a command
        return new_item

    def cut_assets(self, selectedAssets):
        print("Cut Asset is called..")
        command = CutCommand(self, selectedAssets,self.clipboard)
        self.undo_stack.push(command)

    def copy_assets(self, selectedAssets):
        print("Copy Asset is called..")
        command = CopyCommand(self, selectedAssets,self.clipboard)
        self.undo_stack.push(command)

    def paste_assets(self, position):
        print("Paste is called")
        command = PasteCommand(self, position, self.clipboard)
        self.undo_stack.push(command)

    def delete_assets(self, selectedAssets):
        print("Delete asset is called..")
        command = DeleteCommand(self, selectedAssets)
        self.undo_stack.push(command)

    def containerize_assets(self,selectedAssets):
        print("Containerization of assets requested..")
        command = ContainerizeAssetsCommand(self,selectedAssets)
        self.undo_stack.push(command)

    def decontainerize_assets(self,currently_selected_container):
        # Add items back to the scene
        current_position_of_container = currently_selected_container.scenePos()
        available_connections_in_item = []

        for item_entry in currently_selected_container.containerizedAssetsList:
            item = item_entry['item']
            original_position_of_item = current_position_of_container  + item_entry['offset']
            self.addItem(item)
            item.setPos(original_position_of_item)

            if hasattr(item, 'connections'):
                available_connections_in_item.extend(item.connections.copy())

        # Restore connections
        for connection in available_connections_in_item:
            self.addItem(connection)
            connection.restoreLabels()
            connection.updatePath()
            
        self.removeItem(currently_selected_container)

    def expand_container(self,currently_selected_container):
        contained_item_for_bounding_rect_calc = []

        #copied below logic from containerize_assetsCommandUndo

        current_centroid_position_of_container = \
            currently_selected_container.scenePos()

        for item_entry in currently_selected_container.containerizedAssetsList:
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
        #     connection.restoreLabels()
        #     connection.updatePath()

        rectangle_bounding_all_containerized_assets = self\
            .calc_surrounding_rect_for_grouped_assets_in_container(
                contained_item_for_bounding_rect_calc
            )

        self.container_box = AssetsContainerRectangleBox(
            rectangle_bounding_all_containerized_assets
        )

        self.addItem(self.container_box)
        self.container_box.associatedCompressedContainer = currently_selected_container   
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
        compressed_container = currently_selected_container_box.associatedCompressedContainer
        current_centroid_position_of_container = compressed_container.scenePos()
        for item_entry in compressed_container.containerizedAssetsList:
            item = item_entry['item']
            item.setPos(current_centroid_position_of_container)
            self.update_connections(item)
        compressed_container.setVisible(True)

        self.removeItem(currently_selected_container_box)

    def serialize_graphics_items(self, items, cutIntended):
        objdetails = []
        selectedSequenceIds = {item.assetSequenceId for item in items}  # Set of selected item IDs
        for item in items:

            # Convert assetName to a string - This is causing issue with Serialization
            assetNameStr = str(item.assetName)

            propertyKeysToIgnore = ['id','type']

            itemDetails = {
                'assetType': item.assetType,
                'assetName': assetNameStr,
                'assetSequenceId': item.assetSequenceId,
                'position': (item.pos().x(), item.pos().y()),
                'connections': [
                        (conn.start_item.assetSequenceId, conn.end_item.assetSequenceId, '-->'.join(conn.associationDetails))
                        for conn in item.connections
                        if conn.start_item.assetSequenceId in selectedSequenceIds and conn.end_item.assetSequenceId in selectedSequenceIds                    
                    ],
                'assetProperties': [
                    (str(key),str(value))
                    for key,value in item.asset._properties.items()
                    if key not in propertyKeysToIgnore 
                ]
            }
            objdetails.append(itemDetails)

        serializedData = pickle.dumps(objdetails)
        base64SerializedData = base64.b64encode(serializedData).decode('utf-8')
        return base64SerializedData

    def deserialize_graphics_items(self, assetText):
        # Fix padding if necessary- I was getting padding error 
        paddingNeeded = len(assetText) % 4
        if paddingNeeded:
            assetText += '=' * (4 - paddingNeeded)

        serializedData = base64.b64decode(assetText)
        deserializedData = pickle.loads(serializedData)

        return deserializedData

    def deleteConnection(self, conectionItemToBeDeleted):
        print("Delete Connection is called..") 
        command = DeleteConnectionCommand(self, conectionItemToBeDeleted)
        self.undo_stack.push(command)

    def show_asset_context_menu(self, position):
        print("Asset Context menu activated")
        menu = QMenu()
        assetCutAction = QAction("Cut Asset", self)
        assetCopyAction = QAction("Copy Asset", self)
        assetDeleteAction = QAction("Delete Asset", self)
        assetContainerizationAction = QAction("Group Asset(s)", self)

        menu.addAction(assetCutAction)
        menu.addAction(assetCopyAction)
        menu.addAction(assetDeleteAction)
        menu.addAction(assetContainerizationAction)
        action = menu.exec(position)

        selected_items = self.selectedItems()  # Get all selected items

        if action == assetCutAction:
            self.cut_assets(selected_items)
        if action == assetCopyAction:
           self.copy_assets(selected_items)
        if action == assetDeleteAction:
           self.delete_assets(selected_items)
        if action == assetContainerizationAction:
           self.containerize_assets(selected_items)

    def show_connection_item_context_menu(self,position, connectionItem):
        print("AssociationConnectionItem Context menu activated")
        menu = QMenu()
        connectionItemDeleteAction = QAction("Delete Connection", self)

        menu.addAction(connectionItemDeleteAction)
        action = menu.exec(position)

        #In future we may want more option. So "if" condition.
        if action == connectionItemDeleteAction:
            self.deleteConnection(connectionItem)

    def show_assets_container_context_menu(self,position,currently_selected_container):
        print("Assets Container Context menu activated")
        menu = QMenu()
        assetsUngroupAction = QAction("Ungroup Asset(s)", self)
        assetsExpandContainerAction = QAction("Expand Container", self)

        menu.addAction(assetsUngroupAction)
        menu.addAction(assetsExpandContainerAction)
        action = menu.exec(position)

        if action == assetsUngroupAction:
            self.decontainerize_assets(currently_selected_container)
        elif action == assetsExpandContainerAction:
            self.expand_container(currently_selected_container)

    def show_assets_container_box_context_menu(self,position,currently_selected_container_box):
        print("Assets Container Box Context menu activated")
        menu = QMenu()
        assetsCompressContainerBoxAction = QAction("Compress Container Box", self)
        menu.addAction(assetsCompressContainerBoxAction)

        action = menu.exec(position)

        if action == assetsCompressContainerBoxAction:
            self.compress_container(currently_selected_container_box)

    def show_scene_context_menu(self, screenPos,scenePos):
        print("Scene Context menu activated")
        menu = QMenu()
        assetPasteAction = menu.addAction("Paste Asset")
        action = menu.exec(screenPos)

        if action == assetPasteAction:
            # self.requestpasteAsset.emit(scenePos)
            self.paste_assets(scenePos)

    def set_show_assoc_checkbox_status(self,isEnabled):
        self.show_association_checkbox_status = isEnabled

    def get_show_assoc_checkbox_status(self):
        return self.show_association_checkbox_status

    def show_items_details(self):
        selected_items = self.selectedItems()
        if len(selected_items) == 1:
            item = selected_items[0]
            if isinstance(item, AssetBase):
                # self.main_window is a reference to main window
                self.main_window.item_details_window.updateItemDetailsWindow(item)
                if item.assetType == 'Attacker':
                    print("Attacker Selected")
                    self.main_window.updateAttackStepsWindow(item)
                    self.main_window.updatePropertiesWindow(None)
                    self.main_window.updateAssetRelationsWindow(None)
                else:
                    self.main_window.updatePropertiesWindow(item)  
                    self.main_window.updateAttackStepsWindow(None) 
                    self.main_window.updateAssetRelationsWindow(item)     
        else:
            self.main_window.item_details_window.updateItemDetailsWindow(None)
            self.main_window.updatePropertiesWindow(None)
            self.main_window.updateAttackStepsWindow(None)
            self.main_window.updateAssetRelationsWindow(None)

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

    def update_connections(self, item):
        if hasattr(item, 'connections'):
            for connection in item.connections:
                connection.updatePath()
