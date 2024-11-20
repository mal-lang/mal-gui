from collections import namedtuple
from .asset_base import AssetBase

class AssetFactory():
    def __init__(self, parent=None):
        self.asset_info = namedtuple(
            'AssetInfo', ['asset_type', 'asset_name', 'asset_image'])
        self.asset_registry: dict[self.asset_info] = {}

    def add_key_value_to_asset_registry(self, key, value):
        if key not in self.asset_registry:
            self.asset_registry[key] = set()

        if value not in self.asset_registry[key]:
            self.asset_registry[key].add(value)
            return True

        return False

    def register_asset(self, asset_name, image_path):
        self.add_key_value_to_asset_registry(
            asset_name,
            self.asset_info(asset_name,asset_name,image_path)
        )

    def get_asset(self, asset_name_requested):
        asset_type = None
        asset_name = None
        asset_image = None

        if asset_name_requested in self.asset_registry:
            for value in self.asset_registry[asset_name_requested]:
                asset_type = value.asset_type
                asset_name = value.asset_name
                asset_image = value.asset_image
            # return AssetBase(asset_type,asset_name,asset_image)
            requested_asset = AssetBase(asset_type, asset_name, asset_image)
            requested_asset.build()
            return requested_asset
