import csv
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton,QSizePolicy,QMessageBox

class ConnectionDialog(QDialog):
    def __init__(self, startAsset, endAsset,  parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Select Association Type")
        self.setMinimumWidth(300)
        
        self.startAssetType = startAsset.assetType
        self.endAssetType = endAsset.assetType
        self.startAssetName = startAsset.assetName
        self.endAssetName = endAsset.assetName

        layout = QVBoxLayout()
        
        self.label = QLabel(f"{self.startAssetName} : {self.endAssetName}")
        layout.addWidget(self.label)
        
        self.filterEdit = QLineEdit()
        self.filterEdit.setPlaceholderText("Type to filter...")
        self.filterEdit.textChanged.connect(self.filterItems)
        layout.addWidget(self.filterEdit)

        csvAssociationInfoFileName = 'AssociationInfo.csv'
        with open(csvAssociationInfoFileName, 'r') as file:
            reader = csv.reader(file)
            # headers = next(reader)  # Read the first row as headers
            data = [row for row in reader]  # Read the rest of the rows as data
        
        # for row in data:
        #     print("row is:")
        #     print(row)
        
        
        self.associationListWidget = QListWidget()
        i=0
        for row in data:
            # print("row is:")
            print(row)
            assocLeftAssetName,assocLeftFieldName,assocName,assocRightFieldName,assocRightAssetName = row
            print("Checking row : "+ str(i+1))
            i=i+1
            print("self.startAssetName = "+ self.startAssetName)
            print("assocLeftAssetName= "+ assocLeftAssetName)
            print("self.endAssetName = "+ self.endAssetName)
            print("assocRightAssetName = "+ assocRightAssetName)
            if assocLeftAssetName == self.startAssetType and assocRightAssetName == self.endAssetType:
                print("IDENTIFIED MATCH  ++++++++++++")
                formattedAssocStr = self.startAssetName +"."+ assocLeftFieldName +"-->"+ assocName +"-->" + self.endAssetName +"."+ assocRightFieldName
                self.associationListWidget.addItem(QListWidgetItem(formattedAssocStr))
                
        layout.addWidget(self.associationListWidget)      

        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
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
            QMessageBox.information(self, "Selected Item", f"You selected: {selectedAssociationText}")
            self.accept()
