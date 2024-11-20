from PySide6.QtCore import QRectF, Qt,QPointF,QSize,QSizeF,QTimer
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

from ..object_explorer.editable_text_item import EditableTextItem
from .assets_container_rectangle_box import AssetsContainerRectangleBox

class AssetsContainer(QGraphicsItem):
    # Starting Sequence Id with normal start at 100 (randomly taken)
    container_sequence_id = 100

    def __init__(
            self,
            container_type,
            container_name,
            image_path,
            plus_symbol_image_path,
            minus_symbol_image_path,
            parent=None
        ):
        super().__init__(parent)
        self.setZValue(1)  # rect items are on top
        self.container_type = container_type
        self.container_name = container_name
        self.container_sequence_id = \
            AssetsContainer.generate_next_sequence_id()
        self.image_path = image_path
        self.plus_symbol_image_path = plus_symbol_image_path
        self.minus_symbol_image_path = minus_symbol_image_path
        self.plus_or_minus_image_rect = QRectF()
        self.is_plus_symbol_visible = True  # Track the current symbol state
        self.container_box = None
        print("image path = "+ self.image_path)

        self.image = self.load_image_with_quality(
            self.image_path, QSize(512, 512))
        self.plus_symbol_image = self.load_image_with_quality(
            self.plus_symbol_image_path, QSize(512, 512))
        self.minus_symbol_image = self.load_image_with_quality(
            self.minus_symbol_image_path, QSize(512, 512))

        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        # Create the editable text item for block type
        self.type_text_item = EditableTextItem(self.container_name, self)
        self.type_text_item.lostFocus.connect(self.update_container_name)

        self.containerized_assets_list = []
        self.initial_position = QPointF()

        # Visual Styling
        self.width = 240
        self.height = 70
        self.size = QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

        self.container_type_bg_color = QColor(0, 200, 255) #Blue
        self.container_name_bg_color = QColor(20, 20, 20, 200) # Gray

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

    def mouseDoubleClickEvent(self, event):
        """Overrides base method"""
        if event.button() == Qt.LeftButton:
            self.type_text_item.setTextInteractionFlags(
                Qt.TextEditorInteraction)
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

        if self.plus_or_minus_image_rect.contains(event.pos()):
            print("Plus or minus button clicked")
            # Toggle the symbol visibility
            # self.is_plus_symbol_visible = not self.is_plus_symbol_visible
            # self.update()
            self.toggle_container_expansion()
        elif self.type_text_item.hasFocus() and not self.type_text_item.contains(event.pos()):
            self.type_text_item.clearFocus()
        elif not self.type_text_item.contains(event.pos()):
            self.type_text_item.deselect_text()
        else:
            super().mousePressEvent(event)

    def setIcon(self, icon_path=None):
        """Overrides base method"""
        self.icon_path = icon_path
        if self.image:
            self.icon_pixmap = QPixmap(icon_path)
        else:
            self.icon_pixmap = QPixmap()

    def itemChange(self, change, value):
        """Overrides base method"""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            if hasattr(self, 'item_moved') and callable(self.item_moved):
                self.item_moved()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        """Overrides base method"""
        painter.setPen(self.container_name_bg_color.lighter())
        painter.setBrush(self.container_name_bg_color)
        painter.drawPath(self.path)

        gradient = QLinearGradient()
        gradient.setStart(0, -90)
        gradient.setFinalStop(0, 0)
        gradient.setColorAt(0, self.container_type_bg_color)  # Start color
        gradient.setColorAt(1, self.container_type_bg_color.darker())  # End color

        painter.setBrush(QBrush(gradient))
        painter.setPen(self.container_type_bg_color)
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
            target_icon_size = QSize(24, 24)  # Desired size for the icon

            # Resize the icon using smooth transformation
            # resized_image_icon = self.image.scaled(target_icon_size,
            # Qt.KeepAspectRatio, Qt.SmoothTransformation)
            resized_image_icon = self.image


            # Calculate the position and size for the icon background
            icon_rect = QRectF(
                -self.width / 2 + 10,
                -self.height / 2 + 10,
                target_icon_size.width(),
                target_icon_size.height()
            )
            margin = 5  # Margin around the icon

            # Draw the background for the icon with additional margin
            background_rect = QRectF(
                icon_rect.topLeft() - QPointF(margin, margin),
                QSizeF(target_icon_size.width() + 2 * margin,
                       target_icon_size.height() + 2 * margin))

            painter.setBrush(Qt.white)  # Set the brush color to white

            # Convert QRectF to QRect and draw the white background rectangle
            painter.drawRect(background_rect.toRect())

            # Convert QRectF to QRect and draw the resized icon
            painter.drawPixmap(icon_rect.toRect(), resized_image_icon)

        # Determine which symbol to draw based on the current state
        current_symbol_image = self.plus_symbol_image\
                               if self.is_plus_symbol_visible\
                               else self.minus_symbol_image
        if not current_symbol_image.isNull():
            # Desired size for the second icon
            target_symbol_image_size = QSize(12, 12)

            # Get the bounding rect of the title_bg_path
            title_bg_rect = self.title_bg_path.boundingRect()

            # Calculate the position for the symbol at the
            # bottom-right corner of title_bg_path
            self.plus_or_minus_image_rect = QRectF(
                title_bg_rect.right()
                    - target_symbol_image_size.width() - 10,
                title_bg_rect.bottom()
                    - target_symbol_image_size.height() - 5,
                target_symbol_image_size.width(),
                target_symbol_image_size.height()
            )

            painter.setBrush(Qt.white)
            painter.drawRect(self.plus_or_minus_image_rect)

            resized_symbol_image = current_symbol_image.scaled(
                target_symbol_image_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Draw the plus or minus symbol with a white background
            painter.drawPixmap(
                self.plus_or_minus_image_rect.toRect(), resized_symbol_image)



        # Draw the highlight if selected
        if self.isSelected():
            painter.setPen(QPen(self.container_type_bg_color.lighter(), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path)

    @classmethod
    def generate_next_sequence_id(cls):
        cls.container_sequence_id += 1
        return cls.container_sequence_id

    def build(self):
        self.title_text = self.container_type
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
            -fixed_height / 2 + self.vertical_margin
                              + title_font_metrics.ascent(),
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
            self.update_type_text_item_position
        )

        # self.widget.move(-self.widget.size().width() / 2,
        # fixed_height / 2 - self.widget.size().height() + 5)

    def update_type_text_item_position(self):
        # to update the position of the type_text_item so that it
        # remains centered within the lower half of the node
        # whenever the text changes.

        type_font_metrics = QFontMetrics(self.type_text_item.font())
        fixed_height = self.height
        title_font_metrics = QFontMetrics(QFont("Arial", pointSize=12))

        # Calculate the new position for type_text_item
        type_text_item_pos_x = (
            -type_font_metrics.horizontalAdvance(
                self.type_text_item.toPlainText()
            ) / 2
        )
        type_text_item_pos_y = (
            -fixed_height / 2
            + title_font_metrics.height()
            + 2 * self.vertical_margin
        )

        # Update position
        self.type_text_item.setPos(type_text_item_pos_x, type_text_item_pos_y)

    def update_container_name(self):
        self.container_name = self.type_text_item.toPlainText()
        self.type_text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        self.type_text_item.deselect_text()
        self.update_type_text_item_position()

        associated_scene = self.type_text_item.scene()
        if associated_scene:
            print("Container Name Changed by user")

    def get_item_attribute_vakues(self):
        return {
            "Container Sequence ID": self.container_sequence_id,
            "Container Name": self.container_name,
            "Container Type": self.container_type
        }

    def toggle_icon_visibility(self):
        self.icon_visible = not self.icon_visible
        self.update()

    def update_status_color(self):
        self.status_color =  QColor(0, 255, 0)
        self.update()

    def load_image_with_quality(self, path, size):
        image = QImage(path)
        if not image.isNull():
            return QPixmap.fromImage(
                image.scaled(
                    size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        return QPixmap()

    def toggle_container_expansion(self):
        if self.is_plus_symbol_visible:
            # Expand
            self.is_plus_symbol_visible = False
            self.show_container_box()
        else:
            # Collapse
            self.is_plus_symbol_visible = True
            self.hide_container_box()
        self.update()

    def show_container_box(self):
        if not self.container_box:
            rect = QRectF(0, 0, self.width, 100)
            self.container_box = AssetsContainerRectangleBox(rect, self)
            self.update_container_box_position()
            self.scene().addItem(self.container_box)

    def hide_container_box(self):
        if self.container_box:
            self.scene().removeItem(self.container_box)
            self.container_box = None

    def update_container_box_position(self):
        if self.container_box:
            container_bottom_left = (
                self.pos() + QPointF(
                    -self.width / 2,
                    self.boundingRect().height() / 2
                )
            )
            container_box_position = \
                container_bottom_left + QPointF(0, self.height / 2)
            self.container_box.setPos(container_box_position)
