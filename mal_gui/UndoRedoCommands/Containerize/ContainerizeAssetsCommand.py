from PySide6.QtGui import QUndoCommand
from AssetsContainer.AssetsContainer import AssetsContainer
from PySide6.QtCore import QPointF, QTimer
from ObjectExplorer.AssetBase import AssetBase

class ContainerizeAssetsCommand(QUndoCommand):
    def __init__(self, scene, items, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.items = [item for item in items if item.assetType != 'Attacker']
        self.connections = []
        self.centroid = QPointF(0,0)
        
        #Timer specific values for animation
        self.animationDuration = 2000 # in milliseconds
        self.animationTimerInterval = 20 # in milliseconds
        self.numberOfStepsForTheAnimation = self.animationDuration // self.animationTimerInterval  # Number of steps for the animation


        # # Save connections of all items
        for item in self.items:
            if hasattr(item, 'connections'):
                self.connections.extend(item.connections.copy())
                
        self.newAssetsContainer = AssetsContainer("AssetContainer", "ContainerName", "images/assetContainer.png","images/assetContainerPlusSymbol.png","images/assetContainerMinusSymbol.png")
        self.newAssetsContainer.build()

    def redo(self):
        #Find the centroid of all Assets to be containerized where Container will appear
        xCoordinatesListOfAssets = [item.scenePos().x() for item in self.items]
        yCoordinatesListOfAssets = [item.scenePos().y() for item in self.items]
        centerX = sum(xCoordinatesListOfAssets) / len(xCoordinatesListOfAssets)
        centerY = sum(yCoordinatesListOfAssets) / len(yCoordinatesListOfAssets)
        self.centroid = QPointF(centerX, centerY)
        
        #Display the container at centroid location
        self.scene.addItem(self.newAssetsContainer)
        self.newAssetsContainer.setPos(self.centroid)
        
        for item in self.items:
            if isinstance(item,AssetBase):
                self.moveItemFromCurrentPositionToCentroid(item, self.centroid)

    def undo(self):
        # Add items back to the scene
        for itemEntry in self.newAssetsContainer.containerizedAssetsList:
            item = itemEntry['item']
            originalPositionOfItem = self.centroid + itemEntry['offset']
            self.scene.addItem(item)
            item.setPos(originalPositionOfItem)
        
        # Restore connections
        for connection in self.connections:
            self.scene.addItem(connection)
            connection.restoreLabels()
            connection.updatePath()
            
        self.scene.removeItem(self.newAssetsContainer)
    
    
    def updateItemPosition(self, item,  startPos, endPos,isRedo):
        if item.stepCounter >= self.numberOfStepsForTheAnimation:
            item.timer.timeout.disconnect()
            item.timer.stop()
            if isRedo:
                #Store item and offset because items moving towards centroid
                self.newAssetsContainer.containerizedAssetsList.append({'item': item, 'offset': item.offsetFromCentroid})
                item.setPos(self.centroid)
                self.updateConnections(item)
                
                self.newAssetsContainer.itemMoved = lambda: self.updateItemsPositionRelativeToContainer()
            else:
                self.newAssetsContainer.containerizedAssetsList.clear()
            return
        
        deltaX = (endPos.x() - startPos.x()) / self.numberOfStepsForTheAnimation
        deltaY = (endPos.y() - startPos.y()) / self.numberOfStepsForTheAnimation
        newPos = QPointF(startPos.x() + deltaX, startPos.y() + deltaY)
        item.setPos(newPos)

        item.stepCounter += 1
        
        
    def moveItemFromCurrentPositionToCentroid(self,item,centroid):
        item.timer = QTimer()
        item.stepCounter = 0
        item.offsetFromCentroid = item.scenePos() - centroid
        item.timer.timeout.connect(lambda: self.updateItemPosition(item, item.scenePos(),centroid,isRedo=True))
        item.timer.start(self.animationTimerInterval)
    
    def updateConnections(self, item):
        if hasattr(item, 'connections'):
            for connection in item.connections:
                connection.updatePath()
    
    def updateItemsPositionRelativeToContainer(self):
        for itemEntry in self.newAssetsContainer.containerizedAssetsList:
            item = itemEntry['item']
            item.setPos(self.newAssetsContainer.pos())