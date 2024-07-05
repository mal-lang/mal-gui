from PySide6.QtWidgets import QGraphicsScene, QMenu, QApplication, QGraphicsLineItem,QDialog
from PySide6.QtGui import QCursor, QTransform,QAction,QUndoStack
from PySide6.QtCore import QLineF, Qt, QPointF

from ConnectionDialog import ConnectionDialog
from ObjectExplorer.AssetBase import AssetBase

import pickle
import base64

from UndoRedoCommands.Cut.CutCommand import CutCommand
from UndoRedoCommands.Copy.CopyCommand import CopyCommand
from UndoRedoCommands.Paste.PasteCommand import PasteCommand
from UndoRedoCommands.Delete.DeleteCommand import DeleteCommand
from UndoRedoCommands.Move.MoveCommand import MoveCommand
from UndoRedoCommands.DragDrop.DragDropCommand import DragDropCommand
from UndoRedoCommands.CreateConnection.CreateConnectionCommand import CreateConnectionCommand

from maltoolbox.language import LanguageGraph, LanguageClassesFactory
from maltoolbox.model import Model, AttackerAttachment

class ModelScene(QGraphicsScene):
    def __init__(self, assetFactory, mainWindow):
        super().__init__()

        self.assetFactory = assetFactory
        self.undoStack = QUndoStack(self)
        self.clipboard = QApplication.clipboard()
        self.mainWindow = mainWindow

        # Create the MAL language graph, language classes factory, and
        # instance model
        self.langGraph = LanguageGraph.from_mar_archive("langs/org.mal-lang.coreLang-1.0.0.mar")
        self.lcs = LanguageClassesFactory(self.langGraph)
        self.model = Model("Untitled Model", self.lcs)
        self._asset_id_to_item = {}
        self._attacker_id_to_item = {}

        self.copiedItem = None
        self.cutItemFlag = False

        self.lineItem = None
        self.startItem = None
        self.endItem = None

        self.objdetails = {}

        self.movingItem = None
        self.startPos = None

        self.showAssociationCheckBoxStatus = False

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
        newAsset.extras = {
            "position" :
            {
                "x": position.x(),
                "y": position.y()
            }
        }
        newItem = self.createItem(
            itemType,
            position,
            newAsset.name
        )
        newItem.asset = newAsset
        self._asset_id_to_item[newAsset.id] = newItem

    def drawModel(self):
        for asset in self.model.assets:
            newItem = self.createItem(
                asset.type,
                QPointF(asset.extras['position']['x'],
                    asset.extras['position']['y']),
                asset.name
            )
            newItem.asset = asset
            self._asset_id_to_item[asset.id] = newItem

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

                    command = CreateConnectionCommand(
                        self,
                        self._asset_id_to_item[leftAsset.id],
                        self._asset_id_to_item[rightAsset.id],
                        assocText
                    )
                    self.undoStack.push(command)

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
        self.addItem(newItem)
        self.undoStack.push(DragDropCommand(self, newItem))  # Add the drop as a command
        return newItem


    def contextMenuEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if item:
            if isinstance(item, AssetBase):
                print("Found Asset", item)
                self.showAssetContextMenu(event.screenPos(), item)
        else:
            self.showSceneContextMenu(event.screenPos(),event.scenePos())



    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Press event")
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, AssetBase):
                self.startItem = item
                self.lineItem = QGraphicsLineItem()
                self.lineItem.setLine(QLineF(event.scenePos(), event.scenePos()))
                self.addItem(self.lineItem)
                print(f"Start item set: {self.startItem}")
        elif event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos(), QTransform())
            if item and isinstance(item, AssetBase):
                self.movingItem = item
                self.startPos = item.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.lineItem and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Scene Mouse Move event")
            self.lineItem.setLine(QLineF(self.lineItem.line().p1(), event.scenePos()))
        elif self.movingItem:
            newPos = event.scenePos()
            self.movingItem.setPos(newPos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.lineItem and QApplication.keyboardModifiers() == Qt.ShiftModifier:
            print("Entered Release with Shift")
            print("Scene Mouse Release event")

            # Temporarily remove the line item to avoid interference
            self.removeItem(self.lineItem)

            item = self.itemAt(event.scenePos(), QTransform())
            print(f"item is: {item}")
            if isinstance(item, AssetBase) and item != self.startItem:
                print(f"End item found: {item}")
                self.endItem = item

                # Create and show the connection dialog
                dialog = ConnectionDialog(
                    self.startItem,
                    self.endItem,
                    self
                )
                if dialog.exec() == QDialog.Accepted:
                    selectedItem = dialog.associationListWidget.currentItem()
                    if selectedItem:
                        print("Selected Association Text is: "+ selectedItem.text())
                        command = CreateConnectionCommand(
                            self,
                            self.startItem,
                            self.endItem,
                            selectedItem.text()
                        )
                        self.undoStack.push(command)
                    else:
                        self.removeItem(self.lineItem)
            else:
                print("No end item found")
                self.removeItem(self.lineItem)
            self.lineItem = None
            self.startItem = None
            self.endItem = None
        elif event.button() == Qt.LeftButton and self.movingItem:
            endPos = self.movingItem.pos()
            if self.startPos != endPos:
                command = MoveCommand(self,self.movingItem, self.startPos, endPos)
                self.undoStack.push(command)
            self.movingItem = None
        else:
            super().mouseReleaseEvent(event)

    def cutAsset(self, asset):
        print("Cut Asset is called..")
        command = CutCommand(self, asset,self.clipboard)
        self.undoStack.push(command)

    def copyAsset(self, asset):
        print("Copy Asset is called..")
        command = CopyCommand(self, asset,self.clipboard)
        self.undoStack.push(command)

    def pasteAsset(self, position):
        print("Paste is called")
        command = PasteCommand(self, position, self.clipboard)
        self.undoStack.push(command)

    def deleteAsset(self, asset):
        print("Delete asset is called..")
        command = DeleteCommand(self, asset)
        self.undoStack.push(command)

    def serializeGraphicsItem(self, item, cutIntended):
        # objType = type(item).__name__
        # print("objType is: "+ objType)
        print("assetType is: "+ item.assetType)
        self.objdetails['assetType'] = item.assetType
        self.objdetails['assetName'] = item.assetName
        if cutIntended:
            self.objdetails['assetId'] = 5 #This is a ID already generated from mal-toolbox
        else:
            self.objdetails['assetId'] = 6 #This is a ID which will newly be generated from mal-toolbox
        serializedData = pickle.dumps(self.objdetails)
        base64SerializedData = base64.b64encode(serializedData).decode('utf-8')
        return base64SerializedData


    def deserializeGraphicsItem(self, assetText):
        serializedData = base64.b64decode(assetText)
        deserializedData = pickle.loads(serializedData)
        deserializedAssetType = deserializedData['assetType']
        deserializedAssetName = deserializedData['assetName']
        deserializedAssetId = deserializedData['assetId']


        print("deserializedAssetType = "+ deserializedAssetType)
        if deserializedAssetType:
            newItem = self.assetFactory.getAsset(deserializedAssetType)
            # self.addItem(newItem)
            if isinstance(newItem,AssetBase):
                print("It is instance of AssetBase")

            # This below rename currently doesn't work. Need to check why.
            # print("newItem.assetName =" + newItem.assetName)
            # newItem.assetName = deserializedAssetName
            # print("newItem.assetName =" + newItem.assetName)
            return newItem


    def showAssetContextMenu(self, position, asset):
        print("Asset Context menu activated")
        menu = QMenu()
        assetCutAction = QAction("Cut Asset", self)
        assetCopyAction = QAction("Copy Asset", self)
        assetDeleteAction = QAction("Delete Asset", self)

        menu.addAction(assetCutAction)
        menu.addAction(assetCopyAction)
        menu.addAction(assetDeleteAction)
        action = menu.exec(position)

        if action == assetCutAction:
            self.cutAsset(asset)
        if action == assetCopyAction:
           self.copyAsset(asset)
        if action == assetDeleteAction:
           self.deleteAsset(asset)

    def showSceneContextMenu(self, screenPos,scenePos):
        print("Scene Context menu activated")
        menu = QMenu()
        pasteAssetAction = menu.addAction("Paste Asset")
        action = menu.exec(screenPos)

        if action == pasteAssetAction:
            # self.requestpasteAsset.emit(scenePos)
            self.pasteAsset(scenePos)

    def setShowAssociationCheckBoxStatus(self,isEnabled):
        self.showAssociationCheckBoxStatus = isEnabled

    def getShowAssociationCheckBoxStatus(self):
        return self.showAssociationCheckBoxStatus

