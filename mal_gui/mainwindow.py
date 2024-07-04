from pathlib import Path

from PySide6.QtWidgets import QWidget,QLineEdit,QSplitter, QMainWindow,QToolBar,QDockWidget, QListWidget,QVBoxLayout,QComboBox,QListWidgetItem, QLabel,QTreeView,QTreeWidget, QTreeWidgetItem,QCheckBox,QPushButton,QFileDialog,QMessageBox
from PySide6.QtGui import QDrag,QPixmap,QAction,QIcon,QIntValidator
from PySide6.QtCore import Qt,QMimeData,QByteArray,QSize

from ModelScene import ModelScene
from ModelView import ModelView
from ObjectExplorer.AssetBase import AssetBase

from ConnectionItem import ConnectionItem

from AssociationTableView import AssociationDefinitions

from ObjectExplorer.AssetFactory import AssetFactory

from DraggableTreeView import DraggableTreeView

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
    def __init__(self,app):
        super().__init__()
        self.app = app #declare an app member
        self.setWindowTitle("MAL GUI")
        self.modelFilename = None

        assetImages = {
            "Application": "images/application.png",
            "Credentials": "images/credentials.png",
            "Data": "images/datastore.png",
            "Group": "images/group.png",
            "Hardware": "images/hardware.png",
            "HardwareVulnerability": "images/hardwareVulnerability.png",
            "IDPS": "images/idps.png",
            "Identity": "images/identity.png",
            "Group": "images/identity.png",
            "Privileges": "images/identity.png",
            "Information": "images/information.png",
            "Network": "images/network.png",
            "ConnectionRule": "images/network.png",
            "PhysicalZone": "images/physicalZone.png",
            "RoutingFirewall": "images/routingFirewall.png",
            "SoftwareProduct": "images/softwareProduct.png",
            "SoftwareVulnerability": "images/softwareVulnerability.png",
            "User": "images/user.png"
        }

        #Create a registry as a dictionary containing name as key and class as value
        self.assetFactory = AssetFactory()
        self.assetFactory.registerAsset("Attacker", "images/attacker.png")

        self.scene = ModelScene(self.assetFactory, self)
        self.view = ModelView(self.scene, self)
        for asset in self.scene.langGraph.assets:
            if not asset.is_abstract:
                self.assetFactory.registerAsset(asset.name,
                    assetImages[asset.name])

        self.createActions()
        self.createMenus()
        self.createToolbar()


        self.view.zoomChanged.connect(self.updateZoomLabel)

        #Association Information
        self.associationInfo = AssociationDefinitions(self)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(self.associationInfo)
        self.splitter.setSizes([200, 100])  # Set initial sizes of widgets in splitter

        self.setCentralWidget(self.splitter)

        # self.setDockNestingEnabled(True)
        # self.setCorner()
        self.dockAble()

    def dockAble(self):

        # ObjectExplorer - LeftSide pannel is Draggable TreeView
        dockObjectExplorer = QDockWidget("Object Explorer",self)
        self.objectExplorerTree = DraggableTreeView()

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
                self.objectExplorerTree.addChildItem(value.assetType, value.assetType+ "@Number_TBD")


        dockObjectExplorer.setWidget(self.objectExplorerTree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockObjectExplorer)

        #EDOC Tab with treeview
        componentTabTree = QTreeWidget()
        componentTabTree.setHeaderLabel(None)


        #Properties Tab with treeview
        self.propertiesTabTree = QTreeWidget()
        self.propertiesTabTree.setHeaderLabel(None)
        self.propertiesTabTree.setColumnCount(2)
        self.propertiesTabTree.setHeaderLabels(["Property","Value"])

        dockProperties = QDockWidget("Properties",self)
        dockProperties.setWidget(self.propertiesTabTree)
        self.addDockWidget(Qt.RightDockWidgetArea, dockProperties)

    def showAssociationCheckBoxChanged(self,checked):
        print("self.showAssociationCheckBoxChanged clicked")
        self.scene.setShowAssociationCheckBoxStatus(checked)
        for connection in self.scene.items():
            if isinstance(connection, ConnectionItem):
                connection.updatePath()

    def updatePropertiesWindow(self, asset):
        self.propertiesTabTree.clear()
        propertiesTabTreeItems = []
        defenses = self.scene.model.get_asset_defenses(
            asset,
            include_defaults = True
        )
        for key, value in defenses.items():
            print(f"DEF:{key} VAL:{float(value)}")
            item = QTreeWidgetItem([key, str(float(value))])
            propertiesTabTreeItems.append(item)

        self.propertiesTabTree.insertTopLevelItems(0,propertiesTabTreeItems)
        self.propertiesTabTree.show()


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
            self.showInformationPopup("Successfully opened model: " + filePath)
            self.scene.model = Model.load_from_file(
                filePath,
                self.scene.lcs
            )
            self.modelFilename = filePath
            #TODO Re-create the items for the assets, associations, and attackers
            # in the model

    def saveModel(self):
        if self.modelFilename:
            self.scene.model.save_to_file(self.modelFilename)
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
            self.scene.model.save_to_file(filePath)
            self.modelFilename = filePath

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
