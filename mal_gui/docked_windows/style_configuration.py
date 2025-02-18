from enum import Enum

from PySide6.QtWidgets import (
    QPushButton,
    QDialog,
    QLineEdit,
    QColorDialog,
    QFormLayout,
    QDialogButtonBox,
    QLabel
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor

from ..object_explorer.asset_item import AssetItem

class Visibility(Enum):
    HIDE = 1
    UNHIDE = 2

class CustomDialog(QDialog):
    color_changed_1 = Signal(QColor)
    color_changed_2 = Signal(QColor)

    def __init__(self, item, update_color_callback, parent=None):
        super().__init__(parent)

        self.update_color_callback = update_color_callback
        self.selected_item = item

        self.setWindowTitle("Style Configuration")

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(item.text(0))
        layout.addRow("Name:", self.name_edit)

        self.color_button_1 = QPushButton("Select AssetType background color")
        print("type(self.selected_item.childItemObj) = " +
              str(type(self.selected_item.asset_item_reference)))
        self.color_button_1.setStyleSheet(
            f"background-color: {self.selected_item.asset_item_reference.asset_type_background_color.name()}")
        self.color_button_1.clicked.connect(
            lambda: self.open_color_dialog(1,self.selected_item.asset_item_reference))
        layout.addRow("Color 1:", self.color_button_1)

        self.rgb_label_1 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 1:", self.rgb_label_1)

        self.color_button_2 = QPushButton("Select AssetName background color")
        self.color_button_2.setStyleSheet(
            f"background-color: {self.selected_item.asset_item_reference.asset_name_background_color.name()}")
        self.color_button_2.clicked.connect(
            lambda: self.open_color_dialog(2,self.selected_item.asset_item_reference))
        layout.addRow("Color 2:", self.color_button_2)

        self.rgb_label_2 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 2:", self.rgb_label_2)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

        self.selected_color_1 = QColor(255, 255, 255, 255)
        self.selected_color_2 = QColor(255, 255, 255, 255)
        self.current_color_button = None

        self.color_changed_1.connect(self.update_color_label_1)
        self.color_changed_2.connect(self.update_color_label_2)

    def open_color_dialog(self, item_number, asset_item_reference):
        color = QColorDialog.getColor()

        if color.isValid():
            if item_number == 1:
                self.selected_color_1 = color
                self.current_color_button = self.color_button_1
                self.color_changed_1.emit(self.selected_color_1)
                self.color_button_1.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 1: {color.name()}")
                asset_item_reference.asset_type_background_color = color
                asset_item_reference.update()
            elif item_number == 2:
                self.selected_color_2 = color
                self.current_color_button = self.color_button_2
                self.color_changed_2.emit(self.selected_color_2)
                self.color_button_2.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 2: {color.name()}")
                asset_item_reference.asset_name_background_color = color
                asset_item_reference.update()
        
    def update_color_label_1(self, color):
        self.rgb_label_1.setText(
            f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")
    
    def update_color_label_2(self, color):
        self.rgb_label_2.setText(
            f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")

    def get_name(self):
        return self.name_edit.text()

    def get_color_1(self):
        return self.selected_color_1

    def get_color_2(self):
        return self.selected_color_2

    def accept(self):
        super().accept()
        self.update_color_callback(self.get_color_1(), self.get_color_2())




class CustomDialogGlobal(QDialog):
    color_changed_1 = Signal(QColor)
    color_changed_2 = Signal(QColor)

    def __init__(self,scene, item, parent=None):
        super().__init__(parent)
        
        self.scene = scene
        self.selectedAssetType = item

        self.setWindowTitle("Style Configuration")

        layout = QFormLayout(self)

        self.name_edit = QLabel(str(item.text(0)))
        layout.addRow("Name:", self.name_edit)

        self.color_button_1 = QPushButton("Select AssetType background color")
        # print("type(self.selected_item.childItemObj) = "+ str(type(self.selected_item.asset_item_reference)))
        # self.color_button_1.setStyleSheet(f"background-color: {self.selected_item.asset_item_reference.asset_type_background_color.name()}")
        self.color_button_1.clicked.connect(lambda: self.open_color_dialog(1))
        layout.addRow("Color 1:", self.color_button_1)
        
        self.rgb_label_1 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 1:", self.rgb_label_1)


        self.color_button_2 = QPushButton("Select AssetName background color")
        # self.color_button_2.setStyleSheet(f"background-color: {self.selected_item.asset_item_reference.asset_name_background_color.name()}")
        self.color_button_2.clicked.connect(lambda: self.open_color_dialog(2))
        layout.addRow("Color 2:", self.color_button_2)


        self.rgb_label_2 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 2:", self.rgb_label_2)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

        self.selected_color_1 = QColor(255, 255, 255, 255)
        self.selected_color_2 = QColor(255, 255, 255, 255)
        self.current_color_button = None

        self.color_changed_1.connect(self.update_color_label_1)
        self.color_changed_2.connect(self.update_color_label_2)

    def open_color_dialog(self, item_number):
        color = QColorDialog.getColor()

        if color.isValid():
            if item_number == 1:
                self.selected_color_1 = color
                self.current_color_button = self.color_button_1
                self.color_changed_1.emit(self.selected_color_1)
                self.color_button_1.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 1: {color.name()}")

            elif item_number == 2:
                self.selected_color_2 = color
                self.current_color_button = self.color_button_2
                self.color_changed_2.emit(self.selected_color_2)
                self.color_button_2.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 2: {color.name()}")
        
    def update_color_label_1(self, color):
        self.rgb_label_1.setText(f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")
    
    def update_color_label_2(self, color):
        self.rgb_label_2.setText(f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")

    def get_name(self):
        return self.name_edit.text()

    def get_color_1(self):
        return self.selected_color_1

    def get_color_2(self):
        return self.selected_color_2

    def accept(self):
        super().accept()
        # self.update_color_callback(self.get_color_1(), self.get_color_2())
        for item in self.scene.items():
            if isinstance(item, (AssetItem)):
                if item.asset_type == self.selectedAssetType.text(0):
                    item.asset_type_background_color = self.get_color_1()
                    item.asset_name_background_color = self.get_color_2()
                    item.update()