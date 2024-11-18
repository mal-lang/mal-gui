
from PySide6.QtWidgets import QTreeWidget,QTreeWidgetItem
        
class ItemDetailsWindow(QTreeWidget):
    def __init__(self, parent=None):
        super(ItemDetailsWindow, self).__init__(parent)
        self.setHeaderLabel(None)
        self.setColumnCount(2)
        self.setHeaderLabels(["Attribute","Value"])
        
    def updateItemDetailsWindow(self, assetItem):
        self.clear()

        if assetItem is not None:
            assetDetails = assetItem.getItemAttributeValues()  # item has a method that returns a dict
            for (key, value) in assetDetails.items():
                print(f"Attribute:{key} Value:{str(value)}")
                item = QTreeWidgetItem([key, str(value)])
                self.addTopLevelItem(item)
                
        self.show()
        