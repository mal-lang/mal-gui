from __future__ import annotations
from typing import TYPE_CHECKING
from collections import namedtuple

from PySide6.QtCore import QPointF

from ..detectors import DetectorIndex
from .asset_item import AssetItem
from .attacker_item import AttackerItem
from .meta_detector_item import MetaDetectorItem

if TYPE_CHECKING:
    from maltoolbox.model import ModelAsset

AssetInfo = namedtuple("AssetInfo", ["asset_type", "asset_name", "asset_image"])

class AssetFactory:
    def __init__(self, detector_index: DetectorIndex | None = None, parent=None):
        self.asset_registry: dict[str, list[AssetInfo]] = {}
        self.detector_index = detector_index or DetectorIndex()

    def add_key_value_to_asset_registry(self, key, value):
        if key not in self.asset_registry:
            self.asset_registry[key] = []

        if value not in self.asset_registry[key]:
            self.asset_registry[key].append(value)
            return True

        return False

    def register_asset(self, asset_name, image_path):
        self.add_key_value_to_asset_registry(
            asset_name, AssetInfo(asset_name, asset_name, image_path)
        )

    def create_asset_item(self, asset: ModelAsset, pos: QPointF):
        asset_type = asset.lg_asset.name
        asset_info: AssetInfo = self.asset_registry[asset_type][0]
        requested_item = AssetItem(
            asset,
            asset_info.asset_image,
            has_detector=self.detector_index.has_detector(asset_type),
        )

        requested_item.setPos(pos)
        requested_item.type_text_item.setPlainText(asset.name)

        requested_item.build()
        return requested_item

    def create_attacker_item(
        self, name: str, pos: QPointF, entry_points=None, goals=None, policy=None
    ):
        asset_type = "Attacker"
        asset_info: AssetInfo = self.asset_registry[asset_type][0]
        requested_item = AttackerItem(
            name,
            asset_info.asset_image,
            entry_points=entry_points,
            goals=goals,
            policy=policy,
        )

        requested_item.setPos(pos)
        requested_item.type_text_item.setPlainText(name or "Unnamed Attacker")

        requested_item.build()
        return requested_item

    def create_meta_detector_item(
        self,
        name: str,
        pos: QPointF,
        connections=None,
        connection_labels=None,
        entry_points=None,
        goals=None,
        policy=None,
    ):
        asset_type = "Meta Detector"
        asset_info: AssetInfo = self.asset_registry[asset_type][0]
        requested_item = MetaDetectorItem(
            name,
            asset_info.asset_image,
            connections=connections,
            connection_labels=connection_labels,
            entry_points=entry_points,
            goals=goals,
            policy=policy,
        )

        requested_item.setPos(pos)
        requested_item.type_text_item.setPlainText(name or "Unnamed Meta Detector")

        requested_item.build()
        return requested_item
