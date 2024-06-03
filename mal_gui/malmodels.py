from PySide6.QtWidgets import QLabel,QWidget
from PySide6.QtGui import QIcon, QDoubleValidator,QDrag,QPixmap
from PySide6.QtCore import Qt

import threading


class IntegerData(NodeData):
    'Node data holding an integer value'
    data_type = NodeDataType("integer", "Integer")

    def __init__(self, number: int = 0):
        self._number = number
        self._lock = threading.RLock()

    @property
    def lock(self):
        return self._lock

    @property
    def number(self) -> int:
        'The number data'
        return self._number

    def number_as_text(self) -> str:
        'Number as a string'
        return str(self._number)

#Each Class is cosidered a Model
class Attacker(NodeDataModel):
    name: "Attacker"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/attacker.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label
    


class Client(NodeDataModel):
    name: "Client"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/client.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label
    

class Container(NodeDataModel):
    name: "Container"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/container.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label
    
class Container(NodeDataModel):
    name: "Container"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/container.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label
    


class Datastore(NodeDataModel):
    name: "Datastore"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/datastore.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label
    
class Firewall(NodeDataModel):
    name: "Firewall"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/firewall.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label
    
class Host(NodeDataModel):
    name: "Firewall"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/host.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label
    
class Network(NodeDataModel):
    name: "Network"
    caption_visible = True
    data_type = IntegerData.data_type
    num_ports = {PortType.input: 1,
                 PortType.output: 1,
                 }
    port_caption = {'input': {0: 'Input'},'output': {0: 'Output'}}
    
    def __init__(self, style=None, parent=None):
        super().__init__(style=style, parent=parent)
        self._number = None
        self._label = QLabel()
        imageIcon = QPixmap('images/network.png')

        # Resize the QPixmap to a smaller size
        imageWidth = 40  # width of image
        imageHeight = 40  # height of image
        smallerImageIcon = imageIcon.scaled(imageWidth, imageHeight, aspectMode=Qt.KeepAspectRatio)
        self._label.setPixmap(smallerImageIcon)
    
    def embedded_widget(self) -> QWidget:
        # 'The number source has a line edit widget for the user to type in'
        return self._label