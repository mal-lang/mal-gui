from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QPointF, QTimer

from ..object_explorer.asset_item import AssetItem
from ..assets_container.assets_container import AssetsContainer
from ..file_utils import image_path

if TYPE_CHECKING:
    from ..connection_item import IConnectionItem

class ContainerizeAssetsCommand(QUndoCommand):
    def __init__(self, scene, items, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items: list[AssetItem] = \
            [item for item in items if item.asset_type != 'Attacker']
        self.connections: list[IConnectionItem] = []
        self.centroid = QPointF(0,0)

        #Timer specific values for animation
        self.animation_duration = 2000 # in milliseconds
        self.animation_timer_interval = 20 # in milliseconds
        self.num_steps_for_animation = \
            self.animation_duration // self.animation_timer_interval

        # Save connections of all items
        for item in self.items:
            if hasattr(item, 'connections'):
                self.connections.extend(item.connections.copy())

        self.new_assets_container = AssetsContainer(
            "AssetContainer",
            "ContainerName",
            image_path("assetContainer.png"),
            image_path("assetContainerPlusSymbol.png"),
            image_path("assetContainerMinusSymbol.png")
        )
        self.new_assets_container.build()

    def redo(self):
        """Perform containerization"""
        # Find the centroid of all Assets to be containerized
        x_coords_list_of_assets = [item.scenePos().x() for item in self.items]
        y_coords_list_of_assets = [item.scenePos().y() for item in self.items]
        center_x = sum(x_coords_list_of_assets) / len(x_coords_list_of_assets)
        center_y = sum(y_coords_list_of_assets) / len(y_coords_list_of_assets)
        self.centroid = QPointF(center_x, center_y)

        #Display the container at centroid location
        self.scene.addItem(self.new_assets_container)
        self.new_assets_container.setPos(self.centroid)

        for item in self.items:
            if isinstance(item,AssetItem):
                self.move_item_from_current_position_to_centroid(
                    item, self.centroid
                )

    def undo(self):
        """Undo containerization"""
        # Add items back to the scene
        for item_entry in self.new_assets_container.containerized_assets_list:
            item = item_entry['item']
            original_position_of_item = self.centroid + item_entry['offset']
            self.scene.addItem(item)
            item.setPos(original_position_of_item)

        # Restore connections
        for connection in self.connections:
            self.scene.addItem(connection)
            connection.restore_labels()
            connection.update_path()

        self.scene.removeItem(self.new_assets_container)

    def update_item_position(self, item,  start_pos, end_pos, is_redo):
        if item.step_counter >= self.num_steps_for_animation:
            item.timer.timeout.disconnect()
            item.timer.stop()
            if is_redo:
                #Store item and offset because items moving towards centroid
                self.new_assets_container.containerized_assets_list.append(
                    {'item': item, 'offset': item.offsetFromCentroid})
                item.setPos(self.centroid)
                self.update_connections(item)

                self.new_assets_container.item_moved = \
                    self.update_items_positions_relative_to_container
            else:
                self.new_assets_container.containerized_assets_list.clear()
            return

        delta_x = (end_pos.x() - start_pos.x()) / self.num_steps_for_animation
        delta_y = (end_pos.y() - start_pos.y()) / self.num_steps_for_animation
        new_pos = QPointF(start_pos.x() + delta_x, start_pos.y() + delta_y)
        item.setPos(new_pos)

        item.step_counter += 1

    def move_item_from_current_position_to_centroid(self,item,centroid):
        item.timer = QTimer()
        item.step_counter = 0
        item.offsetFromCentroid = item.scenePos() - centroid
        item.timer.timeout.connect(
            lambda: self.update_item_position(
                item, item.scenePos(),centroid,is_redo=True
            )
        )
        item.timer.start(self.animation_timer_interval)

    def update_connections(self, item: AssetItem):
        if hasattr(item, 'connections'):
            for connection in item.connections:
                connection.update_path()

    def update_items_positions_relative_to_container(self):
        for item_entry in self.new_assets_container.containerized_assets_list:
            item = item_entry['item']
            item.setPos(self.new_assets_container.pos())
