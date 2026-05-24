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
    QHBoxLayout
)


class ChatWindow(QWidget):

    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("LANLink")
        self.resize(800, 600)

        self.main_layout = QVBoxLayout()

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")

        self.send_button = QPushButton("Send")

        self.input_layout = QHBoxLayout()

        self.input_layout.addWidget(self.message_input)
        self.input_layout.addWidget(self.send_button)

        self.main_layout.addWidget(self.chat_box)
        self.main_layout.addLayout(self.input_layout)

        self.setLayout(self.main_layout)

        # Button connections
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

        # Signal connection
        self.message_received.connect(self.display_message)

        # Networking
        self.username = "GUI_User"

        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.client.connect(("127.0.0.1", 5555))

        # Send username to server
        self.client.send(self.username.encode())

        # Start receiving thread
        threading.Thread(
            target=self.receive_messages,
            daemon=True
        ).start()

    def send_message(self):
        message = self.message_input.text()

        if message:
            try:
                self.client.send(message.encode())

                self.chat_box.append(
                    f"You: {message}"
                )

                self.message_input.clear()

            except Exception as e:
                self.chat_box.append(
                    f"[ERROR] {e}"
                )

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode()

                if not message:
                    break

                self.message_received.emit(message)

            except Exception as e:
                self.message_received.emit(
                    f"[ERROR] {e}"
                )
                break

    def display_message(self, message):
        self.chat_box.append(message)


app = QApplication(sys.argv)

window = ChatWindow()

window.show()

sys.exit(app.exec())