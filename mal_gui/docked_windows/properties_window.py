from PySide6.QtCore import Qt, QLocale,QObject
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QLineEdit,
    QStyledItemDelegate,
    QMessageBox,
    QTableWidget,
    QHeaderView
)

class FloatValidator(QDoubleValidator):
    def __init__(self, parent=None):
        super(FloatValidator, self).__init__(0.0, 1.0, 2, parent)
        self.setNotation(QDoubleValidator.StandardNotation)
        
        #Without US Locale, decimal point was not appearing even when typed from keyboard
        self.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

    def validate(self, input, pos):
        if input == "":
            return QDoubleValidator.Intermediate, input, pos
        return super(FloatValidator, self).validate(input, pos)

class EditableDelegate(QStyledItemDelegate):
    def __init__(self, asset_item, parent=None):
        super(EditableDelegate, self).__init__(parent)
        self.asset_item = asset_item

    def createEditor(self, parent, option, index):
        """Overrides base"""
        editor = QLineEdit(parent)
        validator = FloatValidator()
        editor.setValidator(validator)
        editor.editingFinished.connect(self.validate_editor)
        return editor

    def setEditorData(self, editor, index):
        """Overrides base"""
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        """Overrides base"""
        value = editor.text()
        print("Value Entered: "+ value)
        # setattr(selected_item.asset, row[0],value)
        state = editor.validator().validate(value, 0)
        if state[0] != QDoubleValidator.Acceptable:
            QMessageBox.warning(editor, "Input Error", "Value must be a float between 0.0 and 1.0.")
            # Revert to previous valid value (optional)
            # editor.setText(index.model().data(index, Qt.EditRole))
        else:
            model.setData(index, value, Qt.EditRole)
            # Update the attribute in asset_item
            row = index.row()
            # property_key = model.item(row, 0).text()
            property_key = index.sibling(row, 0).data()

            # Set the attribute - Probably this is Andrei's expectation
            self.asset_item.asset.defenses[property_key] = float(value)

    def validate_editor(self):
        editor = self.sender()
        if editor:
            state = editor.validator().validate(editor.text(), 0)
            if state[0] != QDoubleValidator.Acceptable:
                QMessageBox.warning(
                    editor,
                    "Input Error",
                    "Value must be a float between 0.0 and 1.0."
                )
                # Revert to previous valid value (optional)
                # editor.setText(self.oldValue)

class PropertiesWindow(QObject):
    def __init__(self):
        super().__init__()

        # Create the table
        self.properties_table = QTableWidget()
        self.properties_table.setColumnCount(3)
        self.properties_table.setHorizontalHeaderLabels(
            ["Defense Property", "Value", "Default Value"])
        # self.properties_table.setRowCount(10)  # Example: setting 10 rows

        self.properties_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.properties_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)  # Adjust the first column
        self.properties_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)  # Adjust the second column
        self.properties_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents)  # Adjust the third column

        # Hide the vertical header (row numbers)
        self.properties_table.verticalHeader().setVisible(False)

        self.properties_table.setItemDelegateForColumn(
            1, EditableDelegate(self.properties_table))
