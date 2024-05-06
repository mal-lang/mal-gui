from PySide6.QtWidgets import QMainWindow,QToolBar,QDockWidget, QListWidget, QTextEdit,QTreeView,QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt

from graph import GraphWindow

class MainWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app = app #declare an app member 
        self.setWindowTitle("Custom MainWindow")
        
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
        
        self.graphWindow = GraphWindow()
        self.setCentralWidget(self.graphWindow)
        
        
        # self.setDockNestingEnabled(True)
        # self.setCorner()
        self.dockAble()
    
    def dockAble(self):
        
        # edocTabTree Data
        edocTabTreeData = {
            "Classes": ["TBD_1","TBD_2", "TBD_3"],
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
        
        
        #EDOC Tab with treeeview
        edocTabTree = QTreeWidget()
        edocTabTree.setHeaderLabel(None)
        
        edocTabTreeItems = []
        for key, values in edocTabTreeData.items():
            item = QTreeWidgetItem([key])
            for value in values:
                ext = "ext"
                child = QTreeWidgetItem([value, ext])
                secondLevelChild = QTreeWidgetItem(["another child"])
                child.addChild(secondLevelChild)
                item.addChild(child)
            edocTabTreeItems.append(item)
        edocTabTree.insertTopLevelItems(0,edocTabTreeItems)
        edocTabTree.show()
        
        dockEDOC = QDockWidget("EDOC",self)
        dockEDOC.setWidget(edocTabTree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockEDOC)
                
                
        #Properties Tab with treeview        

        propertiesTabTree = QTreeWidget()
        propertiesTabTree.setHeaderLabel(None)
        propertiesTabTree.setColumnCount(2)
        propertiesTabTree.setHeaderLabels(["Property","Value"])
        
        propertiesTabTreeItems = []
        for key, values in edocTabTreeData.items():
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