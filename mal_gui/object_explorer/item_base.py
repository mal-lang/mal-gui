from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod

from PySide6.QtCore import QRectF, Qt, QPointF, QSize, QSizeF, QTimer
from PySide6.QtGui import (
    QPixmap,
    QFont,
    QColor,
    QBrush,
    QPen,
    QPainterPath,
    QFontMetrics,
    QLinearGradient,
    QImage
)
from PySide6.QtWidgets import  QGraphicsItem

from .editable_text_item import EditableTextItem

if TYPE_CHECKING:
    from maltoolbox.model import ModelAsset
    from ..connection_item import IConnectionItem

class ItemBase(QGraphicsItem):

    def __init__(
            self,
            title: str,
            image_path: str,
            parent=None,
        ):
        super().__init__(parent)

        self.setZValue(1)  # rect items are on top

        self.title = title
        self.image_path = image_path

        self.image = self.load_image_with_quality(
            self.image_path, QSize(512, 512)
        )

        self.setFlags(
            QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemSendsGeometryChanges
        )

        # Create the editable text item for block type
        self.type_text_item = EditableTextItem(self.title, self)
        self.type_text_item.lostFocus.connect(self.update_name)

        self.connections: list[IConnectionItem] = []
        self.initial_position = QPointF()

        # Visual Styling
        self.width = 240
        self.height = 70
        self.size = QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

        self.asset_type_background_color = QColor(0, 200, 0) #Green
        self.asset_name_background_color = QColor(20, 20, 20, 200) # Gray

        self.icon_path = None
        self.icon_visible = True
        self.icon_pixmap = QPixmap()

        self.title_path = QPainterPath()  # The path for the title
        self.type_path = QPainterPath()  # The path for the type
        self.status_path = QPainterPath()  # A path showing the status of the node

        self.horizontal_margin = 15  # Horizontal margin
        self.vertical_margin = 15  # Vertical margin

        self.timer = QTimer()
        self.status_color =  QColor(0, 255, 0)
        self.attacker_toggle_state = False
        self.timer.timeout.connect(self.update_status_color)
        #timer to trigger every 500ms (0.5 seconds)
        self.timer.start(500)

        self.build()

    def boundingRect(self):
        """Overrides base method"""
        return self.size

    def paint(self, painter, option, widget=None):
        """Overrides base method"""
        painter.setPen(self.asset_name_background_color.lighter())
        painter.setBrush(self.asset_name_background_color)
        painter.drawPath(self.path)

        gradient = QLinearGradient()
        gradient.setStart(0, -90)
        gradient.setFinalStop(0, 0)
        gradient.setColorAt(0, self.asset_type_background_color)  # Start color
        gradient.setColorAt(1, self.asset_type_background_color.darker())  # End color

        painter.setBrush(QBrush(gradient))
        painter.setPen(self.asset_type_background_color)
        painter.drawPath(self.title_bg_path.simplified())

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.white)
        painter.drawPath(self.title_path)
        painter.drawPath(self.type_path)

        # Draw the status path
        painter.setBrush(self.status_color)
        painter.setPen(self.status_color.darker())
        painter.drawPath(self.status_path.simplified())

        # Draw the icon if it's visible
        if self.icon_visible and not self.image.isNull():
            targetIconSize = QSize(24, 24)  # Desired size for the icon

            # Resize the icon using smooth transformation
            # resizedImageIcon = self.image.scaled(targetIconSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            resizedImageIcon = self.image


            # Calculate the position and size for the icon background
            iconRect = QRectF(-self.width / 2 + 10, -self.height / 2 + 10, targetIconSize.width(), targetIconSize.height())
            margin = 5  # Margin around the icon

            # Draw the background for the icon with additional margin
            backgroundRect = QRectF(
                iconRect.topLeft() - QPointF(margin, margin),
                QSizeF(targetIconSize.width() + 2 * margin, targetIconSize.height() + 2 * margin)
            )
            painter.setBrush(Qt.white)  # Set the brush color to white
            painter.drawRect(backgroundRect.toRect())  # Convert QRectF to QRect and draw the white background rectangle

            # Draw the resized icon on top of the white background
            painter.drawPixmap(iconRect.toRect(), resizedImageIcon)  # Convert QRectF to QRect and draw the resized icon

        # Draw the highlight if selected
        if self.isSelected():
            painter.setPen(QPen(self.asset_type_background_color.lighter(), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path)

    def itemChange(self, change, value):
        """Overrides base method"""
        if change == QGraphicsItem.ItemPositionChange:
            if self.pos() != self.initial_position:
                for connection in self.connections:
                    connection.update_path()
                self.initial_position = self.pos()
            if self.scene():
                self.scene().update()  # Ensure the scene is updated - this fixed trailing borders issue
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.type_text_item.setTextInteractionFlags(
                Qt.TextEditorInteraction
            )
            self.type_text_item.setFocus()
            # Select all text when activated
            self.type_text_item.select_all_text()
            event.accept()
        else:
            event.ignore()

    def focusOutEvent(self, event):
        """Overrides base method"""
        self.type_text_item.clearFocus()
        super().focusOutEvent(event)

    def mousePressEvent(self, event):
        """Overrides base method"""
        self.initial_position = self.pos()

        if (
            self.type_text_item.hasFocus()
            and not self.type_text_item.contains(event.pos())
        ):
            self.type_text_item.clearFocus()
        elif not self.type_text_item.contains(event.pos()):
            self.type_text_item.deselect_text()
        else:
            super().mousePressEvent(event)

    def build(self):
        self.title_text = self.title
        self.title_path = QPainterPath()
        self.type_path = QPainterPath()
        self.status_path = QPainterPath()

        # Set the font for title and category
        title_font = QFont("Arial", pointSize=12)
        type_font = QFont("Arial", pointSize=12)

        # Use fixed width and height
        fixed_width = self.width
        fixed_height = self.height

        # Draw the background of the node
        self.path = QPainterPath()
        self.path.addRoundedRect(
            -fixed_width / 2,
            -fixed_height / 2,
            fixed_width,
            fixed_height,
            6,
            6
        )

        self.title_bg_path = QPainterPath()
        self.title_bg_path.addRoundedRect(
            -fixed_width / 2,
            -fixed_height / 2,
            fixed_width,
            title_font.pointSize() + 2 * self.vertical_margin,
            6,
            6
        )

        # Draw status path
        self.status_path.setFillRule(Qt.WindingFill)
        self.status_path.addRoundedRect(
            fixed_width / 2 - 12,
            -fixed_height / 2 + 2,
            10,
            10,
            2,
            2
        )

        # Center title in the upper half
        title_font_metrics = QFontMetrics(title_font)
        self.title_path.addText(
            # Center horizontally
            -title_font_metrics.horizontalAdvance(self.title_text) / 2,
            # Center vertically within its section
            -fixed_height / 2 + self.vertical_margin + title_font_metrics.ascent(),
            title_font,
            self.title_text
        )

        # Set the font and default color for type_text_item
        self.type_text_item.setFont(type_font)
        self.type_text_item.setDefaultTextColor(Qt.white)

        # Initial position of type_text_item
        self.update_type_text_item_position()

        # Connect lostFocus signal to update position when text loses focus
        self.type_text_item.lostFocus.connect(
            self.update_type_text_item_position)

        # self.widget.move(-self.widget.size().width() / 2,
        # fixed_height / 2 - self.widget.size().height() + 5)


    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)


    def update_type_text_item_position(self):
        # to update the position of the type_text_item so that it
        # remains centered within the lower half of the node
        # whenever the text changes.

        type_font_metrics = QFontMetrics(self.type_text_item.font())
        fixed_height = self.height
        title_font_metrics = QFontMetrics(QFont("Arial", pointSize=12))

        # Calculate the new position for type_text_item
        type_text_item_pos_x = \
            -type_font_metrics.horizontalAdvance(self.type_text_item.toPlainText()) / 2
        type_text_item_pos_y = \
            -fixed_height / 2 + title_font_metrics.height() + 2 * self.vertical_margin

        # Update position
        self.type_text_item.setPos(type_text_item_pos_x, type_text_item_pos_y)

    def update_name(self):
        self.title = self.type_text_item.toPlainText()
        self.type_text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        self.type_text_item.deselect_text()
        self.update_type_text_item_position()

        associated_scene = self.type_text_item.scene()
        if associated_scene:
            print("Asset Name Changed by user")
            associated_scene.main_window\
                .update_childs_in_object_explorer_signal.emit()

    def setIcon(self, icon_path=None):
        """Overrides base method"""
        self.icon_path = icon_path
        if self.image:
            self.icon_pixmap = QPixmap(icon_path)
        else:
            self.icon_pixmap = QPixmap()

    def toggle_icon_visibility(self):
        self.icon_visible = not self.icon_visible
        self.update()

    def update_status_color(self):
        if self.asset_type =='Attacker':
            self.attacker_toggle_state = not self.attacker_toggle_state
            if self.attacker_toggle_state:
                self.status_color =  QColor(0, 255, 0) #Green
            else:
                self.status_color =  QColor(255, 0, 0) #Red

        #Otherwise return Green for all assets
        else:
            self.status_color =  QColor(0, 255, 0)

        self.update()

    def load_image_with_quality(self, path, size):
        image = QImage(path)
        if not image.isNull():
            return QPixmap.fromImage(
                image.scaled(
                    size, Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        return QPixmap()

    @abstractmethod
    def get_item_attribute_values(self) -> dict:
        raise NotImplementedError("get_item_attribute_values")

    @abstractmethod
    def serialize(self) -> dict:
        raise NotImplementedError("get_item_attribute_values")
