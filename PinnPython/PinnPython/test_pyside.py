#This is just a basic testing ground to see if it works.
import sys

from PySide6.QtWidgets import QApplication, QWidget


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Test Notepad")
window.resize(1000, 700)
window.show()



app.exec()