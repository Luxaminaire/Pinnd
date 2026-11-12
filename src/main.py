import json
import sys
from pathlib import Path

from PySide6.QtCore import QSize, QByteArray, QSaveFile, QIODevice
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QMenu, QFileDialog, QColorDialog
import pinn
from pinn import Pinn
import atexit

class MainWindow(QMainWindow):
    backgroundColor = "#996A3C"
    textColor = "#000000"

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setMinimumSize(QSize(400, 400))
        self.window = QWidget()
        self.setCentralWidget(self.window)

        self.window.setStyleSheet(f"""
            QWidget {{background-color: {self.backgroundColor}; border: none;}}
        """)

    def showContextMenu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet(
            f"""
            QMenu {{background-color: {pinn.darkenHex(self.backgroundColor, 0.88)}; border: none;}}
            QMenu::item {{color: {self.textColor}; background-color: {pinn.darkenHex(self.backgroundColor, 0.88)};}}
            QMenu::item:selected {{color: {self.textColor}; background-color: {pinn.darkenHex(self.backgroundColor, 0.74)};}}
            QMenu::separator {{background:{self.textColor}; height: 1px; margin-top: 5px; margin-bottom: 5px;}}
            """
        )

        menu.setFixedWidth(150)
        font = QFont(pinn.defaultFont, 10)
        font.setBold(True)

        textPinn = menu.addAction("Text Pinn")
        imagePinn = menu.addAction("Image Pinn")
        audioPinn = menu.addAction("Audio Pinn")
        menu.addSeparator()
        textColor = menu.addAction("Text Color")
        bgColor = menu.addAction("Background Color")

        textPinn.setFont(font)
        imagePinn.setFont(font)
        audioPinn.setFont(font)
        textColor.setFont(font)
        bgColor.setFont(font)

        action = menu.exec(position)
        if action == textPinn:
            note = Pinn(self.window, "Text")
            local_pos = self.mapFromGlobal(position)
            note.move(local_pos)
            pinn.pinnList.append(note)
        if action == imagePinn:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Select an Image", "", "Image Files (*.png *.jpg *.bmp *.gif)"
            )
            if filepath:
                note = Pinn(self.window, "Image", filepath)
                local_pos = self.mapFromGlobal(position)
                note.move(local_pos)
                pinn.pinnList.append(note)
        if action == audioPinn:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Select an Audio", "", "Audio Files (*.wav *.mp3)"
            )
            if filepath:
                note = Pinn(self.window, "Audio", filepath)
                local_pos = self.mapFromGlobal(position)
                note.move(local_pos)
                pinn.pinnList.append(note)
        if action == textColor:
            color = QColorDialog.getColor()
            self.recolor(textColor=color.name())
        if action == bgColor:
            color = QColorDialog.getColor()
            self.recolor(bgColor=color.name())

    def recolor(self, bgColor=None, textColor=None):
        if bgColor is not None: self.backgroundColor = bgColor
        if textColor is not None: self.textColor = textColor

        self.window.setStyleSheet(f"""
            QWidget {{background-color: {self.backgroundColor}; border: none;}}
        """)

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

def Save():
    data = []
    data.append({"textColor": window.textColor, "backgroundColor": window.backgroundColor})
    for item in pinn.pinnList:
        bodyText = None
        bodyImage = None
        bodyAudio = None
        if item.bodyText is not None: bodyText = item.bodyText.text.toPlainText()
        if item.bodyImage is not None: bodyImage = "Image"
        if item.bodyAudio is not None: bodyAudio = {"looped": item.bodyAudio.looped}
        pos = {"x": item.pos().x(), "y": item.pos().y()}
        size = {"x": item.size().width(), "y": item.size().height()}

        data.append({
            "backgroundColor": item.backgroundColor,
            "headerText": item.topBar.text.text(),
            "headerColor": item.headerColor,
            "bodyColor": item.bodyColor,
            "headerSize": item.headerSize,
            "bodySize": item.bodySize,
            "headerFont": item.headerFont,
            "bodyFont": item.bodyFont,
            "bodyText": bodyText,
            "bodyImage": bodyImage,
            "bodyAudio": bodyAudio,
            "filepath": item.filepath,
            "position": pos,
            "size": size
        })

        save = QSaveFile(str(Path.cwd() / "pinnboards" / "default.json"))
        if save.open(QIODevice.OpenModeFlag.WriteOnly):
            jsonData = json.dumps(data, indent=4).encode("utf-8")
            save.write(jsonData)
            save.commit()

def Restore():
    path = Path.cwd() / "pinnboards" / "default.json"
    if path.is_file():
        with open(path, "r", encoding="utf-8") as save:
            data = json.load(save)

            for loaded in data:
                if "textColor" in loaded:
                    window.backgroundColor = loaded["backgroundColor"]
                    window.textColor = loaded["textColor"]
                    window.recolor()
                else:
                    if loaded["bodyText"] is not None:
                        note = Pinn(window, "Text")
                        note.bodyText.text.setText(loaded["bodyText"])
                    if loaded["bodyImage"] is not None:
                        note = Pinn(window, "Image", loaded["filepath"])
                    if loaded["bodyAudio"] is not None:
                        note = Pinn(window, "Audio", loaded["filepath"])
                        note.bodyAudio.looped = loaded["bodyAudio"]["looped"]
                    note.backgroundColor = loaded["backgroundColor"]
                    note.headerColor = loaded["headerColor"]
                    note.bodyColor = loaded["bodyColor"]
                    note.headerSize = loaded["headerSize"]
                    note.bodySize = loaded["bodySize"]
                    note.headerFont = loaded["headerFont"]
                    note.bodyFont = loaded["bodyFont"]
                    note.topBar.text.setText(loaded["headerText"])
                    note.move(loaded["position"]["x"], loaded["position"]["y"])
                    note.resize(loaded["size"]["x"], loaded["size"]["y"])
                    note.recolor()
                    pinn.pinnList.append(note)
atexit.register(Save)
Restore()

app.exec()
