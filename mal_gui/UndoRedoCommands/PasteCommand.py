import json

from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QPointF

from ..ConnectionItem import AssociationConnectionItem

class PasteCommand(QUndoCommand):
    def __init__(self, scene, position, clipboard, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.position = position
        self.pastedItems = []
        self.pastedConnections = []
        self.clipboard = clipboard
        
    def redo(self):
        
        print("\nPaste Redo is Called")
        serializedData = self.clipboard.text()
        print("\nSerializedData = " + str(len(serializedData)))
        print("\nSerializedData = " + str(serializedData))
        if serializedData:
            self.deserializedData = self.scene.deserializeGraphicsItems(serializedData)
            print(json.dumps(self.deserializedData, indent = 2))
            newItemMap = {}  # Map old assetId to new item

            # First pass: create items with new assetIds
            for data in self.deserializedData:
                assetType = data['assetType']
                oldAssetSequenceId = data['assetSequenceId']
                assetProperties = data['assetProperties']

                positionTuple = data['position']
                position = QPointF(positionTuple[0], positionTuple[1])

                # AddAsset Equivalent - Start - To Be Discussed
                if assetType == "Attacker":
                    # newAttackerAttachment = AttackerAttachment()
                    # self.scene.model.add_attacker(newAttackerAttachment)

                    newItem = self.scene.assetFactory.getAsset(assetType)
                    # newItem.assetName = "Attacker"
                    # newItem.typeTextItem.setPlainText(str("Attacker"))
                    newItem.setPos(position)
                    # self.scene._attacker_id_to_item[newAttackerAttachment.id] = newItem
                else:
                    newItem = self.scene.addAsset(assetType, position)
                    #we can assign the properties to new asset
                    for propertyKey,propertyValue in assetProperties:
                        setattr(newItem.asset, propertyKey, float(propertyValue))
                
                self.pastedItems.append(newItem)
                newItemMap[oldAssetSequenceId] = newItem  # Map old assetId to new item
                
                #AddAsset Equivalent - End
                    
            #Adjust the position of all assetItems with offset values
            # Find the top-leftmost position among the items to be pasted
            minX = min(item.pos().x() for item in self.pastedItems)
            minY = min(item.pos().y() for item in self.pastedItems)
            topLeft = QPointF(minX, minY)
            
            # Calculate the offset from the top-leftmost position to the paste position
            offset = self.position - topLeft  
            
            for item in self.pastedItems:
                item.setPos(item.pos() + offset)
                #Ideally After this newAsset.extras and position should be filled- To be discussed
                self.scene.addItem(item)      

            # Second pass: re-establish connections with new assetSequenceIds
            for data in self.deserializedData:
                for conn in data['connections']:
                    print(f'CONN: {conn}')
                    oldStartId = data['assetSequenceId']
                    oldEndId, oldLabel = conn[1], conn[2]
                    newStartItem = newItemMap[oldStartId]
                    newEndItem = newItemMap[oldEndId]

                    #Avoid Self reference
                    if newStartItem != newEndItem:
                        newConnection = AssociationConnectionItem(oldLabel,
                            newStartItem,
                            newEndItem,
                            self.scene
                        )
                        self.scene.addItem(newConnection)
                        self.pastedConnections.append(newConnection)
                        assocType = oldLabel.split('-->')[1]
                        print(f'ASSOC TYPE {assocType}')
                        association = getattr(self.scene.lcs.ns, assocType)()
                        leftAsset = newStartItem.asset
                        rightAsset = newEndItem.asset
                        print(f'LEFT ASSET NAME:{leftAsset.name} ID:{leftAsset.id} TYPE:{leftAsset.type}')
                        print(f'RIGHT ASSET NAME:{rightAsset.name} ID:{rightAsset.id} TYPE:{rightAsset.type}')
                        leftFieldname, rightFieldname = \
                            self.scene.model.get_association_field_names(
                                association
                            )
                        setattr(association, leftFieldname, [leftAsset])
                        setattr(association, rightFieldname, [rightAsset])
                        self.scene.model.add_association(association)
                        newConnection.association = association

        
        #Update the Object Explorer when number of items change
        self.scene.mainWindow.updateChildsInObjectExplorerSignal.emit()

        

    def undo(self):
        print("\nPaste Undo is Called")
        if self.pastedItems:
            print("Undo - Pasted Asset found")
            for conn in self.pastedConnections:
                conn.removeLabels()
                self.scene.removeItem(conn)
                self.scene.model.remove_association(conn.association)
            for item in self.pastedItems:
                self.scene.removeItem(item)
                self.scene.model.remove_asset(item.asset)
            self.pastedItems = []
            self.pastedConnections = []
        
        #Update the Object Explorer when number of items change
        self.scene.mainWindow.updateChildsInObjectExplorerSignal.emit()
