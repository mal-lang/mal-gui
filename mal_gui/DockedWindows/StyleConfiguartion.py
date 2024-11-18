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

from ..ObjectExplorer.AssetBase import AssetBase

class Visibility(Enum):
    HIDE = 1
    UNHIDE = 2
    
class CustomDialog(QDialog):
    colorChanged1 = Signal(QColor)
    colorChanged2 = Signal(QColor)

    def __init__(self, item,updateColorCallback, parent=None):
        super().__init__(parent)
        
        self.updateColorCallback = updateColorCallback
        self.selectedItem = item

        self.setWindowTitle("Style Configuration")

        layout = QFormLayout(self)

        self.nameEdit = QLineEdit(item.text(0))
        layout.addRow("Name:", self.nameEdit)

        self.colorButton1 = QPushButton("Select AssetType background color")
        print("type(self.selectedItem.childItemObj) = "+ str(type(self.selectedItem.assetItemReference)))
        self.colorButton1.setStyleSheet(f"background-color: {self.selectedItem.assetItemReference.assetTypeBackgroundColor.name()}")
        self.colorButton1.clicked.connect(lambda: self.openColorDialog(1,self.selectedItem.assetItemReference))
        layout.addRow("Color 1:", self.colorButton1)
        
        self.rgbLabel1 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 1:", self.rgbLabel1)


        self.colorButton2 = QPushButton("Select AssetName background color")
        self.colorButton2.setStyleSheet(f"background-color: {self.selectedItem.assetItemReference.assetNameBackgroundColor.name()}")
        self.colorButton2.clicked.connect(lambda: self.openColorDialog(2,self.selectedItem.assetItemReference))
        layout.addRow("Color 2:", self.colorButton2)


        self.rgbLabel2 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 2:", self.rgbLabel2)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)

        self.selectedColor1 = QColor(255, 255, 255, 255)
        self.selectedColor2 = QColor(255, 255, 255, 255)
        self.currentColorButton = None

        self.colorChanged1.connect(self.updateColorLabel1)
        self.colorChanged2.connect(self.updateColorLabel2)

    def openColorDialog(self, itemNumber,assetItemReference):
        color = QColorDialog.getColor()

        if color.isValid():
            if itemNumber == 1:
                self.selectedColor1 = color
                self.currentColorButton = self.colorButton1
                self.colorChanged1.emit(self.selectedColor1)
                self.colorButton1.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 1: {color.name()}")
                assetItemReference.assetTypeBackgroundColor = color
                assetItemReference.update()
            elif itemNumber == 2:
                self.selectedColor2 = color
                self.currentColorButton = self.colorButton2
                self.colorChanged2.emit(self.selectedColor2)
                self.colorButton2.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 2: {color.name()}")
                assetItemReference.assetNameBackgroundColor = color
                assetItemReference.update()
        
    def updateColorLabel1(self, color):
        self.rgbLabel1.setText(f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")
    
    def updateColorLabel2(self, color):
        self.rgbLabel2.setText(f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")

    def getName(self):
        return self.nameEdit.text()

    def getColor1(self):
        return self.selectedColor1

    def getColor2(self):
        return self.selectedColor2

    def accept(self):
        super().accept()
        self.updateColorCallback(self.getColor1(), self.getColor2())




class CustomDialogGlobal(QDialog):
    colorChanged1 = Signal(QColor)
    colorChanged2 = Signal(QColor)

    def __init__(self,scene, item, parent=None):
        super().__init__(parent)
        
        self.scene = scene
        self.selectedAssetType = item

        self.setWindowTitle("Style Configuration")

        layout = QFormLayout(self)

        self.nameEdit = QLabel(str(item.text(0)))
        layout.addRow("Name:", self.nameEdit)

        self.colorButton1 = QPushButton("Select AssetType background color")
        # print("type(self.selectedItem.childItemObj) = "+ str(type(self.selectedItem.assetItemReference)))
        # self.colorButton1.setStyleSheet(f"background-color: {self.selectedItem.assetItemReference.assetTypeBackgroundColor.name()}")
        self.colorButton1.clicked.connect(lambda: self.openColorDialog(1))
        layout.addRow("Color 1:", self.colorButton1)
        
        self.rgbLabel1 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 1:", self.rgbLabel1)


        self.colorButton2 = QPushButton("Select AssetName background color")
        # self.colorButton2.setStyleSheet(f"background-color: {self.selectedItem.assetItemReference.assetNameBackgroundColor.name()}")
        self.colorButton2.clicked.connect(lambda: self.openColorDialog(2))
        layout.addRow("Color 2:", self.colorButton2)


        self.rgbLabel2 = QLabel("RGB: ")
        layout.addRow("RGB Values for Color 2:", self.rgbLabel2)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)

        self.selectedColor1 = QColor(255, 255, 255, 255)
        self.selectedColor2 = QColor(255, 255, 255, 255)
        self.currentColorButton = None

        self.colorChanged1.connect(self.updateColorLabel1)
        self.colorChanged2.connect(self.updateColorLabel2)

    def openColorDialog(self, itemNumber):
        color = QColorDialog.getColor()

        if color.isValid():
            if itemNumber == 1:
                self.selectedColor1 = color
                self.currentColorButton = self.colorButton1
                self.colorChanged1.emit(self.selectedColor1)
                self.colorButton1.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 1: {color.name()}")

            elif itemNumber == 2:
                self.selectedColor2 = color
                self.currentColorButton = self.colorButton2
                self.colorChanged2.emit(self.selectedColor2)
                self.colorButton2.setStyleSheet(f"background-color: {color.name()}")
                # QMessageBox.information(self, "Color Selected", f"Selected color for Item 2: {color.name()}")
        
    def updateColorLabel1(self, color):
        self.rgbLabel1.setText(f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")
    
    def updateColorLabel2(self, color):
        self.rgbLabel2.setText(f"RGB: {color.red()}, {color.green()}, {color.blue()}, {color.alpha()}")

    def getName(self):
        return self.nameEdit.text()

    def getColor1(self):
        return self.selectedColor1

    def getColor2(self):
        return self.selectedColor2

    def accept(self):
        super().accept()
        # self.updateColorCallback(self.getColor1(), self.getColor2())
        for item in self.scene.items():
            if isinstance(item, (AssetBase)):
                if item.assetType == self.selectedAssetType.text(0):
                    item.assetTypeBackgroundColor = self.getColor1()
                    item.assetNameBackgroundColor = self.getColor2()
                    item.update()