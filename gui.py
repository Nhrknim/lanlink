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

app = QApplication(sys.argv)

window = QWidget()

window.setWindowTitle("LANLink")
window.resize(800, 600)

main_layout = QVBoxLayout()

chat_box = QTextEdit()
chat_box.setReadOnly(True)

message_input = QLineEdit()
message_input.setPlaceholderText("Type a message...")

send_button = QPushButton("Send")

input_layout = QHBoxLayout()

input_layout.addWidget(message_input)
input_layout.addWidget(send_button)

main_layout.addWidget(chat_box)
main_layout.addLayout(input_layout)

window.setLayout(main_layout)

window.show()

sys.exit(app.exec())