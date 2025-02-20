from PySide6.QtWidgets import QTreeWidget,QTreeWidgetItem

from ..object_explorer import ItemBase

class ItemDetailsWindow(QTreeWidget):
    def __init__(self, parent=None):
        super(ItemDetailsWindow, self).__init__(parent)
        self.setHeaderLabel(None)
        self.setColumnCount(2)
        self.setHeaderLabels(["Attribute","Value"])

    def update_item_details_window(self, item_object: ItemBase):
        self.clear()
        if item_object is not None:
            # item has a method that returns a dict
            asset_details = item_object.get_item_attribute_values()
            for (key, value) in asset_details.items():
                print(f"Attribute:{key} Value:{str(value)}")
                item = QTreeWidgetItem([key, str(value)])
                self.addTopLevelItem(item)

        self.show()
