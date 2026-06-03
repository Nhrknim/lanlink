import sys
import socket
import threading
import os
from datetime import datetime
from network.protocol import send_json, receive_json
from network.server import stop_server
from PyQt6.QtCore import pyqtSignal, Qt, QSize, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLabel,
    QFileDialog
)


class ChatWindow(QWidget):

    message_received = pyqtSignal(dict)

    def __init__(self, username, server_ip):
        super().__init__()

        self.username = username
        self.server_ip = server_ip
        self.buffer = ""
        self.selected_user = None
        self.is_host = False

        self.setWindowTitle(f"LANLink - {self.username}")
        self.resize(800, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-size: 14px;
            }

            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 5px;
            }

            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
            }

            QLineEdit {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 6px;
            }

            QPushButton {
                background-color: #4a90e2;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #5aa0f2;
            }
        """)

        layout = QVBoxLayout()
        chat_layout = QHBoxLayout()

        self.chat_box = QListWidget()

        self.chat_title = QLabel("General Chat")
        self.users_label = QLabel("Online Users")
        user_layout = QVBoxLayout()

        self.user_list = QListWidget()
        self.user_list.setMaximumWidth(200)

        user_layout.addWidget(self.users_label)
        user_layout.addWidget(self.user_list)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            "Enter message and press Enter...")

        self.send_button = QPushButton("Send")
        self.file_button = QPushButton("File")

        message_area = QVBoxLayout()
        message_area.addWidget(self.chat_title)
        message_area.addWidget(self.chat_box)

        chat_layout.addLayout(message_area, 3)
        chat_layout.addLayout(user_layout, 1)
        layout.addLayout(chat_layout)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.file_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

        self.send_button.clicked.connect(self.send_message)
        self.file_button.clicked.connect(self.select_file)
        self.message_input.returnPressed.connect(self.send_message)

        self.message_received.connect(self.display_message)

        self.user_list.itemClicked.connect(
            self.select_user
        )

        try:
            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect(
                (self.server_ip, 5555)
            )

            # Send username to server

            send_json(
                self.client,
                {
                    "type": "login",
                    "username": self.username
                }
            )
            self.add_system_message(f"Connected as {self.username}")

            threading.Thread(
                target=self.receive_messages,
                daemon=True
            ).start()

        except Exception as e:
            self.add_system_message(
                f"[Connection Error] {e}"
            )

    def closeEvent(self, event):

        if self.is_host:

            stop_server()

        event.accept()

    def add_message(self, sender, message, own=False):

        item = QListWidgetItem()

        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 2, 5, 2)

        message_block = QWidget()
        block_layout = QVBoxLayout()
        block_layout.setContentsMargins(0, 0, 0, 0)
        block_layout.setSpacing(3)

        name = QLabel(sender)

        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(350)

        bubble.setStyleSheet(
            """
            QLabel {
                padding: 8px;
                border-radius: 10px;
                background-color: #333333;
            }
            """
        )

        if own:
            name.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            name.setAlignment(Qt.AlignmentFlag.AlignLeft)

        block_layout.addWidget(name)
        block_layout.addWidget(bubble)

        message_block.setLayout(block_layout)

        if own:
            row_layout.addStretch()
            row_layout.addWidget(message_block)

        else:
            row_layout.addWidget(message_block)
            row_layout.addStretch()

        row.setLayout(row_layout)

        row.adjustSize()
        item.setSizeHint(row.sizeHint())

        self.chat_box.addItem(item)
        self.chat_box.setItemWidget(item, row)

        self.chat_box.scrollToBottom()

    def add_system_message(self, message):

        item = QListWidgetItem()

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label.setStyleSheet(
            """
            QLabel {
                color: #aaaaaa;
                padding: 5px;
            }
            """
        )

        item.setSizeHint(label.sizeHint())

        self.chat_box.addItem(item)
        self.chat_box.setItemWidget(item, label)

        self.chat_box.scrollToBottom()

    def send_message(self):
        message = self.message_input.text().strip()

        if not message:
            return

        try:
            if self.selected_user:

                data = {
                    "type": "private",
                    "to": self.selected_user,
                    "message": message
                }

            else:

                data = {
                    "type": "chat",
                    "message": message
                }

            send_json(self.client, data)

            time = datetime.now().strftime("%I:%M %p")

            self.add_message(
                f"You ({time})",
                message,
                own=True
            )

            self.message_input.clear()

        except Exception as e:
            self.add_message(
                "System",
                f"[Send Error] {e}"
            )

    def receive_messages(self):

        while True:

            try:

                data, self.buffer = receive_json(self.client, self.buffer)

                if data is None:
                    break

                if data["type"] == "file":

                    self.receive_file(data)

                else:

                    self.message_received.emit(data)

            except Exception as e:

                print(e)
                break

    def receive_file(self, data):

        filename = data["filename"]
        file_size = data["size"]

        os.makedirs(
            "downloads",
            exist_ok=True
        )

        path = os.path.join(
            "downloads",
            filename
        )

        received = 0

        with open(path, "wb") as file:

            while received < file_size:

                chunk = self.client.recv(
                    min(
                        4096,
                        file_size - received
                    )
                )

                if not chunk:
                    break

                file.write(chunk)

                received += len(chunk)

        if data["private"]:

            message = (
                f"🔒 Private file from {data['sender']}: {filename}"
            )

        else:

            message = (
                f"📁 File from {data['sender']}: {filename}"
            )

        self.message_received.emit(
            {
                "type": "system",
                "message": message
            }
        )

    def display_message(self, data):

        if data["type"] == "chat":
            time = datetime.now().strftime("%I:%M %p")

            self.add_message(
                f"{data['sender']} ({time})",
                data["message"]
            )

        elif data["type"] == "system":

            self.add_system_message(
                data["message"]
            )

        elif data["type"] == "users":

            self.user_list.clear()

            self.user_list.addItem("🌐 General")

            for user in data["users"]:
                if user == self.username:
                    continue
                self.user_list.addItem(user)
        elif data["type"] == "private":
            time = datetime.now().strftime("%I:%M %p")

            self.add_message(
                f"🔒 {data['sender']} ({time})",
                data["message"]
            )
        elif data["type"] == "shutdown":

            self.add_system_message(data["message"])

            QTimer.singleShot(2000, self.close)

    def select_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File"
        )

        if not file_path:
            return

        filename = file_path.split("/")[-1]
        file_size = os.path.getsize(file_path)

        file_data = {
            "type": "file",
            "filename": filename,
            "size": file_size,
            "to": self.selected_user
        }

        # send file information
        send_json(self.client, file_data)

        # send actual file bytes
        with open(file_path, "rb") as file:

            while True:

                chunk = file.read(4096)

                if not chunk:
                    break

                self.client.send(chunk)

        self.add_message(
            "You",
            f"📤 Sent {filename}",
            own=True
        )

    def select_user(self, item):

        user = item.text()

        if user == "🌐 General":
            self.selected_user = None
            self.chat_title.setText("General Chat")
            return

        if user == self.username:
            return

        self.selected_user = user

        self.chat_title.setText(
            f"Chat with {user}"
        )
