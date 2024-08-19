from PySide6.QtWidgets import QGraphicsScene, QMenu, QApplication, QGraphicsLineItem,QDialog,QGraphicsRectItem
from PySide6.QtGui import QCursor, QTransform,QAction,QUndoStack,QPen
from PySide6.QtCore import QLineF, Qt, QPointF,QRectF

from ConnectionItem import ConnectionItem
from ConnectionDialog import ConnectionDialog
from ObjectExplorer.AssetBase import AssetBase
from ObjectExplorer.EditableTextItem import EditableTextItem

import pickle
import base64

from UndoRedoCommands.Cut.CutCommand import CutCommand
from UndoRedoCommands.Copy.CopyCommand import CopyCommand
from UndoRedoCommands.Paste.PasteCommand import PasteCommand
from UndoRedoCommands.Delete.DeleteCommand import DeleteCommand
from UndoRedoCommands.Move.MoveCommand import MoveCommand
from UndoRedoCommands.DragDrop.DragDropCommand import DragDropCommand
from UndoRedoCommands.CreateConnection.CreateConnectionCommand import CreateConnectionCommand
from UndoRedoCommands.DeleteConnection.DeleteConnectionCommand import DeleteConnectionCommand


from maltoolbox.language import LanguageGraph, LanguageClassesFactory
from maltoolbox.model import Model, AttackerAttachment

class ModelScene(QGraphicsScene):
    def __init__(self, assetFactory,langGraph, lcs,model, mainWindow):
        super().__init__()

        self.assetFactory = assetFactory
        self.undoStack = QUndoStack(self)
        self.clipboard = QApplication.clipboard()
        self.mainWindow = mainWindow

        # # Create the MAL language graph, language classes factory, and
        # # instance model
        # self.langGraph = LanguageGraph.from_mar_archive("langs/org.mal-lang.coreLang-1.0.0.mar")
        # self.lcs = LanguageClassesFactory(self.langGraph)
        # self.model = Model("Untitled Model", self.lcs)
        
        
        # # Assign the MAL language graph, language classes factory, and
        # # instance model
        self.langGraph = langGraph
        self.lcs = lcs
        self.model = model
        
        
        self._asset_id_to_item = {}
        self._attacker_id_to_item = {}

        self.copiedItem = None
        self.cutItemFlag = False

        self.lineItem = None
        self.startItem = None
        self.endItem = None

        # self.objdetails = {}

        self.movingItem = None
        self.startPos = None

        self.showAssociationCheckBoxStatus = False
        
        #For multiple select and handle
        self.selectionRect = None
        self.origin = QPointF()
        self.isDraggingItem = False
        self.draggedItems = []
        self.initialPositions = {}

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        print("dropEvent")
        if event.mimeData().hasFormat('text/plain'):
            print("format is text/plain")
            itemType = event.mimeData().text()
            print("dropped item type = "+ itemType)
            pos = event.scenePos()

            if itemType == "Attacker":
                self.addAttacker(pos)
            else:
                self.addAsset(itemType, pos)

            event.acceptProposedAction()
    
    def addAsset(self, itemType, position, name = None):
        newAsset = getattr(self.lcs.ns, itemType)(name = name)
        self.model.add_asset(newAsset)
        # newAsset.extras = {
        #     "position" :
        #     {
        #         "x": position.x(),
        #         "y": position.y()
        #     }
        # }
        newItem = self.createItem(
            itemType,
            position,
            newAsset.name
        )
        newItem.asset = newAsset
        self._asset_id_to_item[newAsset.id] = newItem
        return newItem
    
    def assignPositionToAssetsWithoutPosition(self,assetsWithoutPosition,xMax,yMax):
        distanceBetweenTwoAssetsVertically = 200
        
        for i, asset in enumerate(assetsWithoutPosition):  
            xPos = xMax
            yPos = yMax + (i* distanceBetweenTwoAssetsVertically)
            print("In xPos= "+ str(xPos))
            print("In yPos= "+ str(yPos))
            asset.setPos(QPointF(xPos,yPos))
            

        

    def drawModel(self):
        
        assetsWithoutPosition = []
        xMax = 0
        yMax = 0
        
        for asset in self.model.assets:
            
            if 'position' in asset.extras:
                pos = QPointF(asset.extras['position']['x'],
                    asset.extras['position']['y'])
                
                #Storing xMax and yMax to be used at the end for moving the assets without position
                if xMax< asset.extras['position']['x']:
                    xMax = asset.extras['position']['x']
                    print("xMax = "+ str(xMax))
                if yMax < asset.extras['position']['y']:
                    yMax = asset.extras['position']['y']
                    print("yMax = "+ str(yMax))
                
            else:
                pos = QPointF(0,0)
            
            newItem = self.createItem(
                asset.type,
                pos,
                asset.name
            )
            newItem.asset = asset
            self._asset_id_to_item[asset.id] = newItem
            
            # extract assets without position
            if 'position' not in asset.extras:
                assetsWithoutPosition.append(newItem)
        
        
        self.assignPositionToAssetsWithoutPosition(assetsWithoutPosition,xMax, yMax)

        for assoc in self.model.associations:
            leftFieldName, rightFieldName = \
                self.model.get_association_field_names(
                    assoc
                )
            leftField = getattr(assoc, leftFieldName)
            rightField = getattr(assoc, rightFieldName)

            for leftAsset in leftField:
                for rightAsset in rightField:
                    assocText = str(leftAsset.name) + "." + \
                        leftFieldName + "-->" + \
                        assoc.__class__.__name__ + "-->" + \
                        rightAsset.name  + "." + \
                        rightFieldName

                    self.addConnection(
                        assocText,
                        self._asset_id_to_item[leftAsset.id],
                        self._asset_id_to_item[rightAsset.id]
                    )


    def addConnection(
        self,
        assocText,
        startItem,
        endItem
    ):
        connection = ConnectionItem(
            assocText,
            startItem,
            endItem,
            self
        )

        self.addItem(connection)
        connection.restoreLabels()
        connection.updatePath()
        return connection


    def addAttacker(self, position, name = None):
        newAttackerAttachment = AttackerAttachment()
        self.model.add_attacker(newAttackerAttachment)
        newItem = self.createItem(
            "Attacker",
            position,
            newAttackerAttachment.name
        )
        newItem.attackerAttachment = newAttackerAttachment
        self._attacker_id_to_item[newAttackerAttachment.id] = newItem

    def createItem(self, itemType, position, name):
        newItem = self.assetFactory.getAsset(itemType)
        newItem.assetName = name
        newItem.typeTextItem.setPlainText(str(name))
        newItem.setPos(position)
        # self.addItem(newItem)
        self.undoStack.push(DragDropCommand(self, newItem))  # Add the drop as a command
        return newItem


    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if item:
            if isinstance(item, (AssetBase,EditableTextItem)):
                if isinstance(item, EditableTextItem):
                    # If right-clicked on EditableTextItem, get its parent which is AssetBase
                    item = item.parentItem()
                item.setSelected(True)
                print("Found Asset", item)
                # self.showAssetContextMenu(event.screenPos(), item)
                self.showAssetContextMenu(event.screenPos())
            elif isinstance(item, ConnectionItem):
                print("Found Connection Item", item)
                self.showConnectionItemContextMenu(event.screenPos(), item)
        else:
            self.showSceneContextMenu(event.screenPos(),event.scenePos())



    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Press event")
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, (AssetBase,EditableTextItem)):
                if isinstance(item, EditableTextItem):
                    # If clicked on EditableTextItem, get its parent which is AssetBase
                    assetItem = item.parentItem()
                    if isinstance(assetItem, AssetBase):
                        self.startItem = assetItem
                    else:
                        return  # Ignore clicks on items that are not AssetBase or its EditableTextItem
                else:
                    self.startItem = item
                self.lineItem = QGraphicsLineItem()
                self.lineItem.setLine(QLineF(event.scenePos(), event.scenePos()))
                self.addItem(self.lineItem)
                print(f"Start item set: {self.startItem}")
                return #Fix: Without this return the AssetBaseItem was moving along while drawing line.
        elif event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos(), QTransform())
            if item and isinstance(item, (AssetBase, EditableTextItem)):
                if isinstance(item, EditableTextItem):
                    assetItem = item.parentItem()
                    if isinstance(assetItem, AssetBase):
                        item = assetItem
                    else:
                        return
                if item.isSelected():
                    print("Item is already selected")
                    self.movingItem = item
                    self.startPos = item.pos()
                    self.draggedItems = [i for i in self.selectedItems() if isinstance(i, AssetBase)]
                    self.initialPositions = {i: i.pos() for i in self.draggedItems}
                else:
                    print("Item is not selected")
                    self.clearSelection()
                    item.setSelected(True)
                    self.movingItem = item
                    self.startPos = item.pos()
                    self.draggedItems = [item]
                    self.initialPositions = {item: item.pos()}
            else:
                self.clearSelection()  # Deselect all items if clicking outside any item
                self.origin = event.scenePos()
                self.selectionRect = QGraphicsRectItem(QRectF(self.origin, self.origin))
                self.selectionRect.setPen(QPen(Qt.blue, 2, Qt.DashLine))
                self.addItem(self.selectionRect)
        elif event.button() == Qt.RightButton:
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if item and isinstance(item, AssetBase):
                if not item.isSelected():
                    self.clearSelection()
                    item.setSelected(True)
                    
        self.showItemDetails()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.lineItem and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Move event")
            self.lineItem.setLine(QLineF(self.lineItem.line().p1(), event.scenePos()))
        elif self.movingItem and not QApplication.keyboardModifiers() == Qt.ShiftModifier:
            newPos = event.scenePos()
            delta = newPos - self.startPos
            for item in self.draggedItems:
                item.setPos(self.initialPositions[item] + delta)
        elif self.selectionRect and not self.movingItem:
            rect = QRectF(self.origin, event.scenePos()).normalized()
            self.selectionRect.setRect(rect)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.lineItem and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Entered Release with Shift")
            print("Scene Mouse Release event")
            
            # Temporarily remove the line item to avoid interference
            self.removeItem(self.lineItem)
            
            item = self.itemAt(event.scenePos(), QTransform())
            print(f"item is: {item}")
            if isinstance(item, (AssetBase,EditableTextItem)) and item != self.startItem:
                print(f"End item found: {item}")
                if isinstance(item, EditableTextItem):
                    # If clicked on EditableTextItem, get its parent which is AssetBase
                    assetItem = item.parentItem()
                    if isinstance(assetItem, AssetBase):
                        self.endItem = assetItem
                    else:
                        self.endItem = None
                else:
                    self.endItem = item
                
                # Create and show the connection dialog
                if self.endItem:
                    dialog = ConnectionDialog(self.startItem, self.endItem,self.langGraph, self.lcs,self.model)
                    if dialog.exec() == QDialog.Accepted:
                        selectedItem = dialog.associationListWidget.currentItem()
                        if selectedItem:
                            print("Selected Association Text is: "+ selectedItem.text())
                            # connection = ConnectionItem(selectedItem.text(),self.startItem, self.endItem,self)
                            # self.addItem(connection)
                            command = CreateConnectionCommand(
                                self,
                                self.startItem,
                                self.endItem,
                                selectedItem.text(),
                                selectedItem.association
                            )
                            self.undoStack.push(command)
                        else:
                            print("No end item found")
                            self.removeItem(self.lineItem)
                else:
                    print("No end item found")
                    self.removeItem(self.lineItem)
                self.lineItem = None
                self.startItem = None
                self.endItem = None  
        elif event.button() == Qt.LeftButton:
            if self.selectionRect:
                items = self.items(self.selectionRect.rect(), Qt.IntersectsItemShape)
                for item in items:
                    if isinstance(item, AssetBase):
                        item.setSelected(True)
                self.removeItem(self.selectionRect)
                self.selectionRect = None
            elif self.movingItem and not QApplication.keyboardModifiers() == Qt.ShiftModifier:
                endPositions = {item: item.pos() for item in self.draggedItems}
                if self.initialPositions != endPositions:
                    command = MoveCommand(self, self.draggedItems, self.initialPositions, endPositions)
                    self.undoStack.push(command)
            self.movingItem = None    
                 
        self.showItemDetails()
        super().mouseReleaseEvent(event)

    def cutAssets(self, selectedAssets):
        print("Cut Asset is called..") 
        command = CutCommand(self, selectedAssets,self.clipboard)
        self.undoStack.push(command)

    def copyAssets(self, selectedAssets):
        print("Copy Asset is called..")
        command = CopyCommand(self, selectedAssets,self.clipboard)
        self.undoStack.push(command)
    
    def pasteAssets(self, position):
        print("Paste is called")
        command = PasteCommand(self, position, self.clipboard)
        self.undoStack.push(command) 
        
    def deleteAssets(self, selectedAssets):
        print("Delete asset is called..")
        command = DeleteCommand(self, selectedAssets)
        self.undoStack.push(command)

    def serializeGraphicsItems(self, items, cutIntended):
        objdetails = []
        selectedSequenceIds = {item.assetSequenceId for item in items}  # Set of selected item IDs
        for item in items:
            
            # Convert assetName to a string - This is causing issue with Serialization 
            assetNameStr = str(item.assetName)
            
            propertyKeysToIgnore = ['id','type']
            
            itemDetails = {
                'assetType': item.assetType,
                'assetName': assetNameStr,
                'assetSequenceId': item.assetSequenceId,
                'position': (item.pos().x(), item.pos().y()),
                'connections': [
                        (conn.startItem.assetSequenceId, conn.endItem.assetSequenceId, '-->'.join(conn.associationDetails))
                        for conn in item.connections
                        if conn.startItem.assetSequenceId in selectedSequenceIds and conn.endItem.assetSequenceId in selectedSequenceIds                    
                    ],
                'assetProperties': [
                    (str(key),str(value))
                    for key,value in item.asset._properties.items()
                    if key not in propertyKeysToIgnore 
                ]
            }
            objdetails.append(itemDetails)
            
        serializedData = pickle.dumps(objdetails)
        base64SerializedData = base64.b64encode(serializedData).decode('utf-8')
        return base64SerializedData
    
    def deserializeGraphicsItems(self, assetText):
        # Fix padding if necessary- I was getting padding error 
        paddingNeeded = len(assetText) % 4
        if paddingNeeded:
            assetText += '=' * (4 - paddingNeeded)

        serializedData = base64.b64decode(assetText)
        deserializedData = pickle.loads(serializedData)

        return deserializedData

    def deleteConnection(self, conectionItemToBeDeleted):
        print("Delete Connection is called..") 
        command = DeleteConnectionCommand(self, conectionItemToBeDeleted)
        self.undoStack.push(command)

    def showAssetContextMenu(self, position):
        print("Asset Context menu activated")
        menu = QMenu()
        assetCutAction = QAction("Cut Asset", self)
        assetCopyAction = QAction("Copy Asset", self)
        assetDeleteAction = QAction("Delete Asset", self)
        
        menu.addAction(assetCutAction)
        menu.addAction(assetCopyAction)
        menu.addAction(assetDeleteAction)
        action = menu.exec(position) 
        
        selectedItems = self.selectedItems()  # Get all selected items
        
        if action == assetCutAction:
            self.cutAssets(selectedItems)
        if action == assetCopyAction:
           self.copyAssets(selectedItems)
        if action == assetDeleteAction:
           self.deleteAssets(selectedItems)
           
    def showConnectionItemContextMenu(self,position, connectionItem):
        print("ConnectionItem Context menu activated")
        menu = QMenu()
        connectionItemDeleteAction = QAction("Delete Connection", self)
        
        menu.addAction(connectionItemDeleteAction)
        action = menu.exec(position)
        
        #In future we may want more option. So "if" condition.
        if action == connectionItemDeleteAction:
            self.deleteConnection(connectionItem)

    def showSceneContextMenu(self, screenPos,scenePos):
        print("Scene Context menu activated")
        menu = QMenu()
        assetPasteAction = menu.addAction("Paste Asset")
        action = menu.exec(screenPos)

        if action == assetPasteAction:
            # self.requestpasteAsset.emit(scenePos)
            self.pasteAssets(scenePos)

    def setShowAssociationCheckBoxStatus(self,isEnabled):
        self.showAssociationCheckBoxStatus = isEnabled

    def getShowAssociationCheckBoxStatus(self):
        return self.showAssociationCheckBoxStatus
    
    def showItemDetails(self):
        selectedItems = self.selectedItems()
        if len(selectedItems) == 1:
            item = selectedItems[0]
            if isinstance(item, AssetBase):
                # self.mainWindow is a reference to main window
                self.mainWindow.itemDetailsWindow.updateItemDetailsWindow(item)
                self.mainWindow.updatePropertiesWindow(item)
        else:
            self.mainWindow.itemDetailsWindow.updateItemDetailsWindow(None)
            self.mainWindow.updatePropertiesWindow(None)

