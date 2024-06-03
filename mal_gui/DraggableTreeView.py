from PySide6.QtWidgets import QTreeView, QAbstractItemView
from PySide6.QtCore import Qt, QMimeData, QModelIndex
from PySide6.QtGui import QDrag, QStandardItemModel, QStandardItem,QIcon

class DraggableTreeView(QTreeView):
    def __init__(self):
        super().__init__()


        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setHeaderHidden(True)  # Hide the header, otherwise shows as '1' on top

        self.model = QStandardItemModel()
        self.setModel(self.model)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.model.itemFromIndex(index)
            if item is not None:
                if event.button() == Qt.LeftButton:
                    drag = QDrag(self)
                    mime_data = QMimeData()
                    print("item dragged is:"+ item.text())
                    mime_data.setText(item.text())
                    drag.setMimeData(mime_data)
                    drag.exec(Qt.MoveAction)
                    return
        super().mousePressEvent(event)

    def setParentItemText(self, text,icon=None):
        existingItems = self.model.findItems(text)
        if not existingItems:
            parentItem = QStandardItem(text)
            if icon:
                parentItem.setIcon(QIcon(icon))
            parentItem.setFlags(parentItem.flags() & ~Qt.ItemIsEditable)
            self.model.appendRow(parentItem)

    def addChildItem(self, parentText, childText):
        # Ensure the parent item exists
        existingItems = self.model.findItems(parentText)
        if not existingItems:
            self.setParentItemText(parentText)
            existingItems = self.model.findItems(parentText)
        
        parentItem = existingItems[0]
        childItem = QStandardItem(childText)
        childItem.setFlags(childItem.flags() | Qt.ItemIsDragEnabled & ~Qt.ItemIsEditable)
        parentItem.appendRow(childItem)