import sys
import socket
import threading

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget
)


class ChatWindow(QWidget):

    message_received = pyqtSignal(str)

    def __init__(self, username, server_ip):
        super().__init__()

        self.username = username
        self.server_ip = server_ip

        self.setWindowTitle(f"LANLink - {self.username}")
        self.resize(800, 600)

        layout = QVBoxLayout()
        chat_layout = QHBoxLayout()

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        self.user_list = QListWidget()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            "Enter message and press Enter...")

        self.send_button = QPushButton("Send")

        chat_layout.addWidget(self.chat_box, 3)
        chat_layout.addWidget(self.user_list, 1)
        layout.addLayout(chat_layout)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

        self.send_button.clicked.connect(self.send_message)
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
            self.client.send(
                self.username.encode()
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

    def send_message(self):
        message = self.message_input.text().strip()

        if not message:
            return

        try:
            self.client.send(
                message.encode()
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
                message = self.client.recv(1024).decode()

                if not message:
                    break

                self.message_received.emit(message)

            except:
                break

    def display_message(self, message):
        if message.startswith("USERS:"):
            users = message[6:].split(",")
            self.user_list.clear()
            for user in users:
                if user:
                    self.user_list.addItem(user)
            return

        self.chat_box.append(message)


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
