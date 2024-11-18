from PySide6.QtWidgets import QWidget,QTableView,QVBoxLayout
from PySide6.QtGui import QStandardItemModel,QStandardItem


class AssociationDefinitions(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.associationInfo = None
        self.mainWindow = parent

        self.tableAssociationView = QTableView(self)

        self.associationInfoModel = QStandardItemModel()

        #headers for the columns
        self.associationInfoModel.setHorizontalHeaderLabels(['AssocLeftAsset', 'AssocLeftField', 'AssocName', 'AssocRightField','AssocRightAsset'])

        self.associationInfoModel.removeRows(0, self.associationInfoModel.rowCount())

        for assoc in self.mainWindow.scene.langGraph.associations:
            items = [
                QStandardItem(assoc.left_field.asset.name),
                QStandardItem(assoc.left_field.fieldname),
                QStandardItem(assoc.name),
                QStandardItem(assoc.right_field.fieldname),
                QStandardItem(assoc.right_field.asset.name)
            ]
            self.associationInfoModel.appendRow(items)

        self.associationInfo = self.associationInfoModel

        self.tableAssociationView.setModel(self.associationInfoModel)

        layout = QVBoxLayout()
        layout.addWidget(self.tableAssociationView)

        # Set the layout to the widget
        self.setLayout(layout)

    def getAssociationInfo(self):
        return self.associationInfo


