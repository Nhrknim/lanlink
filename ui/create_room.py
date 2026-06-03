import threading

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)

from network.server import start_server
from ui.chat import ChatWindow
from network.discovery import broadcast_room


class CreateRoomWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create Room")
        self.resize(300, 200)

        layout = QVBoxLayout()

        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("Room name")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.create_button = QPushButton("Start Room")

        layout.addWidget(QLabel("Create LAN Room"))
        layout.addWidget(self.room_input)
        layout.addWidget(self.username_input)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

        self.create_button.clicked.connect(self.create_room)


    def create_room(self):

        room_name = self.room_input.text().strip()
        username = self.username_input.text().strip()

        if not room_name or not username:
            return

        threading.Thread(target=start_server, daemon=True).start()
        threading.Thread(target=broadcast_room, args=(room_name, username), daemon=True).start()

        self.chat = ChatWindow(username, "127.0.0.1")
        self.chat.show()

        self.close()