from PySide6.QtWidgets import QWidget,QSplitter, QMainWindow,QToolBar,QDockWidget, QListWidget,QVBoxLayout,QComboBox,QListWidgetItem, QLabel,QTreeView,QTreeWidget, QTreeWidgetItem,QCheckBox
from PySide6.QtGui import QDrag,QPixmap
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
        
        #Menubar and menus 
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("File")
        file_menu_new_action = file_menu.addAction("New")
        file_menu_open_action = file_menu.addAction("Open")
        file_menu_save_action = file_menu.addAction("Save")
        file_menu_saveas_action = file_menu.addAction("SaveAs..")
        file_menu_quit_action = file_menu.addAction("Quit")
        file_menu_quit_action.triggered.connect(self.quit_app)
        
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu_copy_action = edit_menu.addAction("Copy")
        edit_menu_cut_action = edit_menu.addAction("Cut")
        edit_menu_paste_action= edit_menu.addAction("Paste")
        edit_menu_undo_action = edit_menu.addAction("Undo")
        edit_menu_redo_action = edit_menu.addAction("Redo")
        
        settings_menu = menu_bar.addMenu("Settings")
        settings_menu.addAction("View")
        
        help_menu = menu_bar.addMenu("Help")
        help_menu_about_action = help_menu.addAction("About1")
        help_menu_about_action2 = help_menu.addAction("About2")
        help_menu_tbd2_action = help_menu.addAction("TBD_2")
        help_menu_tbd2_action = help_menu.addAction("TBD_3")
        
        #working with toolbars 
        toolbar = QToolBar("My main Toolbar")
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)
        
        #Add the quit action 
        toolbar.addAction(file_menu_quit_action)
        
        toolbar.addSeparator()
        
        showAssociationCheckBoxLabel  = QLabel("Show Association")
        showAssociationCheckBox = QCheckBox()
        showAssociationCheckBox.setCheckState(Qt.CheckState.Unchecked)
        toolbar.addWidget(showAssociationCheckBoxLabel)
        toolbar.addWidget(showAssociationCheckBox)
        showAssociationCheckBox.stateChanged.connect(self.showAssociationCheckBoxChanged)
        
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
        self.view = ModelView(self.scene)
        
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
            print(f"Key: {key}")
            for value in values:
                print(f"  Tuple: {value}")
                print(f"    Field1: {value.assetNameUpper}")
                print(f"    Field2: {value.assetNameLower}")
                print(f"    Field3: {value.assetImage}")
                self.objectExplorerTree.setParentItemText(value.assetNameUpper,value.assetImage)
                self.objectExplorerTree.addChildItem(value.assetNameUpper, value.assetNameUpper+ "@Number_TBD")
                
        
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
        

        
    def quit_app(self):
        self.app.quit()