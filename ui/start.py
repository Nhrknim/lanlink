import threading
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel
)

from ui.join_room import JoinRoomWindow
from ui.create_room import CreateRoomWindow


class StartWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LANLink")
        self.resize(300, 200)

        layout = QVBoxLayout()

        title = QLabel("LANLink")

        self.create_button = QPushButton("Create Room")
        self.join_button = QPushButton("Join Room")

        layout.addWidget(title)
        layout.addWidget(self.create_button)
        layout.addWidget(self.join_button)

        self.setLayout(layout)

        self.create_button.clicked.connect(self.create_room)
        self.join_button.clicked.connect(self.join_room)

    def create_room(self):

        self.create_window = CreateRoomWindow()
        self.create_window.show()
        self.close()

    def join_room(self):

        self.join_window = JoinRoomWindow()
        self.join_window.show()
        self.close()
