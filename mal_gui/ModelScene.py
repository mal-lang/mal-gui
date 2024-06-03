from PySide6.QtWidgets import QGraphicsScene, QMenu, QApplication, QGraphicsLineItem,QDialog
from PySide6.QtGui import QCursor, QTransform,QAction
from PySide6.QtCore import QLineF, Qt, QPointF

from ConnectionItem import ConnectionItem
from ConnectionDialog import ConnectionDialog
from ObjectExplorer.AssetBase import AssetBase


class ModelScene(QGraphicsScene):
    def __init__(self,assetFactory):
        super().__init__()
        
        self.assetFactory = assetFactory
        
        self.copiedItem = None
        self.cutItemFlag = False
        
        self.lineItem = None
        self.startItem = None
        self.endItem = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        print("dropEvent")
        if event.mimeData().hasFormat('text/plain'):
            print("format is text/plain")
            itemType = event.mimeData().text()
            print("dropped item type = "+ itemType)
            pos = event.scenePos()
            
            newItem = self.assetFactory.getAsset(itemType)
            
            newItem.setPos(pos)
            self.addItem(newItem)
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if item is None:
            menu = QMenu()
            pasteAction = menu.addAction("Paste Item")
            action = menu.exec(QCursor.pos())  # Use QCursor.pos() to get global position
            if action == pasteAction:
                self.pasteItem(event.scenePos())
        else:
            super().contextMenuEvent(event)

    def copyIitem(self, item):
        pass

    def cutItem(self, item):
        pass

    def pasteItem(self, position):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Press event")
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, AssetBase):
                self.startItem = item
                self.lineItem = QGraphicsLineItem()
                self.lineItem.setLine(QLineF(event.scenePos(), event.scenePos()))
                self.addItem(self.lineItem)
                print(f"Start item set: {self.startItem}")
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.lineItem and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Move event")
            self.lineItem.setLine(QLineF(self.lineItem.line().p1(), event.scenePos()))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.lineItem and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Entered Release with Shift")
            print("Scene Mouse Release event")
            
            # Temporarily remove the line item to avoid interference
            self.removeItem(self.lineItem)
            
            item = self.itemAt(event.scenePos(), QTransform())
            print(f"item is: {item}")
            if isinstance(item, AssetBase) and item != self.startItem:
                print(f"End item found: {item}")
                self.endItem = item
                
                # Create and show the connection dialog
                dialog = ConnectionDialog(self.startItem, self.endItem)
                if dialog.exec() == QDialog.Accepted:
                    selectedItem = dialog.associationListWidget.currentItem()
                    if selectedItem:
                        print("Selected Association Text is: "+ selectedItem.text())
                        connection = ConnectionItem(selectedItem.text(),self.startItem, self.endItem,self)
                        self.addItem(connection)
                    else:
                        self.removeItem(self.lineItem)
                
                
            else:
                print("No end item found")
                self.removeItem(self.lineItem)
            self.lineItem = None
            self.startItem = None
            self.endItem = None
        else:
            super().mouseReleaseEvent(event)
