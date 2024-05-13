from PySide6.QtWidgets import QWidget,QSplitter, QMainWindow,QToolBar,QDockWidget, QListWidget,QVBoxLayout,QComboBox,QListWidgetItem, QLabel,QTreeView,QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QDrag,QPixmap
from PySide6.QtCore import Qt,QMimeData,QByteArray,QSize

from graph import GraphWindow

import external.qtpynodeeditor as nodeeditor

from malmodels import Attacker,Client,Container,Datastore,Firewall,Host

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
        
        #Add other widgets
        # self.textEdit = QTextEdit()
        # self.setCentralWidget(self.textEdit)
        
        #Main GraphicsViewFramework ( View, Scene and Items related)
        registry = nodeeditor.DataModelRegistry()

        registry.register_model(Attacker, category='Hacking',style=None)
        registry.register_model(Client, category='Hacking',style=None)
        registry.register_model(Container, category='Hacking',style=None)
        registry.register_model(Datastore, category='Hacking',style=None)
        registry.register_model(Firewall, category='Hacking',style=None)
        registry.register_model(Host, category='Hacking',style=None)
            
        self.scene = nodeeditor.FlowScene(registry=registry)
        self.grapicsView = nodeeditor.FlowView(self.scene)
        
        #Simple Graphics with networkx example
        self.graphWindow = GraphWindow()
        # self.setCentralWidget(self.graphWindow)
        
        self.scene = nodeeditor.FlowScene(registry=registry)
        self.grapicsView = nodeeditor.FlowView(self.scene)
        # self.setCentralWidget(self.grapicsView)
        
        self.splitter = QSplitter()
        self.splitter.addWidget(self.grapicsView)
        self.splitter.addWidget(self.graphWindow)
        self.splitter.setSizes([200, 200])  # Set initial sizes of widgets in splitter
        
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
        
    #     templates = [
    #         [
    #             ["Item1_1_1", "Item1_1_2", "Item1_1_3"],
    #             ["Item1_2_1", "Item1_2_2", "Item1_2_3"]
    #         ],
    #         [
    #             ["Item2_1_1", "Item2_1_2", "Item2_1_3"],
    #             ["Item2_2_1", "Item2_2_2", "Item2_2_3"]
    #         ]
    #     ]

    # for template_level_1 in templates:
    #     for template_level_2 in template_level_1:
    #         print("Template:")
    #         for item in template_level_2:
    #             print(item)
    #         print()
    
        #ObjectExplorer ListView ( With Drag And Drop Functionality)
        self.objectExplorerListContent = ["Attacker","Client","Container","Datastore","Firewall","Host"]
        
        # objectExplorerListTab.setHeaderLabel(None)
        dockObjectExplorer = QDockWidget("Object Explorer",self)
        self.objectExplorerListTab = DraggableListWidget(dockObjectExplorer)
        self.objectExplorerListTab.addItems(self.objectExplorerListContent)
        dockObjectExplorer.setWidget(self.objectExplorerListTab)
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
        
        

        
    def quit_app(self):
        self.app.quit()