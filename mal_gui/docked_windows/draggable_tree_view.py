from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QPushButton, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import QMimeData, QEvent
from PySide6.QtGui import QDrag, QIcon, QResizeEvent

from .style_configuration import (
    Visibility,
    CustomDialog,
    CustomDialogGlobal,
)

if TYPE_CHECKING:
    from ..object_explorer.asset_item import AssetItem

class DraggableTreeView(QTreeWidget):
    def __init__(
            self,
            scene,
            eye_unhide_icon,
            eve_hide_icon,
            rgb_color_icon
        ):

        super().__init__()
        self.scene = scene
        self.eye_visibility = Visibility.UNHIDE
        self.eye_unhide_icon = eye_unhide_icon
        self.eve_hide_icon = eve_hide_icon
        self.rgb_color_icon = rgb_color_icon

        self.setHeaderHidden(True)  # Hide the header
        self.setColumnCount(3)  # Two columns: one for text and one for button
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        # Set default column widths
        self.setColumnWidth(0, 1)  # Placeholder for text column
        self.setColumnWidth(1, 40)  # Width for the left button column
        self.setColumnWidth(2, 40)  # Width for the right button column

        # Connect the signal to adjust column widths
        # when the tree widget is resized
        self.viewport().installEventFilter(self)

    def startDrag(self, supported_actions):
        """Overrides base method"""
        item = self.currentItem()
        if item and item.parent() is None:  # Only start drag if the item is a top-level item (parent)
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(item.text(0))
            drag.setMimeData(mime_data)
            drag.exec(supported_actions)

    def resizeEvent(self, event: QResizeEvent):
        """Overrides base method"""
        super().resizeEvent(event)

        # Calculate and set the widths based on percentages
        tree_width = self.viewport().width()
        button_width = 0.2 * tree_width  # 20% of total width

        # Remaining width for text column
        text_width = tree_width - button_width

        # self.setColumnWidth(0, text_width)  # Set width for text column
        # self.setColumnWidth(1, button_width)  # Set width for button column

        # Adjust the width of all buttons in the tree
        # self.adjust_button_width()

        left_eye_button_width = 0.50 * button_width
        right_color_button_width = 0.50 * button_width

        # Set width for text column and left, right button column
        self.setColumnWidth(0, text_width)
        self.setColumnWidth(1, left_eye_button_width)
        self.setColumnWidth(2, right_color_button_width)

    def eventFilter(self, source, event):
        """Overrides base"""
        if event.type() == QEvent.Resize and source == self.viewport():
            self.resizeEvent(event)
        return super().eventFilter(source, event)

    def set_parent_item_text(self, text, icon=None):
        # Create item with placeholder for button
        parent_item = QTreeWidgetItem([text, ""])
        if icon:
            parent_item.setIcon(0, QIcon(icon))
        self.addTopLevelItem(parent_item)
        self.add_button_to_item(parent_item,"",is_parent=True)
        return parent_item

    def add_child_item(self, parent_item, child_item_asset, text):
        # Create item with placeholder for button
        child_item = QTreeWidgetItem([text, ""])
        child_item.assetItemReference = child_item_asset
        parent_item.addChild(child_item)
        self.add_button_to_item(child_item,"",is_parent=False)
        return child_item

    def add_button_to_item(self, item, text, is_parent, icon_path=None):
        # button = QPushButton(text)
        # if icon_path:
        #     button.setIcon(QIcon(icon_path))
        if is_parent:
            button = QPushButton(text)
            button.setIcon(QIcon(self.rgb_color_icon))
            button.clicked.connect(lambda: self.show_global_asset_edit_form(item))
            # Place the button in the second column
            self.setItemWidget(item, 2, button)
            # self.adjust_button_width()
        else:
            left_eye_button = QPushButton(text)
            left_eye_button.setIcon(QIcon(self.eye_unhide_icon))
            left_eye_button.clicked.connect(
                lambda: self.hide_unhide_asset_item(left_eye_button, item))
            # Place the left button in the second column
            self.setItemWidget(item, 1, left_eye_button)

            right_color_button = QPushButton(text)
            right_color_button.setIcon(QIcon(self.rgb_color_icon))
            right_color_button.clicked.connect(
                lambda: self.show_local_asset_edit_form(item))
            # Place the right button in the third column
            self.setItemWidget(item, 2, right_color_button)

    def hide_unhide_asset_item(self, eye_button, item):
        if self.eye_visibility == Visibility.UNHIDE:
            self.eye_visibility = Visibility.HIDE

            #First Hide the connections associtaed with the asset item
            asset_item: AssetItem = item.assetItemReference

            if hasattr(asset_item, 'connections'):
                connections = asset_item.connections
                for connection in connections:
                    connection.remove_labels()
                    connection.setVisible(False)

            #Then hide the asset item itself
            asset_item.setVisible(False)

            eye_button.setIcon(QIcon(self.eve_hide_icon))
        else:
            self.eye_visibility = Visibility.UNHIDE

            #First unhide the connections associtaed with the asset item
            asset_item = item.assetItemReference

            if hasattr(asset_item, 'connections'):
                connections = asset_item.connections
                for connection in connections:
                    connection.restore_labels()
                    connection.setVisible(True)

            #Then unhide the asset item itself
            asset_item.setVisible(True)


            eye_button.setIcon(QIcon(self.eye_unhide_icon))

    def adjust_button_width(self):
        """Adjust the width of all buttons in the tree"""
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            button = self.itemWidget(top_item, 1)
            if button:
                # Set button width to match the column width
                button.setFixedWidth(self.columnWidth(1))
            for j in range(top_item.childCount()):
                child_item = top_item.child(j)
                button = self.itemWidget(child_item, 1)
                if button:
                    # Set button width to match the column width
                    button.setFixedWidth(self.columnWidth(1))

    # def showEditForm(self, item):
    #     dialog = CustomDialog(item, self)
    #     if dialog.exec() == QDialog.Accepted:
    #         item.setText(0, dialog.get_name())
    #         if dialog.get_color_1():
    #             item.setBackground(0, dialog.get_color_1())
    #         if dialog.get_color_2():
    #             item.setBackground(1, dialog.get_color_2())
    #         font1 = dialog.getFont1()
    #         if font1:
    #             item.setFont(0, QFont(font1))
    #         font2 = dialog.getFont2()
    #         if font2:
    #             item.setFont(1, QFont(font2))


    def update_color_callback(self, color1, color2):
        item = self.selected_item
        item.asset_type_background_color = color1
        item.asset_name_background_color = color2
        print(f"RGB Color1: {color1.red()}, {color1.green()}, {color1.blue()}")
        print(f"RGB Color2: {color2.red()}, {color2.green()}, {color2.blue()}")

    def show_local_asset_edit_form(self, item):
        self.selected_item = item
        self.dialog = CustomDialog(item, self.update_color_callback)
        self.dialog.exec()

    def show_global_asset_edit_form(self, item):
        # self.globalAssetStyleHandlerDialog(self.scene)
        # print("globalAssetStyleHandlerDialog executing")
        # self.globalAssetStyleHandlerDialog.exec()
        self.dialog = CustomDialogGlobal(self.scene,item)
        self.dialog.exec()

    def check_and_get_if_parent_asset_type_exists(self, child_asset_type):
        for i in range(self.topLevelItemCount()):
            parent_item = self.topLevelItem(i)
            if parent_item.text(0) == child_asset_type:
                return parent_item,child_asset_type
        return None, None

    def remove_children(self, parent_item):
        while parent_item.childCount() > 0:
            parent_item.takeChild(0)

    def clear_all_object_explorer_child_items(self):
        for i in range(self.topLevelItemCount()):
            parent_item = self.topLevelItem(i)
            self.remove_children(parent_item)
            # parent_item.removeChild()
