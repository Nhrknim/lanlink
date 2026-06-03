import threading

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton
)

from network.discovery import find_rooms
from ui.chat import ChatWindow


class JoinRoomWindow(QWidget):

    rooms_found = pyqtSignal(dict)


    def __init__(self):
        super().__init__()

        self.setWindowTitle("Join Room")
        self.resize(300, 300)

        self.rooms = {}

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.room_list = QListWidget()

        self.join_button = QPushButton("Join")

        layout.addWidget(self.username_input)
        layout.addWidget(self.room_list)
        layout.addWidget(self.join_button)

        self.setLayout(layout)


        self.rooms_found.connect(self.update_rooms)

        self.join_button.clicked.connect(self.join_room)


        threading.Thread(target=self.search_rooms, daemon=True).start()


    def search_rooms(self):

        rooms = find_rooms()

        self.rooms_found.emit(rooms)


    def update_rooms(self, rooms):

        self.rooms = rooms

        self.room_list.clear()


        for room, info in rooms.items():

            self.room_list.addItem(
                f"{room} - {info['host']}"
            )


    def join_room(self):

        username = self.username_input.text().strip()

        selected = self.room_list.currentItem()


        if not username or not selected:
            return


        room_name = selected.text().split(" - ")[0]

        ip = self.rooms[room_name]["ip"]


        self.chat = ChatWindow(username, ip)

        self.chat.show()

        self.close()