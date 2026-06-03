import sys
import socket
import threading
import os
from network.protocol import send_json, receive_json

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
        self.selected_user = None

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

                data, self.buffer = receive_json(self.client,self.buffer)

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

            self.chat_box.append(
                f"{data['sender']}: {data['message']}"
            )

        elif data["type"] == "system":

            self.chat_box.append(
                f"*** {data['message']} ***"
            )

        elif data["type"] == "users":

            self.user_list.clear()

            self.user_list.addItem("🌐 General")

            for user in data["users"]:
                if user == self.username:
                    continue
                self.user_list.addItem(user)
        elif data["type"] == "private":

            self.chat_box.append(
                f"🔒 {data['sender']}: {data['message']}"
            )       

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
        send_json(self.client,file_data)

        # send actual file bytes
        with open(file_path, "rb") as file:

            while True:

                chunk = file.read(4096)

                if not chunk:
                    break

                self.client.send(chunk)

        self.chat_box.append(
            f"📤 You sent: {filename}"
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
