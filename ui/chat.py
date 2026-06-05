import sys
import socket
import threading
import os
import uuid
import time
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
    QFileDialog,
    QMessageBox,
    QProgressBar
)


class ChatWindow(QWidget):

    message_received = pyqtSignal(dict)

    def __init__(self, username, server_ip):
        super().__init__()
        self.running = True
        self.valid = True
        self.username = username
        self.server_ip = server_ip
        self.buffer = ""
        self.selected_user = None
        self.pending_files = {}
        self.is_host = False
        self.receiving_file = False
        self.file_buttons = {}
        self.downloaded_files = {}
        self.file_cards = {}
        self.file_progress = {}

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

            response, self.buffer = receive_json(self.client,self.buffer)

            if response["type"] == "login_failed":
                QMessageBox.warning(
                    self,
                    "Login failed",
                    response["message"]
                )
                self.valid = False
                self.client.close()
                return

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

        self.running = False


        self.pending_files.clear()
        self.file_buttons.clear()
        self.downloaded_files.clear()


        if self.is_host:

            stop_server()


        try:

            self.client.close()

        except:

            pass


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
    

    def add_file_card(self, data, own=False, path=None):

        item = QListWidgetItem()
        card = QWidget()
        layout = QVBoxLayout()

        if data.get("private"):
            title = f"🔒 📄 {data['filename']}"
        else:
            title = f"📄 {data['filename']}"

        filename = QLabel(title)

        size = QLabel(self.format_size(data["size"]))

        sender = QLabel(f"From {data['sender']}")

        layout.addWidget(filename)
        layout.addWidget(size)
        layout.addWidget(sender)


        if own:

            open_button = QPushButton("Open")

            open_button.clicked.connect(
                lambda: os.startfile(path)
            )

            layout.addWidget(open_button)


        else:

            progress = QProgressBar()
            progress.setValue(0)
            progress.hide()
            progress.setStyleSheet(
                """
                QProgressBar {
                    background-color: #222;
                    border-radius: 8px;
                    height: 12px;
                    text-align: center;
                }

                QProgressBar::chunk {
                    background-color: #00C853;
                    border-radius: 8px;
                }
                """
            )            


            download_button = QPushButton("Download")

            download_button.clicked.connect(
                lambda: self.request_file(data)
            )
            
            self.file_buttons[data["file_id"]] = download_button
            self.file_progress[data["file_id"]] = progress

            layout.addWidget(progress)
            layout.addWidget(download_button)
            sender = data["sender"]
            if sender not in self.file_cards:
                self.file_cards[sender] = []
            self.file_cards[sender].append(download_button)


        card.setLayout(layout)

        card.setStyleSheet(
            """
            QWidget {
                background-color: #333333;
                border-radius: 10px;
                padding: 8px;
            }
            """
        )


        container = QWidget()
        container_layout = QHBoxLayout()
        if own:

            container_layout.addStretch()
            container_layout.addWidget(card)

        else:

            container_layout.addWidget(card)
            container_layout.addStretch()

        container.setLayout(container_layout)
        item.setSizeHint(container.sizeHint())
        self.chat_box.addItem(item)
        self.chat_box.setItemWidget(item, container)
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
            if self.selected_user != "🌐 General":

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

        while self.running:

            try:

                if self.receiving_file:
                    time.sleep(0.1)
                    continue

                data, self.buffer = receive_json(self.client, self.buffer)


                if data is None:

                    self.message_received.emit(
                        {
                            "type": "shutdown",
                            "message": "Room closed"
                        }
                    )

                    break
                
                if data["type"] == "file_data":
                    self.receiving_file = True

                self.message_received.emit(data)
                    


            except Exception as e:

                print(e)


                self.message_received.emit(
                    {
                        "type": "shutdown",
                        "message": "Connection lost"
                    }
                )

                break

    def receive_file(self, data):

        self.receiving_file = True

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            data["filename"]
        )


        if not save_path:
            return
        
        remaining = data["size"]
        received = 0
        total = data["size"]


        with open(save_path, "wb") as file:

            while remaining > 0:

                chunk = self.client.recv(
                    min(65536, remaining)
                )


                if not chunk:
                    break


                file.write(chunk)

                remaining -= len(chunk)
                received += len(chunk)
                percent = int((received / total) * 100)
                self.message_received.emit(
                    {
                        "type": "download_progress",
                        "file_id": data["file_id"],
                        "progress": percent
                    }
                )
        
        self.receiving_file = False
        self.downloaded_files[data["file_id"]] = save_path
        self.message_received.emit(
            {
                "type": "download_complete",
                "file_id": data["file_id"]
            }
        )        
        



    def request_file(self, data):
        request ={
            "type": "file_request",
            "file_id": data["file_id"],
            "from": data["sender"]
        }
        send_json(self.client, request)

    def send_requested_file(self, data):
        file_id = data["file_id"]
        if file_id not in self.pending_files:
            return
        file_info = self.pending_files[file_id]
        header={
           "type": "file_data",
           "file_id": file_id,
           "filename": file_info["filename"],
           "size": file_info["size"],
           "to": data["receiver"]
        }

        send_json(self.client, header)
        with open(file_info["path"], "rb") as file:
            while True:
                chunk = file.read(65536)
                if not chunk:
                    break
                self.client.sendall(chunk)
        

    def format_size(self, size):

        if size < 1024 ** 2:

            return f"{size / 1024:.1f} KB"


        elif size < 1024 ** 3:

            return f"{size / (1024 ** 2):.1f} MB"


        else:

            return f"{size / (1024 ** 3):.2f} GB"

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
            current = self.selected_user

            self.user_list.clear()

            self.user_list.addItem("🌐 General")

            for user in data["users"]:
                if user == self.username:
                    continue
                self.user_list.addItem(user)
            
            if current:
                items = self.user_list.findItems(current,Qt.MatchFlag.MatchExactly)
                if items:
                    self.user_list.setCurrentItem(items[0])
                else:
                    self.user_list.setCurrentRow(0)
                    self.selected_user = "🌐 General"
            else:
                self.user_list.setCurrentRow(0)
                self.selected_user = "🌐 General"


        
        elif data["type"] == "private":
            time = datetime.now().strftime("%I:%M %p")

            self.add_message(
                f"🔒 {data['sender']} ({time})",
                data["message"]
            )
        elif data["type"] == "shutdown":

            self.add_system_message(data["message"])

            QTimer.singleShot(2000, self.close)
        
        elif data["type"] == "file_offer":
            self.add_file_card(data)
        
        elif data["type"] == "send_file":
            self.send_requested_file(data)
        
        elif data["type"] == "file_data":
            self.receive_file(data)

    
        elif data["type"] == "download_complete":

            file_id = data["file_id"]
            bar = self.file_progress[file_id]
            bar.hide()

            button = self.file_buttons[file_id]
            button.show()

            button.setText("Open")
            try:
                button.clicked.disconnect()
            except:
                pass

            button.clicked.connect(
                lambda: os.startfile(
                    self.downloaded_files[file_id]
                )
            )
        elif data["type"] == "user_left":

            self.add_system_message(
                data["message"]
            )


            user = data["username"]


            if user in self.file_cards:

                for button in self.file_cards[user]:
                    if button.text() == "Download":
                        button.setText("Sender offline")
                        button.setEnabled(False)
        elif data["type"] == "download_progress":

            bar = self.file_progress[
                data["file_id"]
            ]

            button = self.file_buttons[
                data["file_id"]
            ]


            button.hide()

            bar.show()

            bar.setValue(
                data["progress"]
            )

                        
            

    def select_file(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")

        if not file_path:
            return

        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        file_id = str(uuid.uuid4())

        self.pending_files[file_id]={
            "path": file_path,
            "filename": filename,
            "size": file_size
        }

        receiver = None
        if self.selected_user != "🌐 General":
            receiver = self.selected_user

        file_data = {
            "type": "file_offer",
            "file_id": file_id,
            "filename": filename,
            "size": file_size,
            "to": receiver
        }

        # send file information
        send_json(self.client, file_data)

        self.add_file_card(
            {
                "filename": filename,
                "sender": "You",
                "size": file_size,
                "private": receiver is not None
            },
            own=True,
            path=file_path
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
