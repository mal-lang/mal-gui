from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter


class ModelView(QGraphicsView):
    zoom_changed = Signal(float)

    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)

        self.zoom_factor = 1.0
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._hand_drag_enabled = False

    def zoomIn(self):
        """Overrides base"""
        self.zoom(1.5)  # Akash: This value need to discuss with Andrei

    def zoomOut(self):
        """Overrides base"""
        self.zoom(1 / 1.5)  # Akash: This value need to discuss with Andrei

    def wheelEvent(self, event):
        """Overrides base"""
        if event.angleDelta().y() > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    def zoom(self, factor):
        """Zoom one step with given factor"""
        self.zoom_factor *= factor
        self.scale(factor, factor)
        self.zoom_changed.emit(self.zoom_factor)

    def set_zoom(self, zoom_percentage):
        """Set zoom to certain value"""
        factor = zoom_percentage / 100.0
        self.scale(factor / self.zoom_factor, factor / self.zoom_factor)
        self.zoom_factor = factor
        self.zoom_changed.emit(self.zoom_factor)

    def set_hand_drag_enabled(self, enabled: bool):
        """Enable or disable hand drag mode"""
        self._hand_drag_enabled = enabled
        self.setDragMode(
            QGraphicsView.ScrollHandDrag if enabled else QGraphicsView.NoDrag
        )
        self.setCursor(Qt.OpenHandCursor if enabled else Qt.ArrowCursor)
        if enabled:
            self._ensure_scene_rect_margin()

    def _ensure_scene_rect_margin(self):
        """Ensure that the scene rect has a margin around the items to allow for panning when hand drag is enabled."""
        scene = self.scene()
        if scene is None:
            return
        items_rect = scene.itemsBoundingRect()
        view_rect = self.viewport().rect()
        margin = max(200, int(max(view_rect.width(), view_rect.height()) * 0.5))
        padded = items_rect.adjusted(-margin, -margin, margin, margin)
        scene_rect = scene.sceneRect()
        if scene_rect.isNull():
            scene.setSceneRect(padded)
            return
        if not scene_rect.contains(padded):
            scene.setSceneRect(scene_rect.united(padded))

    def resizeEvent(self, event):
        """Overrides base"""
        super().resizeEvent(event)
        if self._hand_drag_enabled:
            self._ensure_scene_rect_margin()

    # Handling all the mouse press/move/release event to QGraphicsScene ( ModelScene) derived class to avoid
    # collision of functionality in 2 different places( ModelView vs ModelScene).