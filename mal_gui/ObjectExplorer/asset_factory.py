from collections import namedtuple
from .asset_base import AssetBase

class AssetFactory():
    def __init__(self, parent=None):
        self.assetRegistry = {}
        self.assetInfo = namedtuple('AssetInfo', ['assetType', 'assetName', 'assetImage'])

    def addKeyValueToAssetRegistry(self,key,value):
        if key not in self.assetRegistry:
            self.assetRegistry[key] = set()

        if value not in self.assetRegistry[key]:
            self.assetRegistry[key].add(value)
            return True

        return False

    def registerAsset(self,assetName,imagePath):
        self.addKeyValueToAssetRegistry(assetName, self.assetInfo(assetName,assetName,imagePath))


    def getAsset(self,assetNameRequested):
        assetType = None
        assetName = None
        assetImage = None

        if assetNameRequested in self.assetRegistry:
            for value in self.assetRegistry[assetNameRequested]:
                assetType = value.assetType
                assetName = value.assetName
                assetImage = value.assetImage
            # return AssetBase(assetType,assetName,assetImage)
            requestedAsset = AssetBase(assetType, assetName, assetImage)
            requestedAsset.build()
            return requestedAsset

