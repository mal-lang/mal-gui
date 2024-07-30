import csv
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton,QSizePolicy,QMessageBox

class ConnectionDialog(QDialog):
    # def __init__(self, startItem, endItem, scene, parent=None):
    def __init__(self, startItem, endItem,langGraph, lcs,model,parent=None):
        super().__init__(parent)

        # self.scene = scene
        self.langGraph = langGraph
        self.lcs = lcs
        self.model = model
        
        self.setWindowTitle("Select Association Type")
        self.setMinimumWidth(300)

        startAsset = startItem.asset
        endAsset = endItem.asset
        self.startAssetType = startAsset.type
        self.endAssetType = endAsset.type
        self.startAssetName = startAsset.name
        self.endAssetName = endAsset.name

        layout = QVBoxLayout()

        self.label = QLabel(f"{self.startAssetName} : {self.endAssetName}")
        layout.addWidget(self.label)

        self.filterEdit = QLineEdit()
        self.filterEdit.setPlaceholderText("Type to filter...")
        self.filterEdit.textChanged.connect(self.filterItems)
        layout.addWidget(self.filterEdit)

        self.associationListWidget = QListWidget()
        langGraphStartAsset = next(
                (asset for asset in self.langGraph.assets
                 if asset.name == startAsset.type), None
            )
        if langGraphStartAsset is None:
            raise LookupError(f'Failed to find asset "{startAsset.type}" '
                'in language graph.')

        langGraphEndAsset = next(
                (asset for asset in self.langGraph.assets
                 if asset.name == endAsset.type), None
            )
        if langGraphEndAsset is None:
            raise LookupError(f'Failed to find asset "{endAsset.type}" '
                'in language graph.')
        self._str_to_assoc = {}
        for assoc in langGraphStartAsset.associations:
            assetPairs = []
            oppositeAsset = assoc.get_opposite_asset(langGraphStartAsset)

            # Check if the other side of the association matches the other end
            # and if the exact association does not already exist in the
            # model.
            if langGraphEndAsset.is_subasset_of(oppositeAsset):
                print("IDENTIFIED MATCH  ++++++++++++")
                if langGraphStartAsset.is_subasset_of(assoc.left_field.asset):
                    assetPairs.append((startAsset, endAsset))
                else:
                    assetPairs.append((endAsset, startAsset))
            if langGraphStartAsset.is_subasset_of(oppositeAsset):
                # The association could be applied either way, add the
                # reverse association as well.
                otherAsset = assoc.get_opposite_asset(oppositeAsset)
                # Check if the other side of the association matches the other end
                # and if the exact association does not already exist in the
                # model.
                if langGraphEndAsset.is_subasset_of(otherAsset):
                    print("REVERSE ASSOC  ++++++++++++")
                    # We need to create the reverse association as well
                    assetPairs.append((endAsset, startAsset))
            for (leftAsset, rightAsset) in assetPairs:
                if not self.model.association_exists_between_assets(
                        assoc.name,
                        leftAsset,
                        rightAsset):
                    formattedAssocStr = leftAsset.name + "." + \
                        assoc.left_field.fieldname + "-->" + \
                        assoc.name + "-->" + \
                        rightAsset.name + "." + \
                        assoc.right_field.fieldname
                    self._str_to_assoc[formattedAssocStr] = (
                        assoc,
                        leftAsset,
                        rightAsset
                    )
                    self.associationListWidget.addItem(QListWidgetItem(formattedAssocStr))

        layout.addWidget(self.associationListWidget)

        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.OkButtonClicked)
        self.okButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttonLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        self.cancelButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttonLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

        # Select the first item by default
        self.associationListWidget.setCurrentRow(0)

    def filterItems(self, text):
        for i in range(self.associationListWidget.count()):
            item = self.associationListWidget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def OkButtonClicked(self):
        selectedItem = self.associationListWidget.currentItem()
        if selectedItem:
            selectedAssociationText = selectedItem.text()
            # QMessageBox.information(self, "Selected Item", f"You selected: {selectedAssociationText}")
            (assoc, leftAsset, rightAsset) = self._str_to_assoc[selectedAssociationText]
            association = getattr(self.lcs.ns, assoc.name)()
            print(f'N:{assoc.name} LF:{assoc.left_field.fieldname} LA:{leftAsset.name} RF:{assoc.right_field.fieldname} RA:{rightAsset.name}')
            setattr(association, assoc.left_field.fieldname, [leftAsset])
            setattr(association, assoc.right_field.fieldname, [rightAsset])
            selectedItem.association = association
            # self.model.add_association(association)
        self.accept()
