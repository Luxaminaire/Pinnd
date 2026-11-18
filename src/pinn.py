import colorsys
import os
import shutil
import time
from pathlib import Path
from PySide6.QtCore import Qt, QPoint, QUrl
from PySide6.QtGui import QRegion, QPolygon, QPixmap, QPainter, QColor, QIcon, QFont, QAction
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QWidget, QPushButton, QMenu, QVBoxLayout, QLineEdit, QTextEdit,
    QSizePolicy, QLabel, QSlider, QHBoxLayout, QColorDialog, QMessageBox, QWidgetAction,
)

pinnList = []

defaultTextPinnWidth = 250
defaultTextPinnHeight = 350
minPinnSize = 100
maxPinnSize = 600
maxAudioPinnWidth = 500
minAudioPinnWidth = 180
audioPinnHeight = 114
minFontSize = 6
maxFontSize = 20
defaultBackgroundColor = "#FFCC5E"
defaultTextColor = "#000000"
defaultFont = "Arial"
defaultHeaderSize = 12
defaultBodySize = 10

def recolor(pixmap, color):
    """Recolors a given image using the color provided to the function."""
    colored = QPixmap(pixmap.size())
    colored.fill(Qt.GlobalColor.transparent)
    painter = QPainter(colored)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(colored.rect(), QColor(color))
    painter.end()
    return colored

def darkenHex(color, factor):
    """Darkens a given hex code by the factor provided to the function."""
    hex_color = color.lstrip('#')
    r, g, b = (int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4)) # Translate into RGB to be manipulated easier.
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, l * factor, s)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}" # Translate back into a hex code to be directly used by widgets.

def getColor(pinn, part):
    """Returns a color corresponding to the provided area of the Pinn to ensure consistent color matching."""
    if part == "Header": return darkenHex(pinn.backgroundColor, 0.88)
    elif part == "Hover": return darkenHex(pinn.backgroundColor, 0.74)
    elif part == "Corner": return darkenHex(pinn.backgroundColor, 0.64)
    elif part == "Outline": return darkenHex(pinn.backgroundColor, 0.58)
    elif part == "Dark": return darkenHex(pinn.backgroundColor, 0.33)
    else: return pinn.backgroundColor

def assetCreationHandler(filepath, imported):
    """Handles the creation of asset filepaths by duplicating a file and saving it to the assets folder,
    rendering it permanently accessible within the Pinnboard even if the original file is moved or deleted."""
    if imported:
        return filepath # Asset has already been created, no need to copy any files!
    else:
        fileName, fileExtension = os.path.splitext(os.path.basename(filepath)) # Preserve file extension and add a
        assetName = f"{int(time.time())}_{fileName}{fileExtension}"            # timestamp so that multiple Pinns can
        path = Path.cwd() / "assets" / assetName                               # import files with the same name.

        shutil.copyfile(filepath, path)
        return assetName

class Pinn(QWidget):
    backgroundColor = defaultBackgroundColor
    headerColor = defaultTextColor
    bodyColor = defaultTextColor
    headerSize = defaultHeaderSize
    bodySize = defaultBodySize
    headerFont = defaultFont
    bodyFont = defaultFont
    bodyText = None
    bodyImage = None
    bodyAudio = None
    filepath = None
    dragOffset = None

    def __init__(self, parent, pinnType, filepath = None, imported = False):
        super().__init__(parent)
        self.setMinimumSize(minPinnSize, minPinnSize)
        self.setMaximumSize(maxPinnSize, maxPinnSize)

        if pinnType == "Text":
            self.bodyText = bodyText(self)
            self.resize(defaultTextPinnWidth, defaultTextPinnHeight)

        if pinnType == "Image":
            self.filepath = assetCreationHandler(filepath, imported)
            self.bodyImage = bodyImage(self)
            imgWidth = self.bodyImage.image.pixmap().size().width()
            imgHeight = self.bodyImage.image.pixmap().size().height()
            if imgWidth < minPinnSize: # Check minimum size limits and shrink the Pinn as needed to comply.
                imgHeight = (imgHeight / imgWidth) * minPinnSize
                imgWidth = minPinnSize
            if imgHeight < minPinnSize:
                imgWidth = (imgWidth / imgHeight) * minPinnSize
                imgHeight = minPinnSize
            if imgWidth > maxPinnSize: # Check maximum size limits and enlarge the Pinn as needed to comply.
                imgHeight = (imgHeight / imgWidth) * maxPinnSize
                imgWidth = maxPinnSize
            if imgHeight > maxPinnSize:
                imgWidth = (imgWidth / imgHeight) * maxPinnSize
                imgHeight = maxPinnSize
            self.resize(int(imgWidth) + 4, int(imgHeight) + 29) # Compensate for the border & header to ensure the
                                                                # image retains the correct aspect ratio.
        if pinnType == "Audio":
            self.filepath = assetCreationHandler(filepath, imported)
            self.bodyAudio = bodyAudio(self)
            self.setMinimumSize(minAudioPinnWidth, audioPinnHeight)
            self.setMaximumSize(maxPinnSize, audioPinnHeight) # Audio Pinns cannot be resized vertically!

        self.topBar = Header(self)
        self.resizeHandle = resizeCorner(self)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QWidget {{background-color: {getColor(self, 'Background')}; border: 2px solid {getColor(self, 'Outline')};}}
        """)

        self.raise_()
        self.show()

    def showContextMenu(self, position, origin):
        menu = QMenu(self)
        menu.setStyleSheet( # Context menu should inherit the Pinn's colors.
            f"""
            QMenu {{background-color: {getColor(self, 'Header')}; border: none;}}
            QMenu::item {{color: {self.headerColor}; background-color: {getColor(self, 'Header')};}}
            QMenu::item:selected {{color: {self.headerColor}; background-color: {getColor(self, 'Hover')};}}
            QMenu::separator {{background:{self.headerColor}; height: 1px; margin-top: 5px; margin-bottom: 5px;}}
            """
        )
        menu.setFixedWidth(150)
        font = QFont(defaultFont, 10)
        font.setBold(True)

        headerColor, bodyColor = None, None

        if origin == "Header":
            headerColor = menu.addAction("Header Text Color")
            headerColor.setFont(font)
        if origin == "BodyText" or origin == "BodyAudio":
            bodyColor = menu.addAction("Body Text Color")
            bodyColor.setFont(font)
        bgColor = menu.addAction("Background Color")
        menu.addSeparator()
        delete = menu.addAction("Delete Pinn")
        bgColor.setFont(font)
        delete.setFont(font)

        action = menu.exec(position)
        if action == delete:
            if self.bodyAudio is not None: self.bodyAudio.player.setSource(QUrl())
            if self.filepath is not None: Path(Path.cwd() / "assets" / self.filepath).unlink(missing_ok=True)
            pinnList.remove(self) # Remove from Pinn list so that the board does not attempt to save an invalid Pinn.
            self.hide()
            self.deleteLater()
        if action == bgColor:
            color = QColorDialog.getColor()
            self.recolor(bgColor = color.name())
        if action == headerColor and action is not None:
            color = QColorDialog.getColor()
            self.recolor(headerColor = color.name())
        if action == bodyColor and action is not None:
            color = QColorDialog.getColor()
            self.recolor(bodyColor = color.name())

    def recolor(self, bgColor=None, headerColor=None, bodyColor=None):
        if bgColor is not None: self.backgroundColor = bgColor
        if headerColor is not None: self.headerColor = headerColor
        if bodyColor is not None: self.bodyColor = bodyColor

        self.setStyleSheet(f"""
            QWidget {{background-color: {getColor(self, 'Background')}; border: 2px solid {getColor(self, 'Outline')};}}
        """)
        self.topBar.setStyleSheet(f"background-color: {getColor(self, 'Header')}; border: none;")
        self.topBar.updateFormat(self.topBar.text)
        self.resizeHandle.setStyleSheet(f"background-color: {getColor(self, 'Corner')}; border: none;")
        if self.bodyText is not None: # Recoloring steps unique to Text Pinns.
            self.bodyText.setStyleSheet(f"background-color: {getColor(self, 'Body')}; border: none;")
            self.bodyText.updateFormat(self.bodyText.text)
        if self.bodyImage is not None: # Recoloring steps unique to Image Pinns.
            self.bodyImage.image.setStyleSheet(f"background-color: {getColor(self, 'Body')}; border: none;")
        if self.bodyAudio is not None: # Recoloring steps unique to Audio Pinns.
            buttonStyle = f"""
                QPushButton {{background-color: {getColor(self, 'Header')}; color: {self.headerColor}; border: none;}}
                QPushButton:hover {{background-color: {getColor(self, 'Hover')}; color: {self.headerColor}; border: none;}}
            """
            loopStyle = f"""
                QPushButton {{background-color: {getColor(self, 'Corner')}; color: {self.headerColor}; border: none;}}
                QPushButton:hover {{background-color: {getColor(self, 'Outline')}; color: {self.headerColor}; border: none;}}
            """
            self.bodyAudio.play.setStyleSheet(buttonStyle)
            if self.bodyAudio.paused: # Ensure the correct icon is applied based on whether the audio is playing or paused.
                pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioPlay.png"), self.bodyColor)
                self.bodyAudio.play.setIcon(QIcon(pixmap))
            else:
                pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioPause.png"), self.bodyColor)
                self.bodyAudio.play.setIcon(QIcon(pixmap))
            pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioStop.png"), self.bodyColor)
            self.bodyAudio.stop.setIcon(QIcon(pixmap))
            pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioLoop.png"), self.bodyColor)
            self.bodyAudio.loop.setIcon(QIcon(pixmap))

            if self.bodyAudio.looped: # Ensure the loop button remains darker if the audio is currently looping.
                self.bodyAudio.loop.setStyleSheet(loopStyle)
            else:
                self.bodyAudio.loop.setStyleSheet(buttonStyle)
            self.bodyAudio.stop.setStyleSheet(buttonStyle)
            self.bodyAudio.time.setStyleSheet(f"""
                background-color: {getColor(self, 'Header')}; color: {self.headerColor}; border: none;
            """)
            self.bodyAudio.slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{border: none; height: 6px;}}
                QSlider::handle:horizontal {{background: {getColor(self, 'Hover')}; border: 4px solid {getColor(self, 'Dark')};
                width: 8px; height: 12px; margin: -5px 0; border-radius: 8px;}}
                QSlider::sub-page:horizontal {{background: {getColor(self, 'Corner')}; border: none;}}
                QSlider::add-page:horizontal {{background: #FFFFFF; border: none;}}
                background-color: {getColor(self, 'Body')}; color: {self.headerColor}; border: none;
            """)

    def resizeEvent(self, event):
        if self.bodyText is not None: # Resizing steps unique to Text Pinns.
            self.bodyText.setGeometry(4, 2, self.width() - 8, self.height() - 31)
            self.bodyText.move(4,29)

        if self.bodyImage is not None: # Resizing steps unique to Image Pinns.
            self.bodyImage.setGeometry(2, 2, self.width() - 4, self.height() - 29)
            self.bodyImage.move(2,27)

        if self.bodyAudio is not None: # Resizing steps unique to Audio Pinns.
            self.bodyAudio.setGeometry(2, 2, self.width() - 4, self.height() - 29)
            self.bodyAudio.move(2, 27)

        self.topBar.setGeometry(2, 2, self.width() - 4, 25)
        self.resizeHandle.move(self.width() - self.resizeHandle.width() - 2, self.height() - self.resizeHandle.height() - 2)
        w, h = self.resizeHandle.width(), self.resizeHandle.height()
        points = [QPoint(w, 0), QPoint(0, h), QPoint(w, h)]
        self.resizeHandle.setMask(QRegion(QPolygon(points)))

        super().resizeEvent(event)



class bodyAudio(QWidget):
    def contextMenuEvent(self, event): # Refer all context menu events to the parent Pinn object.
        self.parentWidget().showContextMenu(event.globalPos(),"BodyAudio")
        event.accept()

    def __init__(self, parent):
        super().__init__(parent)

        self.player = QMediaPlayer()
        self.output = QAudioOutput()
        self.player.setAudioOutput(self.output)
        self.player.setSource(QUrl.fromLocalFile(Path.cwd() / "assets" / self.parentWidget().filepath))
        self.parentWidget().audioLength = self.player.duration()

        self.paused = True
        self.looped = False

        self.play = QPushButton()
        pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioPlay.png"), self.parentWidget().bodyColor)
        self.play.setIcon(QIcon(pixmap))

        self.stop = QPushButton()
        pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioStop.png"), self.parentWidget().bodyColor)
        self.stop.setIcon(QIcon(pixmap))

        self.loop = QPushButton()
        pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioLoop.png"), self.parentWidget().bodyColor)
        self.loop.setIcon(QIcon(pixmap))

        buttonStyle = f"""
            QPushButton {{background-color: {getColor(self.parentWidget(), 'Header')};
            color: {self.parentWidget().headerColor}; border: none;}}
            QPushButton:hover {{background-color: {getColor(self.parentWidget(), 'Hover')};
            color: {self.parentWidget().headerColor}; border: none;}}
        """
        self.play.setStyleSheet(buttonStyle)
        self.stop.setStyleSheet(buttonStyle)
        self.loop.setStyleSheet(buttonStyle)
        self.play.setFixedHeight(21)
        self.stop.setFixedHeight(21)
        self.loop.setFixedHeight(21)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{border: none; height: 6px;}}
            QSlider::handle:horizontal {{
                background: {getColor(self.parentWidget(), 'Hover')};
                border: 4px solid {getColor(self.parentWidget(), 'Dark')};
                width: 8px;
                height: 12px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{background: {getColor(self.parentWidget(), 'Corner')}; border: none;}}
            QSlider::add-page:horizontal {{background: #FFFFFF; border: none;}}
            background-color: {getColor(self.parentWidget(), 'Body')}; color: {self.parentWidget().headerColor}; border: none;
        """)
        self.time = QLabel("00:00 / 00:00")
        self.time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time.setStyleSheet(f"""
            background-color: {getColor(self.parentWidget(), 'Header')}; color: {self.parentWidget().headerColor}; border: none;
        """)

        display = QHBoxLayout() # Create a layout and insert the audio buttons to allow the user to interact with the Pinn.
        display.addWidget(self.play)
        display.addWidget(self.stop)
        display.addWidget(self.loop)

        layout = QVBoxLayout() # Create another layout to handle the overall Pinn layout.
        layout.addLayout(display)
        layout.addWidget(self.slider)
        layout.addWidget(self.time)
        self.setLayout(layout)

        self.play.clicked.connect(self.playClick)
        self.loop.clicked.connect(self.loopClick)
        self.stop.clicked.connect(self.stopClick)

        self.player.durationChanged.connect(self.updateDuration)
        self.player.positionChanged.connect(self.updatePosition)
        self.slider.sliderPressed.connect(self.pressPosition) # Allow the user to skip through the audio by clicking the slider.
        self.slider.sliderMoved.connect(self.setPosition)

        self.player.playbackStateChanged.connect(self.loopCheck) # Check if the audio should loop once it finishes playing.

        self.raise_()
        self.show()

    def playClick(self):
        if self.paused: # Update icon so that the user knows the audio is now playing, and can be paused by clicking the button.
            pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioPause.png"), self.parentWidget().bodyColor)
            self.play.setIcon(QIcon(pixmap))
            self.player.play()
            self.paused = False
        else: # Update icon so that the user knows the audio is now paused, and can be played by clicking the button.
            pixmap = recolor(QPixmap(Path.cwd() / "icons" / "audioPlay.png"), self.parentWidget().bodyColor)
            self.play.setIcon(QIcon(pixmap))
            self.player.pause()
            self.paused = True

    def stopClick(self):
        if self.looped: self.loopClick()
        self.player.stop()

    def loopClick(self):
        if self.looped: # Lighten the loop button so that the user knows the audio is no longer looping.
            self.loop.setStyleSheet(f"""
                QPushButton {{background-color: {getColor(self.parentWidget(), 'Header')};
                color: {self.parentWidget().headerColor}; border: none;}}
                QPushButton:hover {{background-color: {getColor(self.parentWidget(), 'Hover')};
                color: {self.parentWidget().headerColor}; border: none;}}
            """)
            self.looped = False
        else: # Darken the loop button so the user knows the audio is now looping.
            self.loop.setStyleSheet(f"""
                QPushButton {{background-color: {getColor(self.parentWidget(), 'Corner')};
                color: {self.parentWidget().headerColor}; border: none;}}
                QPushButton:hover {{background-color: {getColor(self.parentWidget(), 'Outline')};
                color: {self.parentWidget().headerColor}; border: none;}}
            """)
            self.looped = True

    def loopCheck(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.looped:
                self.player.setPosition(0)
                self.player.play()
            elif not self.paused:
                self.playClick()
                self.player.setPosition(0)

    def updateDuration(self, duration):
        width = minAudioPinnWidth + min(duration/300, maxAudioPinnWidth)
        self.parentWidget().resize(int(width) + 4, audioPinnHeight)
        self.slider.setMaximum(duration)
        pos_sec = self.player.position() // 1000
        dur_sec = self.player.duration() // 1000
        self.time.setText(
            f"{pos_sec // 60:02d}:{pos_sec % 60:02d} / {dur_sec // 60:02d}:{dur_sec % 60:02d}"
        )
    def updatePosition(self, position):
        if not self.slider.isSliderDown(): self.slider.setValue(position)
        pos_sec = position // 1000
        dur_sec = self.player.duration() // 1000
        self.time.setText(
            f"{pos_sec // 60:02d}:{pos_sec % 60:02d} / {dur_sec // 60:02d}:{dur_sec % 60:02d}"
        )

    def pressPosition(self): self.player.setPosition(self.slider.value())
    def setPosition(self, position): self.player.setPosition(position)



class bodyImage(QWidget):
    def contextMenuEvent(self, event): # Refer all context menu events to the parent Pinn object.
        self.parentWidget().showContextMenu(event.globalPos(),"BodyImage")
        event.accept()

    def __init__(self, parent):
        super().__init__(parent)

        self.image = QLabel()
        self.image.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Body")}; border: none;")
        pixmap = QPixmap(Path.cwd() / "assets" / self.parentWidget().filepath)
        self.image.setPixmap(pixmap)
        self.image.setScaledContents(True) # Ensures the image is properly scaled to fill the entire Pinn.

        layout = QVBoxLayout() # Creates the layout to display the image on the Pinn.
        layout.addWidget(self.image)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.raise_()
        self.show()



class bodyText(QWidget):
    def contextMenuEvent(self, event): # Refer all context menu events to the parent Pinn object.
        self.parentWidget().showContextMenu(event.globalPos(),"BodyText")
        event.accept()

    def updateFormat(self, obj):
        obj.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Body")}; border: none;")
        obj.setStyleSheet(f"color: {self.parentWidget().bodyColor};")

    def resizeText(self): # Automatically extends the Pinn if the user fills up all available body space.
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
        self.text.setReadOnly(True) # Text is initially read-only, but becomes editable on double-click.
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.text.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.text.focusOutEvent = self.focusOutEvent
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.text.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.text.document().documentLayout().documentSizeChanged.connect(self.resizeText)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Body")}; border: none;")

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.raise_()
        self.show()

    def mouseDoubleClickEvent(self, event): # Allows the user to edit text by making it no longer read-only.
        self.text.setReadOnly(False)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.text.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.text.setFocus()

    def focusOutEvent(self, event): # Re-locks the text, allowing the user to drag and resize the Pinn
        self.text.setReadOnly(True)              # without accidentally editing it.
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)



class Header(QWidget):
    def contextMenuEvent(self, event): # Refer all context menu events to the parent Pinn object.
        self.parentWidget().showContextMenu(event.globalPos(),"Header")
        event.accept()

    def updateFormat(self, obj):
        self.text.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Header")}; border: none;")
        self.text.setStyleSheet(f"color: {self.parentWidget().headerColor};")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.text.font()
        font.setBold(True)
        self.text.setFont(font)

    def __init__(self, parent):
        super().__init__(parent)
        self.dragOffset = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Header")}; border: none;")

        self.text = QLineEdit()
        self.text.setText("New Pinn")
        self.text.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.updateFormat(self.text)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setReadOnly(True) # Text is initially read-only, but becomes editable on double-click.
        self.text.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.text.focusOutEvent = self.focusOutEvent

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.raise_()
        self.show()

    def mouseDoubleClickEvent(self, event): # Allows the user to edit text by making it no longer read-only.
        self.text.setReadOnly(False)
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.text.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.text.setFocus()

    def focusOutEvent(self, event): # Re-locks the text, allowing the user to drag and resize the Pinn
        self.text.setReadOnly(True)              # without accidentally editing it.
        self.text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def mousePressEvent(self, event): # Initiates a drag when the user clicks the header.
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragOffset = self.mapToParent(event.position().toPoint())
            self.parentWidget().raise_()
            event.accept()

    def mouseMoveEvent(self, event): # Drags the Pinn alongside the mouse when it is moved.
        if self.dragOffset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            current_position = self.mapToParent(event.position().toPoint())
            self.parentWidget().move(self.parentWidget().pos() + current_position - self.dragOffset)
            event.accept()

    def mouseReleaseEvent(self, event): # Releases the Pinn when the user stops clicking.
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragOffset = None
            event.accept()



class resizeCorner(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dragStartPosition = None
        self.originalSize = None
        self.setFixedSize(15, 15)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Corner")}; border: none;")
        self.raise_()
        self.show()

    def contextMenuEvent(self, event):
        self.parentWidget().showContextMenu(event.globalPos(),"Body") # Refer all context menu events to the parent Pinn object.
        event.accept()

    def enterEvent(self, event): # Highlights the corner so the user knows it is interactable.
        self.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Hover")}; border: none;")

    def leaveEvent(self, event): # Unhighlights the corner once the user moves away.
        self.setStyleSheet(f"background-color: {getColor(self.parentWidget(), "Corner")}; border: none;")

    def mousePressEvent(self, event): # Initiates a resize when the corner is clicked.
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.globalPosition().toPoint()
            self.originalSize = self.parentWidget().size()
            event.accept()

    def mouseMoveEvent(self, event): # Resizes the Pinn proportionally when the mouse is dragged.
        if self.dragStartPosition is not None and event.buttons() & Qt.MouseButton.LeftButton:
            movement = event.globalPosition().toPoint() - self.dragStartPosition

            if self.parentWidget().bodyText is not None: # Text Pinns can be freely resized in both dimensions.
                self.parentWidget().resize(self.originalSize.width() + movement.x(), self.originalSize.height() + movement.y())
            if self.parentWidget().bodyImage is not None: # Image Pinns must keep a consistent aspect ratio when resized.
                scaledWidth = self.originalSize.width() - 4
                scaledHeight = self.originalSize.height() - 29
                imgWidth = self.parentWidget().bodyImage.image.pixmap().size().width()
                imgHeight = self.parentWidget().bodyImage.image.pixmap().size().height()
                widthFactor = (scaledWidth + movement.x()) / scaledWidth
                heightFactor = (scaledHeight + movement.y()) / scaledHeight
                if widthFactor > heightFactor: # Check maximum and minimum bounds after scaling.
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
            if self.parentWidget().bodyAudio is not None: # Audio Pinns can only be scaled horizontally.
                self.parentWidget().resize(self.originalSize.width() + movement.x(), audioPinnHeight)

            event.accept()

    def mouseReleaseEvent(self, event): # Releases the Pinn when the user stops clicking.
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = None
            self.originalSize = None
            event.accept()
