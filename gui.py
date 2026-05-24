import sys

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

        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)

    def send_message(self):
        message = self.message_input.text()

        if message:
            self.chat_box.append(f"You: {message}")
            self.message_input.clear()


app = QApplication(sys.argv)

window = ChatWindow()

window.show()

sys.exit(app.exec())