from collections import namedtuple
from ObjectExplorer.AssetBase import AssetBase

class AssetFactory():
    def __init__(self, parent=None):
        self.assetRegistry = {}
        self.assetInfo = namedtuple('AssetInfo', ['assetNameUpper', 'assetNameLower', 'assetImage'])
    
    def addKeyValueToAssetRegistry(self,key,value):
        if key not in self.assetRegistry:
            self.assetRegistry[key] = set()
        
        if value not in self.assetRegistry[key]:
            self.assetRegistry[key].add(value)
            return True

        return False
    
    def registerAsset(self,assetName,imagePath):
        self.addKeyValueToAssetRegistry(assetName, self.assetInfo(assetName,assetName,imagePath))
        
    
    def getAsset(self,assetName):
        assetNameUpper = None
        assetNameLower = None
        assetImage = None
        
        if assetName in self.assetRegistry:
            for value in self.assetRegistry[assetName]:
                assetNameUpper = value.assetNameUpper
                assetNameLower = value.assetNameLower
                assetImage = value.assetImage
            return AssetBase(assetNameUpper,assetNameLower,assetImage)
        