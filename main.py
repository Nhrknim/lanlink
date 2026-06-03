import sys

from PyQt6.QtWidgets import QApplication
from ui.start import StartWindow


app = QApplication(sys.argv)

window = StartWindow()
window.show()

sys.exit(app.exec())