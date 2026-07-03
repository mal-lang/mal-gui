from malsim import policies

from .attacker_item import AttackerItem


class MetaDetectorItem(AttackerItem):
    TITLE = "Meta Detector"
    HEADER_COLOR = (255, 165, 0)
    ITEM_KIND = "meta_detector"

    def __init__(
        self,
        name: str,
        image_path: str,
        connections=None,
        connection_labels=None,
        entry_points=None,
        goals=None,
        policy=None,
        parent=None,
    ):
        super().__init__(
            name,
            image_path,
            entry_points=entry_points,
            goals=goals,
            policy=policy or policies.PassiveAgent,
            parent=parent,
        )
        self.connected_assets: list[str] = list(connections) if connections else []
        self.connected_asset_labels: dict[str, int] = {
            asset_name: int(label)
            for asset_name, label in (connection_labels or {}).items()
        }
        for asset_name in self.connected_assets:
            self.connected_asset_labels.setdefault(asset_name, 1)

    def get_item_attribute_values(self) -> dict[str, dict]:
        return {
            "name": {"value": self.name, "editable": False},
            "connections": {"value": self.connected_assets, "editable": False},
            "connection labels": {
                "value": self.connected_asset_labels,
                "editable": False,
            },
        }
