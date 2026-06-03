from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout
)

from ui.chat import ChatWindow

class LoginWindow(QWidget):

    def __init__(self,default_ip=""):
        super().__init__()

        self.setWindowTitle("LANLink Login")
        self.resize(300, 150)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Server IP")
        self.ip_input.setText(default_ip)

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
