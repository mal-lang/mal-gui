from PySide6.QtWidgets import QWidget,QLineEdit,QSplitter, QMainWindow,QToolBar,QDockWidget, QListWidget,QVBoxLayout,QComboBox,QListWidgetItem, QLabel,QTreeView,QTreeWidget, QTreeWidgetItem,QCheckBox,QPushButton
from PySide6.QtGui import QDrag,QPixmap,QAction,QIcon,QIntValidator
from PySide6.QtCore import Qt,QMimeData,QByteArray,QSize

from ModelScene import ModelScene
from ModelView import ModelView
from ObjectExplorer.AssetBase import AssetBase

from graph import GraphWindow
from ConnectionItem import ConnectionItem

from AssociationTableView import AssociationDefinitions

# from malmodels import Attacker,Client,Container,Datastore,Firewall,Host
from ObjectExplorer.AssetFactory import AssetFactory

from DraggableTreeView import DraggableTreeView

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
        
        self.createActions()
        self.createMenus()
        self.createToolbar()
        
        #Create a registery as a dictionary containing name as key and class as value
        self.assetFactory = AssetFactory()
        self.assetFactory.registerAsset("Application", "images/application.png")
        self.assetFactory.registerAsset("Attacker", "images/attacker.png")
        self.assetFactory.registerAsset("Credentials", "images/credentials.png")
        self.assetFactory.registerAsset("Data", "images/dataStore.png")
        self.assetFactory.registerAsset("Group", "images/group.png")
        self.assetFactory.registerAsset("Hardware", "images/hardware.png")
        self.assetFactory.registerAsset("HardwareVulnerability", "images/hardwareVulnerability.png")
        # self.assetFactory.registerAsset("IAMObject", "images/IAMObject.png") # Need to verify before adding here
        self.assetFactory.registerAsset("IDPS", "images/idps.png")
        self.assetFactory.registerAsset("Identity", "images/identity.png")
        self.assetFactory.registerAsset("Information", "images/information.png")
        self.assetFactory.registerAsset("Network", "images/network.png")
        self.assetFactory.registerAsset("PhysicalZone", "images/physicalZone.png")
        self.assetFactory.registerAsset("RoutingFirewall", "images/routingFirewall.png")
        self.assetFactory.registerAsset("SoftwareProduct", "images/softwareProduct.png")
        self.assetFactory.registerAsset("SoftwareVulnerability", "images/softwareVulnerability.png")
        self.assetFactory.registerAsset("User", "images/user.png")
        
        
        
        self.scene = ModelScene(self.assetFactory)
        self.view = ModelView(self.scene, self)
        
        self.view.zoomChanged.connect(self.updateZoomLabel)
        
        #Simple Graphics with networkx example
        self.graphWindow = GraphWindow()
        # self.setCentralWidget(self.graphWindow)
        
        #Association Information
        self.associationInfo = AssociationDefinitions()
        
        self.splitter = QSplitter()
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(self.associationInfo)
        self.splitter.addWidget(self.graphWindow)
        self.splitter.setSizes([200, 100, 100])  # Set initial sizes of widgets in splitter
        
        self.setCentralWidget(self.splitter)
        
        # self.setDockNestingEnabled(True)
        # self.setCorner()
        self.dockAble()
    
    def dockAble(self):
        
        # edocTabTree Data
        edocTabTreeData = {
            "Attacker": ["TBD_1","TBD_2", "TBD_3"],
            "Templates": [["AccessControl", "ApplicationClient", "Attacker", "Dataflow","Datastore","Firewall"]],
            "SoftwareProduct": []
        }
        
        malGuiComponentTabTreeData = {
            "MALGuiCADComponents": ["clients","hosts", "networkRelated","protocols","services","softwares"],
        }
        
        propertiesTabTreeData = {
            "Attacker": ["TBD_1","TBD_2", "TBD_3"],
            "Templates": [["AccessControl", "ApplicationClient", "Attacker", "Dataflow","Datastore","Firewall"]],
            "SoftwareProduct": []
        }
        
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
        
        edocTabTreeItems = []
        for key, values in malGuiComponentTabTreeData.items():
            item = QTreeWidgetItem([key])
            for value in values:
                ext = "ext"
                child = QTreeWidgetItem([value, ext])
                secondLevelChild = QTreeWidgetItem(["another child"])
                child.addChild(secondLevelChild)
                item.addChild(child)
            edocTabTreeItems.append(item)
        componentTabTree.insertTopLevelItems(0,edocTabTreeItems)
        componentTabTree.show()
        
        dockEDOC = QDockWidget("Components",self)
        dockEDOC.setWidget(componentTabTree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockEDOC)
                
                
        #Properties Tab with treeview        
        propertiesTabTree = QTreeWidget()
        propertiesTabTree.setHeaderLabel(None)
        propertiesTabTree.setColumnCount(2)
        propertiesTabTree.setHeaderLabels(["Property","Value"])
        
        propertiesTabTreeItems = []
        for key, values in propertiesTabTreeData.items():
            item = QTreeWidgetItem([key])
            for value in values:
                val = "1.0"
                child = QTreeWidgetItem([value, val])
                item.addChild(child)
            propertiesTabTreeItems.append(item)
        propertiesTabTree.insertTopLevelItems(0,propertiesTabTreeItems)
        propertiesTabTree.show()
        
        dockProperties = QDockWidget("Properties",self)
        dockProperties.setWidget(propertiesTabTree)
        self.addDockWidget(Qt.RightDockWidgetArea, dockProperties)
        
    def showAssociationCheckBoxChanged(self,checked):
        print("self.showAssociationCheckBoxChanged clicked")
        for connection in self.scene.items():
            if isinstance(connection, ConnectionItem):
                connection.setShowAssocitaions(checked)
                
                
    def createActions(self):

        self.zoomInAction = QAction(QIcon("images/zoomIn.png"), "ZoomIn", self)
        self.zoomInAction.triggered.connect(self.zoomIn)
        
        self.zoomOutAction = QAction(QIcon("images/zoomOut.png"), "ZoomOut", self)
        self.zoomOutAction.triggered.connect(self.zoomOut)

        
    def createMenus(self):
         #Menubar and menus
        self.menuBar = self.menuBar()
        self.fileMenu =  self.menuBar.addMenu("&File")
        self.fileMenuNewAction = self.fileMenu.addAction("New")
        self.fileMenuOpenAction = self.fileMenu.addAction("Open")
        self.fileMenuSaveAction = self.fileMenu.addAction("Save")
        self.fileMenuSaveAsAction = self.fileMenu.addAction("SaveAs..")
        self.fileMenuQuitAction = self.fileMenu.addAction("Quit")
        
        self.fileMenuQuitAction.triggered.connect(self.quitApp)

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
        
    def quitApp(self):
        self.app.quit()