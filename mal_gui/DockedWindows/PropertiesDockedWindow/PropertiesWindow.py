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
    def __init__(self, assetItem, parent=None):
        super(EditableDelegate, self).__init__(parent)
        self.assetItem = assetItem

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        validator = FloatValidator()
        editor.setValidator(validator)
        editor.editingFinished.connect(self.validateEditor)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        print("Value Entered: "+ value)
        # setattr(selectedItem.asset, row[0],value)
        state = editor.validator().validate(value, 0)
        if state[0] != QDoubleValidator.Acceptable:
            QMessageBox.warning(editor, "Input Error", "Value must be a float between 0.0 and 1.0.")
            # Revert to previous valid value (optional)
            # editor.setText(index.model().data(index, Qt.EditRole))
        else:
            model.setData(index, value, Qt.EditRole)
            # Update the attribute in assetItem
            row = index.row()
            # propertyKey = model.item(row, 0).text()
            propertyKey = index.sibling(row, 0).data()
            
            #Here We are setting the attribute - Probably this is Andrei's expectation
            setattr(self.assetItem.asset, propertyKey, float(value))

    def validateEditor(self):
        editor = self.sender()
        if editor:
            state = editor.validator().validate(editor.text(), 0)
            if state[0] != QDoubleValidator.Acceptable:
                QMessageBox.warning(editor, "Input Error", "Value must be a float between 0.0 and 1.0.")
                # Revert to previous valid value (optional)
                # editor.setText(self.oldValue)
                
class PropertiesWindow(QObject):
    def __init__(self):
        super().__init__()
        
        # Create the table
        self.propertiesTable = QTableWidget()
        self.propertiesTable.setColumnCount(3)
        self.propertiesTable.setHorizontalHeaderLabels(["Defense Property", "Value", "Default Value"])
        # self.propertiesTable.setRowCount(10)  # Example: setting 10 rows


        self.propertiesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.propertiesTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Adjust the first column
        self.propertiesTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Adjust the second column
        self.propertiesTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Adjust the third column


        # Hide the vertical header (row numbers)
        self.propertiesTable.verticalHeader().setVisible(False)
        
        self.propertiesTable.setItemDelegateForColumn(1, EditableDelegate(self.propertiesTable))

