from PySide6.QtWidgets import QWidget,QTableView,QVBoxLayout
from PySide6.QtGui import QStandardItemModel,QStandardItem

from .main_window import MainWindow
class AssociationDefinitions(QWidget):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)

        self.association_info = None
        self.main_window = parent

        self.table_association_view = QTableView(self)
        self.association_info_model = QStandardItemModel()

        #headers for the columns
        self.association_info_model.setHorizontalHeaderLabels(
            ['AssocLeftAsset', 'AssocLeftField', 'AssocName',
             'AssocRightField','AssocRightAsset']
        )

        self.association_info_model.removeRows(
            0, self.association_info_model.rowCount()
        )

        for assoc in self.main_window.scene.lang_graph.associations:
            items = [
                QStandardItem(assoc.left_field.asset.name),
                QStandardItem(assoc.left_field.fieldname),
                QStandardItem(assoc.name),
                QStandardItem(assoc.right_field.fieldname),
                QStandardItem(assoc.right_field.asset.name)
            ]
            self.association_info_model.appendRow(items)

        self.association_info = self.association_info_model
        self.table_association_view.setModel(self.association_info_model)

        layout = QVBoxLayout()
        layout.addWidget(self.table_association_view)

        # Set the layout to the widget
        self.setLayout(layout)

    def get_association_info(self):
        return self.association_info
