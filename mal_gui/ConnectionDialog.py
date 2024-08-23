import csv
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton,QSizePolicy,QMessageBox

class ConnectionDialog(QDialog):
    def filterItems(self, text):
        pass
    
    def OkButtonClicked(self):
        pass


class AssociationConnectionDialog(ConnectionDialog):
    def __init__(self, startItem, endItem,langGraph, lcs,model,parent=None):
        super().__init__(parent)

        self.langGraph = langGraph
        self.lcs = lcs
        self.model = model
        
        self.setWindowTitle("Select Association Type")
        self.setMinimumWidth(300)

        print(f'START ITEM TYPE {startItem.assetType}')
        print(f'END ITEM TYPE {endItem.assetType}')

        targetAsset = None
        self.associationListWidget = QListWidget()

        startAsset = startItem.asset
        endAsset = endItem.asset
        self.startAssetType = startAsset.type
        self.endAssetType = endAsset.type
        self.startAssetName = startAsset.name
        self.endAssetName = endAsset.name
        self.layout = QVBoxLayout()
        self.label = QLabel(f"{self.startAssetName} : {self.endAssetName}")
        self.layout.addWidget(self.label)
        self.filterEdit = QLineEdit()
        self.filterEdit.setPlaceholderText("Type to filter...")
        self.filterEdit.textChanged.connect(self.filterItems)
        self.layout.addWidget(self.filterEdit)
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
        self.layout.addWidget(self.associationListWidget)

        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.OkButtonClicked)
        self.okButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttonLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        self.cancelButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(buttonLayout)

        self.setLayout(self.layout)

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
            # TODO: Create association based on its full name instead in order
            # to avoid conflicts when multiple associations with the same name
            # exist.
            association = getattr(self.lcs.ns, assoc.name)()
            print(f'N:{assoc.name} LF:{assoc.left_field.fieldname} LA:{leftAsset.name} RF:{assoc.right_field.fieldname} RA:{rightAsset.name}')
            setattr(association, assoc.left_field.fieldname, [leftAsset])
            setattr(association, assoc.right_field.fieldname, [rightAsset])
            selectedItem.association = association
            # self.model.add_association(association)
        self.accept()
        
class EntrypointConnectionDialog(ConnectionDialog):
    def __init__(self, attackerItem, assetItem, langGraph, lcs, model, parent=None):
        super().__init__(parent)

        self.langGraph = langGraph
        self.lcs = lcs
        self.model = model

        self.setWindowTitle("Select Entry Point")
        self.setMinimumWidth(300)

        print(f'Attacker ITEM TYPE {attackerItem.assetType}')
        print(f'Asset ITEM TYPE {assetItem.assetType}')

        self.attackStepListWidget = QListWidget()
        attacker = attackerItem.attackerAttachment

        if assetItem.asset is not None:
            assetType = self.langGraph.get_asset_by_name(assetItem.asset.type)

            # Find asset attack steps already part of attacker entry points
            entry_point_attack_steps = next(
                (entry_point_tuple[1] for entry_point_tuple
                 in attacker.entry_points
                 if entry_point_tuple[0] == assetItem.asset),
                 []
            )

            for attackStep in assetType.attack_steps:
                if attackStep.type not in ['or', 'and']:
                    continue

                if attackStep.name not in entry_point_attack_steps:
                    print(attackStep.name)
                    item = QListWidgetItem(attackStep.name)
                    self.attackStepListWidget.addItem(item)

            self.layout = QVBoxLayout()

            self.label = QLabel(f"{attacker.name}:{assetItem.asset.name}")
            self.layout.addWidget(self.label)

            self.filterEdit = QLineEdit()
            self.filterEdit.setPlaceholderText("Type to filter...")
            self.filterEdit.textChanged.connect(self.filterItems)
            self.layout.addWidget(self.filterEdit)
            self.layout.addWidget(self.attackStepListWidget)


        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.OkButtonClicked)
        self.okButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttonLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        self.cancelButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(buttonLayout)

        self.setLayout(self.layout)

        # Select the first item by default
        self.attackStepListWidget.setCurrentRow(0)

    def filterItems(self, text):
        for i in range(self.attackStepListWidget.count()):
            item = self.attackStepListWidget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def OkButtonClicked(self):
        self.accept()
