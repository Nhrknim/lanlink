import sys
import socket
import threading
import json

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
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

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
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

        chat_layout.addWidget(self.chat_box, 3)
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

        try:
            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect(
                (self.server_ip, 5555)
            )

            # Send username to server

            self.send_json(
                {
                    "type": "login",
                    "username": self.username
                }
            )
            self.chat_box.append(f"Connected as {self.username}")

            threading.Thread(
                target=self.receive_messages,
                daemon=True
            ).start()

        except Exception as e:
            self.chat_box.append(
                f"[Connection Error] {e}"
            )

    def send_json(self, data):
        message = json.dumps(data) + "\n"
        self.client.send(message.encode())

    def receive_json(self):

        while "\n" not in self.buffer:

            data = self.client.recv(1024).decode()

            if not data:
                return None

            self.buffer += data

        message, self.buffer = (
            self.buffer.split("\n", 1)
        )

        return json.loads(message)

    def send_message(self):
        message = self.message_input.text().strip()

        if not message:
            return

        try:
            self.send_json(
                {
                    "type": "chat",
                    "message": message

                }
            )

            self.chat_box.append(
                f"You: {message}"
            )

            self.message_input.clear()

        except Exception as e:
            self.chat_box.append(
                f"[Send Error] {e}"
            )

    def receive_messages(self):
        while True:
            try:
                data = self.receive_json()

                if data is None:
                    break

                self.message_received.emit(data)

            except Exception as e:
                print("GUI receive error:", e)
                break

    def display_message(self, data):

        if data["type"] == "chat":

            self.chat_box.append(
                f"{data['sender']}: {data['message']}"
            )

        elif data["type"] == "system":

            self.chat_box.append(
                f"*** {data['message']} ***"
            )

        elif data["type"] == "users":

            self.user_list.clear()

            for user in data["users"]:
                self.user_list.addItem(user)

    def select_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File"
        )

        if file_path:

            self.chat_box.append(
                f"Selected file: {file_path}"
            )


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LANLink Login")
        self.resize(300, 150)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Server IP")
        self.ip_input.setText("127.0.0.1")

        self.connect_button = QPushButton("Connect")

        layout.addWidget(self.username_input)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

        self.username_input.returnPressed.connect(
            self.connect_to_chat
        )
        self.ip_input.returnPressed.connect(
            self.connect_to_chat
        )

        self.connect_button.clicked.connect(
            self.connect_to_chat
        )

    def connect_to_chat(self):

        username = self.username_input.text().strip()
        server_ip = self.ip_input.text().strip()

        if not username:
            return

        self.chat_window = ChatWindow(
            username,
            server_ip
        )

        self.chat_window.show()

        self.close()


app = QApplication(sys.argv)

window = LoginWindow()

window.show()

sys.exit(app.exec())
