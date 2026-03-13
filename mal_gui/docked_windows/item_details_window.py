from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt

from ..object_explorer import ItemBase

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox


class EnumDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        choices = index.data(Qt.UserRole + 1)
        if not choices:
            return super().createEditor(parent, option, index)

        combo = QComboBox(parent)
        combo.addItems(choices)
        combo.setEditable(True)  # enables typing + autocomplete
        combo.setInsertPolicy(QComboBox.NoInsert)
        return combo

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            value = index.data(Qt.EditRole)
            i = editor.findText(value)
            if i >= 0:
                editor.setCurrentIndex(i)
            return
        super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
            return
        super().setModelData(editor, model, index)


class ItemDetailsWindow(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["Attribute", "Value"])

        self._current_object = None
        self.setItemDelegateForColumn(1, EnumDelegate())
        self.itemChanged.connect(self._on_item_changed)

    def update_item_details_window(self, item_object):
        self.blockSignals(True)
        self.clear()
        self._current_object = item_object

        if item_object:
            asset_details = item_object.get_item_attribute_values()

            for attr_name, meta in asset_details.items():
                value = meta["value"]
                editable = meta.get("editable", False)
                choices = meta.get("choices")

                item = QTreeWidgetItem([attr_name, str(value)])
                item.setData(0, Qt.UserRole, attr_name)

                if choices:
                    item.setData(1, Qt.UserRole + 1, choices)

                if editable:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                self.addTopLevelItem(item)

        self.blockSignals(False)

    def _on_item_changed(self, item, column):
        if not self._current_object or column != 1:
            return

        attr_name = item.data(0, Qt.UserRole)
        new_value = item.text(1)
        self._current_object.set_item_attribute_value(attr_name, new_value)