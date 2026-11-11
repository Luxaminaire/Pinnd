import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QMenu,
    QVBoxLayout,
    QLineEdit,
    QTextEdit, QFileDialog
)

import pinn
from pinn import Pinn

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setMinimumSize(QSize(400, 400))
        self.window = QWidget()
        self.setCentralWidget(self.window)

    def showContextMenu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet(
            f"""
            QMenu {{background-color: #FFBE34; border: none;}}
            QMenu::item {{color: {pinn.defaultTextColor}; background-color: #FFBE34;}}
            QMenu::item:selected {{color: {pinn.defaultTextColor}; background-color: #FEAF03;}}
            """
        )

        textPinn = menu.addAction("Text Pinn")
        imagePinn = menu.addAction("Image Pinn")
        audioPinn = menu.addAction("Audio Pinn")
        font = textPinn.font()
        font.setBold(True)
        textPinn.setFont(font)
        imagePinn.setFont(font)
        audioPinn.setFont(font)

        action = menu.exec(position)
        if action == textPinn:
            note = Pinn(self.window, "Text")
            local_pos = self.mapFromGlobal(position)
            note.move(local_pos)
        if action == imagePinn:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Select an Image", "", "Image Files (*.png *.jpg *.bmp *.gif)"
            )
            if filepath:
                note = Pinn(self.window, "Image", filepath)
                local_pos = self.mapFromGlobal(position)
                note.move(local_pos)
        if action == audioPinn:
            note = Pinn(self.window, "Audio")
            local_pos = self.mapFromGlobal(position)
            note.move(local_pos)

    def contextMenuEvent(self, event):
        self.showContextMenu(event.globalPos())
        event.accept()

    def mousePressEvent(self, event):
        focus = QApplication.focusWidget()
        if isinstance(focus, QWidget): focus.clearFocus()



app = QApplication(sys.argv)
window = MainWindow()
window.setWindowTitle("Untitled Pinnboard")
window.resize(1000, 700)
window.show()
app.exec()
