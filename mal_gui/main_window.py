from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QSplitter,
    QMainWindow,
    QToolBar,
    QDockWidget,
    QListWidget,
    QComboBox,
    QLabel,
    QTreeWidget,
    QCheckBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem
)
from PySide6.QtGui import QDrag, QAction, QIcon, QIntValidator
from PySide6.QtCore import Qt, QMimeData, QByteArray, QSize, Signal, QPointF

from qt_material import apply_stylesheet,list_themes

from .model_scene import ModelScene
from .model_view import ModelView
from .object_explorer.asset_base import AssetBase
from .object_explorer.asset_factory import AssetFactory
from .assets_container.assets_container import AssetsContainer
from .connection_item import AssociationConnectionItem

from .docked_windows.draggable_tree_view import DraggableTreeView
from .docked_windows.item_details_window import ItemDetailsWindow
from .docked_windows.properties_window import PropertiesWindow,EditableDelegate
from .docked_windows.attack_steps_window import AttackStepsWindow
from .docked_windows.asset_relations_window import AssetRelationsWindow

from maltoolbox.language import LanguageGraph, LanguageClassesFactory
from maltoolbox.model import Model


class DraggableListWidget(QListWidget):
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if item:
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setData("application/x-qabstractitemmodeldatalist", QByteArray())
                mime_data.setData("text/plain", item.text().encode())
                drag.setMimeData(mime_data)
                drag.exec()


class MainWindow(QMainWindow):
    updateChildsInObjectExplorerSignal = Signal()
    
    def __init__(self,app,malLanguageMarFilePath):
        super().__init__()
        self.app = app #declare an app member
        self.setWindowTitle("MAL GUI")
        self.modelFileName = None

        assetImages = {
            "Application": "images/application.png",
            "Credentials": "images/credentials.png",
            "Data": "images/datastore.png",
            "Group": "images/group.png",
            "Hardware": "images/hardware.png",
            "HardwareVulnerability": "images/hardwareVulnerability.png",
            "IDPS": "images/idps.png",
            "Identity": "images/identity.png",
            "Privileges": "images/privileges.png",
            "Information": "images/information.png",
            "Network": "images/network.png",
            "ConnectionRule": "images/connectionRule.png",
            "PhysicalZone": "images/physicalZone.png",
            "RoutingFirewall": "images/routingFirewall.png",
            "SoftwareProduct": "images/softwareProduct.png",
            "SoftwareVulnerability": "images/softwareVulnerability.png",
            "User": "images/user.png"
        }
        
        self.eyeUnhideIconImage = "images/eyeUnhide.png"
        self.eyeHideIconImage = "images/eyeHide.png"
        self.rgbColorIconImage = "images/rgbColor.png"

        #Create a registry as a dictionary containing name as key and class as value
        self.assetFactory = AssetFactory()
        self.assetFactory.registerAsset("Attacker", "images/attacker.png")
        
        # Create the MAL language graph, language classes factory, and
        # instance model
        # self.langGraph = LanguageGraph.from_mar_archive("langs/org.mal-lang.coreLang-1.0.0.mar")
        self.langGraph = LanguageGraph.from_mar_archive(malLanguageMarFilePath)
        self.lcs = LanguageClassesFactory(self.langGraph)
        self.model = Model("Untitled Model", self.lcs)


        PACKAGE_DIR = Path(__file__).resolve().parent
        for asset in self.langGraph.assets:
            if not asset.is_abstract:
                asset_image_path = str(PACKAGE_DIR / assetImages[asset.name])
                self.assetFactory.registerAsset(
                    asset.name,
                    asset_image_path
                )
        
        #assetFactory registration should complete before injecting into ModelScene
        self.scene = ModelScene(self.assetFactory, self.langGraph, self.lcs,self.model, self)
        self.view = ModelView(self.scene, self)

        self.createActions()
        self.createMenus()
        self.createToolbar()


        self.view.zoomChanged.connect(self.updateZoomLabel)

        #Association Information
        # self.associationInfo = AssociationDefinitions(self)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.view)
        # self.splitter.addWidget(self.associationInfo)
        self.splitter.setSizes([200, 100])  # Set initial sizes of widgets in splitter

        self.setCentralWidget(self.splitter)

        # self.setDockNestingEnabled(True)
        # self.setCorner()
        
        self.updateChildsInObjectExplorerSignal.connect(self.updateExplorerDockedWindow)
        
        self.dockAble()

    def dockAble(self):

        # ObjectExplorer - LeftSide pannel is Draggable TreeView
        dockObjectExplorer = QDockWidget("Object Explorer",self)
        self.objectExplorerTree = DraggableTreeView(self.scene,self.eyeUnhideIconImage,self.eyeHideIconImage,self.rgbColorIconImage)

        #printing registry
        print("printing registry: ")
        for key,values in self.assetFactory.assetRegistry.items():
            # print(f"Key: {key}")
            for value in values:
                # print(f"  Tuple: {value}")
                # print(f"    Field1: {value.assetType}")
                # print(f"    Field2: {value.assetName}")
                # print(f"    Field3: {value.assetImage}")
                self.objectExplorerTree.setParentItemText(value.assetType,value.assetImage)
                # self.objectExplorerTree.addChildItem(value.assetType, value.assetType+ "@Number_TBD")


        dockObjectExplorer.setWidget(self.objectExplorerTree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockObjectExplorer)

        #EDOC Tab with treeview
        componentTabTree = QTreeWidget()
        componentTabTree.setHeaderLabel(None)
        
        
        #ItemDetails with treeview
        self.itemDetailsWindow = ItemDetailsWindow()
        
        dockItemDetails = QDockWidget("Item Details",self)
        dockItemDetails.setWidget(self.itemDetailsWindow)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockItemDetails)
        
        #Properties Tab with tableview
        self.propertiesDockedWindow = PropertiesWindow()
        self.propertiesTable = self.propertiesDockedWindow.propertiesTable

        dockProperties = QDockWidget("Properties",self)
        dockProperties.setWidget(self.propertiesTable)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockProperties)
        
        #AttackSteps Tab with ListView
        self.attackStepsDockedWindow = AttackStepsWindow()
        dockAttackSteps = QDockWidget("Attack Steps",self)
        dockAttackSteps.setWidget(self.attackStepsDockedWindow)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockAttackSteps)
        
        #AssetRelations Tab with ListView
        self.assetRelationsDockedWindow = AssetRelationsWindow()
        dockAssetRelations = QDockWidget("Asset Relations",self)
        dockAssetRelations.setWidget(self.assetRelationsDockedWindow)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockAssetRelations)
        
        #Keep Propeties Window and Attack Step Window Tabbed
        self.tabifyDockWidget(dockProperties, dockAttackSteps)
        
        #Keep the properties Window highlighted and raised
        dockProperties.raise_()

    def showAssociationCheckBoxChanged(self,checked):
        print("self.showAssociationCheckBoxChanged clicked")
        self.scene.setShowAssociationCheckBoxStatus(checked)
        for connection in self.scene.items():
            if isinstance(connection, AssociationConnectionItem):
                connection.updatePath()
    
    def showImageIconCheckBoxChanged(self,checked):
        print("self.showImageIconCheckBoxChanged clicked")
        for item in self.scene.items():
            if isinstance(item, (AssetBase,AssetsContainer)):
                item.toggleIconVisibility()
                
    def fitToViewButtonClicked(self):
        print("Fit To View Button Clicked..")  
        # Find the bounding rectangle of all items in Scene
        boundingRect = self.scene.itemsBoundingRect()   
        self.view.fitInView(boundingRect,Qt.KeepAspectRatio) 

    def updatePropertiesWindow(self, assetItem): 
        #Clear the table
        self.propertiesTable.setRowCount(0)
        
        if assetItem is not None and assetItem.assetType != "Attacker":
            asset = assetItem.asset
            defenses = self.model.get_asset_defenses(
                asset,
                include_defaults = True
            )
            
            # for association in asset.associations:
            #     print("association= "+ str(association.name))
            
            properties = list(defenses.items())
            # Insert new rows based on the data dictionary
            numRows = len(properties)
            self.propertiesTable.setRowCount(numRows)
            self.propertiesTable.currentItem = assetItem
            
            for row, (propertyKey, propertyValue) in enumerate(properties):
                print(f"DEF:{propertyKey} VAL:{float(propertyValue)}")
                
                columnPropertyName = QTableWidgetItem(propertyKey)
                columnPropertyName.setFlags(Qt.ItemIsEnabled)  # Make the property name read-only
            
                columnValue = QTableWidgetItem(str(float(propertyValue)))
                columnValue.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)  # Make the value editable
            
                columnDefaultValue = QTableWidgetItem("1.0")
                columnDefaultValue.setFlags(Qt.ItemIsEnabled)  # Make the default value read-only

                self.propertiesTable.setItem(row, 0, columnPropertyName)
                self.propertiesTable.setItem(row, 1, columnValue)
                self.propertiesTable.setItem(row, 2, columnDefaultValue)
            
            # Set the item delegate and pass assetItem - based on Andrei's input
            self.propertiesTable.setItemDelegateForColumn(1, EditableDelegate(assetItem))

        else: 
            self.propertiesTable.currentItem = None
            
    def updateAttackStepsWindow(self, attackerAssetItem):
        if attackerAssetItem is not None:
            self.attackStepsDockedWindow.clear()
            for asset, attack_step_names in \
                    attackerAssetItem.attackerAttachment.entry_points:
                for attack_step_name in attack_step_names:
                    self.attackStepsDockedWindow.addItem(
                        asset.name + ':' + attack_step_name
                    )
        else:
            self.attackStepsDockedWindow.clear()

    def updateAssetRelationsWindow(self, assetItem):
        self.assetRelationsDockedWindow.clear()
        if assetItem is not None:
            asset = assetItem.asset
            for association in asset.associations:
                left_field_name, right_field_name = \
                    self.scene.model.get_association_field_names(association)
                if asset in getattr(association, left_field_name):
                    opposite_field_name = right_field_name
                else:
                    opposite_field_name = left_field_name

                for associated_asset in getattr(association,
                        opposite_field_name):
                    self.assetRelationsDockedWindow.addItem(
                        opposite_field_name + "-->" + associated_asset.name)

    def createActions(self):

        self.zoomInAction = QAction(QIcon("images/zoomIn.png"), "ZoomIn", self)
        self.zoomInAction.triggered.connect(self.zoomIn)

        self.zoomOutAction = QAction(QIcon("images/zoomOut.png"), "ZoomOut", self)
        self.zoomOutAction.triggered.connect(self.zoomOut)

        #undo Action
        self.undoAction = QAction(QIcon("images/undoIcon.png"), "Undo", self)
        self.undoAction.setShortcut("Ctrl+z")
        self.undoAction.triggered.connect(self.scene.undoStack.undo)

        #redo Action
        self.redoAction = QAction(QIcon("images/redoIcon.png"), "Redo", self)
        self.redoAction.setShortcut("Ctrl+Shift+z")
        self.redoAction.triggered.connect(self.scene.undoStack.redo)
        
        #cut Action
        self.cutAction = QAction(QIcon("images/cutIcon.png"), "Cut", self)
        self.cutAction.setShortcut("Ctrl+x")
        self.cutAction.triggered.connect(lambda: self.scene.cutAssets(self.scene.selectedItems()))

        #copy Action
        self.copyAction = QAction(QIcon("images/copyIcon.png"), "Copy", self)
        self.copyAction.setShortcut("Ctrl+c")
        self.copyAction.triggered.connect(lambda: self.scene.copyAssets(self.scene.selectedItems()))
        
        #paste Action
        self.pasteAction = QAction(QIcon("images/pasteIcon.png"), "Paste", self)
        self.pasteAction.setShortcut("Ctrl+v")
        self.pasteAction.triggered.connect(lambda: self.scene.pasteAssets(QPointF(0,0)))
        
        #delete Action
        self.deleteAction = QAction(QIcon("images/deleteIcon.png"), "Delete", self)
        self.deleteAction.setShortcut("Delete")
        self.deleteAction.triggered.connect(lambda: self.scene.deleteAssets(self.scene.selectedItems()))

    def createMenus(self):
         #Menubar and menus
        self.menuBar = self.menuBar()
        self.fileMenu =  self.menuBar.addMenu("&File")
        self.fileMenuNewAction = self.fileMenu.addAction("New")
        self.fileMenuOpenAction = self.fileMenu.addAction("Open")
        self.fileMenuSaveAction = self.fileMenu.addAction("Save")
        self.fileMenuSaveAsAction = self.fileMenu.addAction("SaveAs..")
        self.fileMenuQuitAction = self.fileMenu.addAction("Quit")
        self.fileMenuOpenAction.triggered.connect(self.loadModel)
        self.fileMenuSaveAction.triggered.connect(self.saveModel)
        self.fileMenuSaveAsAction.triggered.connect(self.saveAsModel)
        self.fileMenuQuitAction.triggered.connect(self.quitApp)
        self.editMenu = self.menuBar.addMenu("Edit")
        self.editMenuUndoAction = self.editMenu.addAction(self.undoAction)
        self.editMenuRedoAction = self.editMenu.addAction(self.redoAction)
        self.editMenuCutAction = self.editMenu.addAction(self.cutAction)
        self.editMenuCopyAction = self.editMenu.addAction(self.copyAction)
        self.editMenuPasteAction = self.editMenu.addAction(self.pasteAction)
        self.editMenuDeleteAction = self.editMenu.addAction(self.deleteAction)

    def createToolbar(self):
        #toolbar
        self.toolbar = QToolBar("Mainwindow Toolbar")
        self.toolbar.setIconSize(QSize(20, 20))  # Adjust the size to reduce bigger image- its a magic number
        self.addToolBar(self.toolbar)
        # Set the style to show text beside the icon for the entire toolbar
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        #Add the quit action
        self.toolbar.addAction(self.fileMenuQuitAction)

        self.toolbar.addSeparator()

        showAssociationCheckBoxLabel  = QLabel("Show Association")
        showAssociationCheckBox = QCheckBox()
        showAssociationCheckBox.setCheckState(Qt.CheckState.Unchecked)
        self.toolbar.addWidget(showAssociationCheckBoxLabel)
        self.toolbar.addWidget(showAssociationCheckBox)
        showAssociationCheckBox.stateChanged.connect(self.showAssociationCheckBoxChanged)
        
        self.toolbar.addSeparator()

        showImageIconCheckBoxLabel  = QLabel("Show Image Icon")
        showImageIconCheckBox = QCheckBox()
        showImageIconCheckBox.setCheckState(Qt.CheckState.Checked)
        self.toolbar.addWidget(showImageIconCheckBoxLabel)
        self.toolbar.addWidget(showImageIconCheckBox)
        showImageIconCheckBox.stateChanged.connect(self.showImageIconCheckBoxChanged)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.zoomInAction)
        self.toolbar.addAction(self.zoomOutAction)
        self.zoomLabel = QLabel("100%")
        self.zoomLineEdit = QLineEdit()
        self.zoomLineEdit.setValidator(QIntValidator()) # No limit on zoom level, but should be an integer
        # self.zoomLineEdit.setValidator(QIntValidator(1, 500)) #Akash: If we want to put limit we can use this
        self.zoomLineEdit.setText("100")
        self.zoomLineEdit.returnPressed.connect(self.setZoomLevelFromLineEdit)
        self.zoomLineEdit.setFixedWidth(40)
        self.toolbar.addWidget(self.zoomLabel)
        self.toolbar.addWidget(self.zoomLineEdit)

        self.toolbar.addSeparator()

        #undo/redo
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)
        self.toolbar.addSeparator()
        #cut/copy/paste/delete
        self.toolbar.addAction(self.cutAction)
        self.toolbar.addAction(self.copyAction)
        self.toolbar.addAction(self.pasteAction)
        self.toolbar.addAction(self.deleteAction)
        self.toolbar.addSeparator()
        
         #Fit To Window
        fitToViewButton = QPushButton(QIcon("images/fitToView.png"), "Fit To View")
        self.toolbar.addWidget(fitToViewButton)
        fitToViewButton.clicked.connect(self.fitToViewButtonClicked)
        self.toolbar.addSeparator()
        
        #Material Theme - https://pypi.org/project/qt-material/
        materialThemeLabel  = QLabel("Theme")
        self.themeComboBox = QComboBox()
        
        self.themeComboBox.addItem('None')
        inbuiltThemeListFromPackage = list_themes()
        self.themeComboBox.addItems(inbuiltThemeListFromPackage)
        
        self.toolbar.addWidget(materialThemeLabel)
        self.toolbar.addWidget(self.themeComboBox)
        self.themeComboBox.currentIndexChanged.connect(self.onThemeSelectionChanged)
        self.toolbar.addSeparator()

    def zoomIn(self):
        print("Zoom In Clicked")
        self.view.zoomIn()

    def zoomOut(self):
        print("Zoom Out Clicked")
        self.view.zoomOut()

    def setZoomLevelFromLineEdit(self):
        zoomValue = int(self.zoomLineEdit.text())
        self.view.setZoom(zoomValue)

    def updateZoomLabel(self):
        self.zoomLabel.setText(f"{int(self.view.zoomFactor * 100)}%")
        self.zoomLineEdit.setText(f"{int(self.view.zoomFactor * 100)}")

    def loadModel(self):
        """
        To load SharpCut project from a file.This function is not used currently.
        """
        fileExtensionFilter = "YAML Files (*.yaml *.yml);;JSON Files (*.json)"
        filePath, _ = QFileDialog.getOpenFileName(None, "Select Model File", "",fileExtensionFilter)

        if not filePath:
            print("No valid path detected for loading")
            return
        else:
            OpenProjectUserConfirmation = QMessageBox.question(self, "Load New Project",
                                     "Loading a new project will delete current work (if any). Do you want to continue ?",
                                     QMessageBox.Ok | QMessageBox.Cancel)
            if OpenProjectUserConfirmation == QMessageBox.Ok:
                
                #clear scene so that canvas becomes blank
                self.scene.clear()
                
                self.showInformationPopup("Successfully opened model: " + filePath)
                self.scene.model = Model.load_from_file(
                    filePath,
                    self.scene.lcs
                )
                self.modelFileName = filePath
                self.scene.drawModel()
            else:
                #User canceled, do nothing - Need to check with Andrei for any other behaviour
                pass
            
    def updatePositionsAndSaveModel(self):

        print(f'ASSET ID TO ITEMS KEYS:{self.scene._asset_id_to_item.keys()}')
        for asset in self.scene.model.assets:
            print(f'ASSET NAME:{asset.name} ID:{asset.id} TYPE:{asset.type}')
            item = self.scene._asset_id_to_item[int(asset.id)]
            position = item.pos()
            asset.extras = {
                "position": 
                    {
                        "x": position.x(),
                        "y": position.y()
                    }
            }
        self.scene.model.save_to_file(self.modelFileName)

    def saveModel(self):
        if self.modelFileName:
            self.updatePositionsAndSaveModel()
        else:
            self.saveAsModel()

    def saveAsModel(self):
        """
        To Save SharpCut project from current scene on window. This function is not used currently.
        """
        fileDialog = QFileDialog()
        fileDialog.setAcceptMode(QFileDialog.AcceptSave)
        fileDialog.setDefaultSuffix("yaml")
        filePath, _ = fileDialog.getSaveFileName()

        if not filePath:
            print("No valid path detected for saving")
            return
        else:
            self.showInformationPopup("Successfully saved model to: " + filePath)
            self.scene.model.name = Path(filePath).stem
            self.modelFileName = filePath
            self.updatePositionsAndSaveModel()

    def quitApp(self):
        self.app.quit()


    def showInformationPopup(self,messageText):
        parentWidget = QWidget() #To maintain object lifetim
        messageBox = QMessageBox(parentWidget)
        messageBox.setIcon(QMessageBox.Information)
        messageBox.setWindowTitle("Information") #default values
        messageBox.setText("This is default informative Text") #default values
        messageBox.setInformativeText(messageText) #default values
        messageBox.setStandardButtons(QMessageBox.Ok) #default Ok Button
        messageBox.exec()
    
    def updateExplorerDockedWindow(self):
        #Clean the existing child and fill each items from scratch- performance BAD- To be discussed/improved
        self.objectExplorerTree.clearAllObjectExplorerChildItems()
        
        #Fill all the items from Scene one by one
        for childAssetItem in self.scene.items():
            if isinstance(childAssetItem,AssetBase):
                # Check if parent exists before adding child
                # parentAssetType = self.objectExplorerTree.checkAndGetIfParentAssetTypeExists(childAssetItem.assetType)
                parentItem,parentAssetType = self.objectExplorerTree.checkAndGetIfParentAssetTypeExists(childAssetItem.assetType)

                if parentAssetType:
                    self.objectExplorerTree.addChildItem(parentItem,childAssetItem, str(childAssetItem.assetName))
                    
    def onThemeSelectionChanged(self):
        # Get the selected theme
        selectedTheme = self.themeComboBox.currentText()
        print(f"{selectedTheme} is the Theme selected")
        apply_stylesheet(self.app, theme=selectedTheme)
                
            
