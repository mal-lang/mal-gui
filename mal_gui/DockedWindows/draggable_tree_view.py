from PySide6.QtWidgets import QPushButton, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import QMimeData, QEvent
from PySide6.QtGui import QDrag, QIcon, QResizeEvent

from .style_configuration import (
    Visibility,
    CustomDialog,
    CustomDialogGlobal,
)

class DraggableTreeView(QTreeWidget):
    def __init__(self,scene,eyeUnHideIcon,eyeHideIcon,rgbColorIcon):
        super().__init__()

        self.scene = scene
        
        self.eyeVisibility = Visibility.UNHIDE
        self.eyeUnhideIcon = eyeUnHideIcon
        self.eyeHideIcon = eyeHideIcon
        self.rgbColorIcon = rgbColorIcon

        self.setHeaderHidden(True)  # Hide the header
        self.setColumnCount(3)  # Two columns: one for text and one for button
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        # Set default column widths
        self.setColumnWidth(0, 1)  # Placeholder for text column
        # self.setColumnWidth(1, 80)  # Fixed width for button column
        self.setColumnWidth(1, 40)  # Width for the left button column
        self.setColumnWidth(2, 40)  # Width for the right button column

        # Connect the signal to adjust column widths when the tree widget is resized
        self.viewport().installEventFilter(self)

    def setParentItemText(self, text, icon=None):
        parentItem = QTreeWidgetItem([text, ""])  # Create item with placeholder for button
        if icon:
            parentItem.setIcon(0, QIcon(icon))
        self.addTopLevelItem(parentItem)
        self.addButtonToItem(parentItem,"",isParent=True)
        return parentItem

    def addChildItem(self, parentItem,childItemAsset, text):
        childItem = QTreeWidgetItem([text, ""])  # Create item with placeholder for button
        childItem.assetItemReference = childItemAsset
        parentItem.addChild(childItem)
        self.addButtonToItem(childItem,"",isParent=False)
        return childItem

    def addButtonToItem(self, item, text, isParent, iconPath=None):
        # button = QPushButton(text)
        # if icon_path:
        #     button.setIcon(QIcon(icon_path))
        if isParent:
            button = QPushButton(text)
            button.setIcon(QIcon(self.rgbColorIcon)) 
            button.clicked.connect(lambda: self.showGlobalAssetEditForm(item))
            self.setItemWidget(item, 2, button)  # Place the button in the second column
            # self.adjustButtonWidth()
        else:
            leftEyeButton = QPushButton(text)
            leftEyeButton.setIcon(QIcon(self.eyeUnhideIcon))
            leftEyeButton.clicked.connect(lambda: self.hideUnhideAssetItem(leftEyeButton, item))
            self.setItemWidget(item, 1, leftEyeButton)  # Place the left button in the second column

            rightColorButton = QPushButton(text)
            rightColorButton.setIcon(QIcon(self.rgbColorIcon))
            rightColorButton.clicked.connect(lambda: self.showLocalAssetEditForm(item))
            self.setItemWidget(item, 2, rightColorButton)  # Place the right button in the third column

    def hideUnhideAssetItem(self, eyeButton, item):
        if self.eyeVisibility == Visibility.UNHIDE:
            self.eyeVisibility = Visibility.HIDE
            
            #First Hide the connections associtaed with the asset item
            assetItem = item.assetItemReference 
            
            if hasattr(assetItem, 'connections'):
                connections = assetItem.connections
                for connection in connections:
                    connection.removeLabels()
                    connection.setVisible(False) 
                    
            #Then hide the asset item itself
            assetItem.setVisible(False)
            
            eyeButton.setIcon(QIcon(self.eyeHideIcon)) 
        else:
            self.eyeVisibility = Visibility.UNHIDE
            
            #First unhide the connections associtaed with the asset item
            assetItem = item.assetItemReference
            
            if hasattr(assetItem, 'connections'):
                connections = assetItem.connections
                for connection in connections:
                    connection.restoreLabels()
                    connection.setVisible(True) 
                    
            #Then unhide the asset item itself
            assetItem.setVisible(True)
            
            
            eyeButton.setIcon(QIcon(self.eyeUnhideIcon))

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item and item.parent() is None:  # Only start drag if the item is a top-level item (parent)
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(item.text(0))
            drag.setMimeData(mime_data)
            drag.exec(supportedActions)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        # Calculate and set the widths based on percentages
        tree_width = self.viewport().width()
        button_width = 0.2 * tree_width  # 20% of total width
        text_width = tree_width - button_width  # Remaining width for text column

        # self.setColumnWidth(0, text_width)  # Set width for text column
        # self.setColumnWidth(1, button_width)  # Set width for button column

        # Adjust the width of all buttons in the tree
        # self.adjustButtonWidth()
        
        leftEyeButtonWidth = 0.50 * button_width
        rightColorButtonWidth = 0.50 * button_width
        
        self.setColumnWidth(0, text_width)  # Set width for text column
        self.setColumnWidth(1, leftEyeButtonWidth)  # Set width for left button column
        self.setColumnWidth(2, rightColorButtonWidth)  # Set width for right button column


    def adjustButtonWidth(self):
        # Adjust the width of all buttons in the tree
        for i in range(self.topLevelItemCount()):
            topItem = self.topLevelItem(i)
            button = self.itemWidget(topItem, 1)
            if button:
                button.setFixedWidth(self.columnWidth(1))  # Set button width to match the column width
            for j in range(topItem.childCount()):
                childItem = topItem.child(j)
                button = self.itemWidget(childItem, 1)
                if button:
                    button.setFixedWidth(self.columnWidth(1))  # Set button width to match the column width

    # def showEditForm(self, item):
    #     dialog = CustomDialog(item, self)
    #     if dialog.exec() == QDialog.Accepted:
    #         item.setText(0, dialog.getName())
    #         if dialog.getColor1():
    #             item.setBackground(0, dialog.getColor1())
    #         if dialog.getColor2():
    #             item.setBackground(1, dialog.getColor2())
    #         font1 = dialog.getFont1()
    #         if font1:
    #             item.setFont(0, QFont(font1))
    #         font2 = dialog.getFont2()
    #         if font2:
    #             item.setFont(1, QFont(font2))


    def updateColorCallback(self, color1, color2):
        item = self.selectedItem
        item.assetTypeBackgroundColor = color1
        item.assetNameBackgroundColor = color2
        print(f"RGB Color1: {color1.red()}, {color1.green()}, {color1.blue()}")
        print(f"RGB Color2: {color2.red()}, {color2.green()}, {color2.blue()}")

    def showLocalAssetEditForm(self, item):
        self.selectedItem = item
        self.dialog = CustomDialog(item, self.updateColorCallback)
        self.dialog.exec()
        
    def showGlobalAssetEditForm(self, item):
        # self.globalAssetStyleHandlerDialog(self.scene)
        # print("globalAssetStyleHandlerDialog executing")
        # self.globalAssetStyleHandlerDialog.exec()
        
        self.dialog = CustomDialogGlobal(self.scene,item)
        self.dialog.exec()


    def eventFilter(self, source, event):
        if event.type() == QEvent.Resize and source == self.viewport():
            self.resizeEvent(event)
        return super().eventFilter(source, event)

    def checkAndGetIfParentAssetTypeExists(self, childAssetType):
        for i in range(self.topLevelItemCount()):
            parentItem = self.topLevelItem(i)
            if parentItem.text(0) == childAssetType:
                return parentItem,childAssetType
        return None,None

    def removeChildren(self,parentItem):
        while parentItem.childCount() > 0:
            parentItem.takeChild(0)
    
    def clearAllObjectExplorerChildItems(self):
        for i in range(self.topLevelItemCount()):
            parentItem = self.topLevelItem(i)
            self.removeChildren(parentItem)
            # parentItem.removeChild()