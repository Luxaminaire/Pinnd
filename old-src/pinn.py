import os
import re
import time
from logging import error
from PIL import Image
from just_playback import Playback
from pathlib import Path
import shutil

pinnList = []
defaultTextPinnWidth = 250
defaultTextPinnHeight = 450
minPinnSize = 100
maxAudioPinnWidth = 450
minAudioPinnWidth = 200
defaultAudioPinnHeight = 100

maxHeaderLength = 75
maxCaptionLength = 75
maxBodyLength = 1000
minFontSize = 6
maxFontSize = 50

defaultBackgroundColor = "#FFAA1B"
defaultTextColor = "#000000"
defaultFont = "Arial"
defaultHeaderSize = 14
defaultBodySize = 11
defaultCaptionSize = 12

def assetCreationHandler(filepath):
    fileName, fileExtension = os.path.splitext(os.path.basename(filepath)) # Preserve file extension
    assetName = f"{int(time.time())}_{fileName}{fileExtension}" # Add timestamp so that multiple Pinns can
    path = Path(__file__).parent / "assets" / assetName         # import files with the same name.
    newPath = shutil.copyfile(filepath, path)
    return str(newPath)

def textUpdateHandler(pinn, type, text, size, font, color):
    maxLength = 0
    if type == "Header": maxLength = maxHeaderLength
    elif type == "Caption": maxLength = maxCaptionLength
    elif type == "Body": maxLength = maxBodyLength
    else: error(f'Invalid text type: {type}')

    if len(text) > maxLength: pinnText = text[:maxLength] # Truncate if needed
    else: pinnText = text

    pinnSize = min(max(size, minFontSize), maxFontSize) # Clamps the size to valid values

    pinnFont = font # Add logic later to ensure valid font name is used

    if re.fullmatch(r'^#[0-9a-fA-F]{6}$', color):
        pinnColor = color # Only update text color if valid hex code is given.
    else: pinnColor = ''

    if type == "Header":
        if text != '': pinn.headerText = pinnText
        if size != 0: pinn.headerTextSize = pinnSize
        if font != '': pinn.headerTextFont = pinnFont
        if pinnColor != '': pinn.headerTextColor = pinnColor
    if type == "Caption":
        if text != '': pinn.captionText = pinnText
        if size != 0: pinn.captionTextSize = pinnSize
        if font != '': pinn.captionTextFont = pinnFont
        if color != '': pinn.captionTextColor = pinnColor
    if type == "Body":
        if text != '': pinn.bodyText = pinnText
        if size != 0: pinn.bodyTextSize = pinnSize
        if font != '': pinn.bodyTextFont = pinnFont
        if color != '': pinn.bodyTextColor = pinnColor

class pinn:
    name = ""
    pinnID = 0
    xPos = 0
    yPos = 0
    xScale = 0
    yScale = 0
    layer = 0
    type = "Base"
    backgroundColor = defaultBackgroundColor
    pinnPIN = None

    def __init__(self, name):
        self.name = name
        pinnList.append(self)
        self.pinnID = len(pinnList)

    def updateBackgroundColor(self, color):
        if re.fullmatch(r'^#[0-9a-fA-F]{6}$', color):
            self.backgroundColor = color  # Only update text color if valid hex code is given.

    def move(self, x, y):
        self.xPos = x
        self.yPos = y

    def resize(self, x, y):
        self.xScale = max(x, minPinnSize)
        self.yScale = max(y, minPinnSize)

    def delete(self):
        for note in pinnList:
            if note.pinnID > self.pinnID:
                note.pinnID -= 1
        pinnList.remove(self)
        self.__del__()

    def __del__(self):
        print(f'Pinn "{self.name}" Deleted')

class textPinn(pinn):
    headerText = ""
    headerTextSize = defaultHeaderSize
    headerTextColor = defaultTextColor
    headerTextFont = defaultFont
    bodyText = ""
    bodyTextSize = defaultBodySize
    bodyTextColor = defaultTextColor
    bodyTextFont = defaultFont

    def __init__(self, name, headerText, bodyText):
        super().__init__(name)
        self.type = "Text"
        self.headerText = headerText
        self.bodyText = bodyText
        self.xScale = defaultTextPinnWidth
        self.yScale = defaultTextPinnHeight

    def updateHeader(self, text = '', size = 0, font = '', color = ''):
        textUpdateHandler(self, "Header", text, size, font, color)

    def updateBody(self, text = '', size = 0, font = '', color = ''):
        textUpdateHandler(self, "Body", text, size, font, color)

class imagePinn(pinn):
    captionText = ""
    captionTextSize = defaultCaptionSize
    captionTextColor = defaultTextColor
    captionTextFont = defaultFont
    imageFilepath = None
    imageSizeX = 0
    imageSizeY = 0

    def __init__(self, name, captionText, imageFilepath):
        super().__init__(name)
        self.type = "Image"
        self.captionText = captionText
        self.updateImage(imageFilepath)

    def delete(self):
        Path(self.imageFilepath).unlink(missing_ok = True)
        super().delete()

    def updateCaption(self, text = '', size = 0, font = '', color = ''):
        textUpdateHandler(self, "Caption", text, size, font, color)

    def readjustSize(self):
        if self.imageSizeX <= 0 or self.imageSizeY <= 0:
            return -1 # Return a special value to warn the caller that the image is invalid.
        if self.imageSizeX > self.xScale or self.imageSizeY > self.yScale:
            self.xScale = self.imageSizeX
            self.yScale = self.imageSizeY

            if self.xScale < minPinnSize: # Resize Pinn if image is too small
                self.yScale *= minPinnSize / self.xScale
                self.xScale = minPinnSize
            if self.yScale < minPinnSize:
                self.xScale *= minPinnSize / self.yScale
                self.yScale = minPinnSize
            return True # Pinn was successfully enlarged to fit image size.

        if self.xScale < minPinnSize: self.xScale = minPinnSize
        self.yScale = round(self.xScale * (self.imageSizeY / self.imageSizeX))
        return False # Pinn was set to correct aspect ratio, but not enlarged.

    def updateImage(self, filepath):
        self.imageFilepath = assetCreationHandler(filepath)
        try:
            with Image.open(self.imageFilepath) as imageImport:
                self.imageSizeX = imageImport.size[0]
                self.imageSizeY = imageImport.size[1]
        except FileNotFoundError:
            error("Error importing image to Pinn!")
        if self.readjustSize() == -1:
            error("Error reading image file: Could not resolve image size!")

class audioPinn(pinn):
    headerText = ""
    headerTextSize = defaultHeaderSize
    headerTextColor = defaultTextColor
    headerTextFont = defaultFont
    audioPlayer = Playback()
    audioFilepath = None
    audioLength = 0

    def __init__(self, name, headerText, audioFilepath):
        super().__init__(name)
        self.type = "Audio"
        self.headerText = headerText
        self.updateAudio(audioFilepath)
        self.yScale = defaultAudioPinnHeight

    def delete(self):
        self.audioPlayer.close()
        Path(self.audioFilepath).unlink(missing_ok = True)
        super().delete()

    def updateHeader(self, text = '', size = 0, font = '', color = ''):
        textUpdateHandler(self, "Header", text, size, font, color)

    def updateAudio(self, filepath):
        self.audioFilepath = assetCreationHandler(filepath)
        self.audioPlayer.load_file(self.audioFilepath)
        self.audioLength = self.audioPlayer.duration
        self.xScale = minAudioPinnWidth + min(self.audioLength, maxAudioPinnWidth)

    def play(self, startTime = 0):
        if startTime != 0: self.audioPlayer.seek(startTime)
        self.audioPlayer.play()
    def pause(self): self.audioPlayer.pause()
    def resume(self): self.audioPlayer.resume()
    def stop(self): self.audioPlayer.stop()
