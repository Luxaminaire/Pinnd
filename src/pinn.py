import colorsys
import os
import shutil
import sys
import time
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QPoint
from PySide6.QtGui import QRegion, QPolygon, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QMenu,
    QVBoxLayout,
    QLineEdit,
    QTextEdit, QSizePolicy, QLabel,
)

defaultTextPinnWidth = 250
defaultTextPinnHeight = 350
minPinnSize = 100
maxPinnSize = 600
maxAudioPinnWidth = 350
minAudioPinnWidth = 175
defaultAudioPinnHeight = 100

maxHeaderLength = 75
maxCaptionLength = 75
maxBodyLength = 1000
minFontSize = 6
maxFontSize = 50

defaultBackgroundColor = "#FFCC5E"
defaultTextColor = "#000000"
defaultFont = "Arial"
defaultHeaderSize = 14
defaultBodySize = 11
defaultCaptionSize = 12

def darkenHex(color, factor):
    hex_color = color.lstrip('#')
    r, g, b = (int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, l * factor, s)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

def assetCreationHandler(filepath):
    fileName, fileExtension = os.path.splitext(os.path.basename(filepath)) # Preserve file extension
    assetName = f"{int(time.time())}_{fileName}{fileExtension}" # Add timestamp so that multiple Pinns can
    path = Path(__file__).parent / "assets" / assetName         # import files with the same name.
    newPath = shutil.copyfile(filepath, path)
    return str(newPath)

class Pinn(QWidget):
    backgroundColor = defaultBackgroundColor
    headerColor = defaultTextColor
    bodyColor = defaultTextColor
    bodyText = None
    bodyImage = None
    bodyAudio = None
    filepath = None

    def getColor(self, part):
        if part == "Header": return darkenHex(self.backgroundColor, 0.88)
        elif part == "Hover": return darkenHex(self.backgroundColor, 0.74)
        elif part == "Corner": return darkenHex(self.backgroundColor, 0.64)
        elif part == "Outline": return darkenHex(self.backgroundColor, 0.58)
        else: return self.backgroundColor

    def __init__(self, parent, pinnType, filepath = None):
        super().__init__(parent)
        self.dragOffset = None
        self.setMinimumSize(minPinnSize, minPinnSize)
        self.setMaximumSize(maxPinnSize, maxPinnSize)

        if pinnType == "Text":
            self.bodyText = bodyText(self)
            self.resize(defaultTextPinnWidth, defaultTextPinnHeight)

        if pinnType == "Image":
            self.filepath = assetCreationHandler(filepath)
            self.bodyImage = bodyImage(self)
            imgWidth = self.bodyImage.image.pixmap().size().width()
            imgHeight = self.bodyImage.image.pixmap().size().height()
            if imgWidth < minPinnSize:
                imgHeight = (imgHeight / imgWidth) * minPinnSize
                imgWidth = minPinnSize
            if imgHeight < minPinnSize:
                imgWidth = (imgWidth / imgHeight) * minPinnSize
                imgHeight = minPinnSize
            if imgWidth > maxPinnSize:
                imgHeight = (imgHeight / imgWidth) * maxPinnSize
                imgWidth = maxPinnSize
            if imgHeight > maxPinnSize:
                imgWidth = (imgWidth / imgHeight) * maxPinnSize
                imgHeight = maxPinnSize
            self.resize(int(imgWidth) + 4, int(imgHeight) + 29)

        self.topBar = Header(self)
        self.resizeHandle = resizeCorner(self)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QWidget {{background-color: {self.getColor("Background")}; border: 2px solid {self.getColor("Outline")};}}
        """)

        self.raise_()
        self.show()

    def showContextMenu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet(
            f"""
            QMenu {{background-color: #FFBE34; border: none;}}
            QMenu::item {{color: {self.headerColor}; background-color: {self.getColor("Header")};}}
            QMenu::item:selected {{color: {self.headerColor}; background-color: {self.getColor("Hover")};}}
            """
        )

        delete = menu.addAction("Delete Pinn")
        font = delete.font()
        font.setBold(True)
        delete.setFont(font)

        action = menu.exec(position)
        if action == delete:
            if self.filepath is not None: Path(self.filepath).unlink(missing_ok=True)
            self.hide()
            self.deleteLater()

    def contextMenuEvent(self, event):
        self.showContextMenu(event.globalPos())
        event.accept()

    def resizeEvent(self, event):
        if self.bodyText is not None:
            self.bodyText.setGeometry(4, 2, self.width() - 8, self.height() - 31)
            self.bodyText.move(4,29)

        if self.bodyImage is not None:
            self.bodyImage.setGeometry(2, 2, self.width() - 4, self.height() - 29)
            self.bodyImage.move(2,27)

        self.topBar.setGeometry(2, 2, self.width() - 4, 25)
        self.resizeHandle.move(self.width() - self.resizeHandle.width() - 2, self.height() - self.resizeHandle.height() - 2)
        w, h = self.resizeHandle.width(), self.resizeHandle.height()
        points = [QPoint(w, 0), QPoint(0, h), QPoint(w, h)]
        self.resizeHandle.setMask(QRegion(QPolygon(points)))

        super().resizeEvent(event)



class bodyImage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.image = QLabel()
        self.image.setStyleSheet(f"background-color: {self.parentWidget().getColor("Body")}; border: none;")
        pixmap = QPixmap(self.parentWidget().filepath)
        self.image.setPixmap(pixmap)
        self.image.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.image)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.raise_()
        self.show()



class bodyText(QWidget):
    def updateFormat(self, obj):
        obj.setStyleSheet(f"background-color: {self.parentWidget().getColor("Body")}; border: none;")
        obj.setStyleSheet(f"color: {self.parentWidget().bodyColor};")

    def resizeText(self):
        newHeight = int(self.text.document().size().height())
        oldSize = self.parentWidget().size()
        if newHeight > oldSize.height() - 31 and self.text.isReadOnly() == False:
            self.parentWidget().resize(oldSize.width(), newHeight + 31)

    def __init__(self, parent):
        super().__init__(parent)

        self.text = QTextEdit()
        self.text.setAcceptRichText(False)
        self.text.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.updateFormat(self.text)
        self.text.setReadOnly(True)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.text.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.text.focusOutEvent = self.focusOutEvent
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.text.document().documentLayout().documentSizeChanged.connect(self.resizeText)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {self.parentWidget().getColor("Body")}; border: none;")

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.raise_()
        self.show()

    def mouseDoubleClickEvent(self, event):
        self.text.setReadOnly(False)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.text.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.text.setFocus()

    def focusOutEvent(self, event):
        self.text.setReadOnly(True)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)



class Header(QWidget):
    def updateFormat(self, obj):
        self.text.setStyleSheet(f"background-color: {self.parentWidget().getColor("Header")}; border: none;")
        self.text.setStyleSheet(f"color: {self.parentWidget().headerColor};")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.text.font()
        font.setBold(True)
        self.text.setFont(font)

    def __init__(self, parent):
        super().__init__(parent)
        self.dragOffset = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {self.parentWidget().getColor("Header")}; border: none;")

        self.text = QLineEdit()
        self.text.setText("New Pinn")
        self.text.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.updateFormat(self.text)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setReadOnly(True)
        self.text.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.text.focusOutEvent = self.focusOutEvent

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.raise_()
        self.show()

    def mouseDoubleClickEvent(self, event):
        self.text.setReadOnly(False)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.text.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.text.setFocus()

    def focusOutEvent(self, event):
        self.text.setReadOnly(True)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def contextMenuEvent(self, event):
        self.parentWidget().showContextMenu(event.globalPos())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragOffset = self.mapToParent(event.position().toPoint())
            self.parentWidget().raise_()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragOffset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            current_position = self.mapToParent(event.position().toPoint())
            self.parentWidget().move(self.parentWidget().pos() + current_position - self.dragOffset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragOffset = None
            event.accept()



class resizeCorner(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dragStartPosition = None
        self.originalSize = None
        self.setFixedSize(20, 20)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {self.parentWidget().getColor("Corner")}; border: none;")
        self.raise_()
        self.show()

    def contextMenuEvent(self, event):
        self.parentWidget().showContextMenu(event.globalPos())
        event.accept()

    def enterEvent(self, event):
        self.setStyleSheet(f"background-color: {self.parentWidget().getColor("Hover")}; border: none;")

    def leaveEvent(self, event):
        self.setStyleSheet(f"background-color: {self.parentWidget().getColor("Corner")}; border: none;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.globalPosition().toPoint()
            self.originalSize = self.parentWidget().size()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragStartPosition is not None and event.buttons() & Qt.MouseButton.LeftButton:
            movement = event.globalPosition().toPoint() - self.dragStartPosition

            if self.parentWidget().bodyImage is None:
                self.parentWidget().resize(self.originalSize.width() + movement.x(), self.originalSize.height() + movement.y())
            else:
                scaledWidth = self.originalSize.width() - 4
                scaledHeight = self.originalSize.height() - 29
                imgWidth = self.parentWidget().bodyImage.image.pixmap().size().width()
                imgHeight = self.parentWidget().bodyImage.image.pixmap().size().height()
                widthFactor = (scaledWidth + movement.x()) / scaledWidth
                heightFactor = (scaledHeight + movement.y()) / scaledHeight
                if widthFactor > heightFactor:
                    scaledHeight *= heightFactor
                    scaledWidth = (imgWidth / imgHeight) * scaledHeight
                else:
                    scaledWidth *= widthFactor
                    scaledHeight = (imgHeight / imgWidth) * scaledWidth
                if scaledWidth < minPinnSize:
                    scaledHeight = (imgHeight / imgWidth) * minPinnSize
                    scaledWidth = minPinnSize
                if scaledHeight < minPinnSize:
                    scaledWidth = (imgWidth / imgHeight) * minPinnSize
                    scaledHeight = minPinnSize
                if scaledWidth > maxPinnSize:
                    scaledHeight = (scaledHeight / scaledWidth) * maxPinnSize
                    scaledWidth = maxPinnSize
                if scaledHeight > maxPinnSize:
                    scaledWidth = (scaledWidth / scaledHeight) * maxPinnSize
                    scaledHeight = maxPinnSize
                self.parentWidget().resize(int(scaledWidth) + 4, int(scaledHeight) + 29)

            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = None
            self.originalSize = None
            event.accept()
