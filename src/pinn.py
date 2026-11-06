from logging import error

pinnList = []
defaultTextPinnWidth = 250
defaultTextPinnHeight = 450
minImagePinnSize = 100
maxAudioPinnWidth = 450
minAudioPinnWidth = 200
defaultAudioPinnHeight = 100

maxHeaderLength = 75
maxCaptionLength = 75
maxBodyLength = 1000
minFontSize = 6
maxFontSize = 50

defaultBackgroundColor = "FFAA1B"
defaultTextColor = "000000"
defaultFont = "Arial"
defaultHeaderSize = 14
defaultBodySize = 11
defaultCaptionSize = 12

def textUpdateHandler(pinn, type, text, size, font, color):
    maxLength = 0
    if type == "Header": maxLength = maxHeaderLength
    elif type == "Caption": maxLength = maxCaptionLength
    elif type == "Body": maxLength = maxBodyLength
    else: error(f'Invalid text type: {type}')

    if len(text) > maxLength:
        pinnText = '' # Chop off extra text, will add later
    else: pinnText = text

    pinnSize = min(max(size, minFontSize), maxFontSize) # Clamps the size to valid values
    pinnFont = font # Add logic later to ensure valid font name is used
    pinnColor = color # Add logic later to ensure valid HEX code is used

    if type == "Header":
        if text != '': pinn.headerText = pinnText
        if size != 0: pinn.headerTextSize = pinnSize
        if font != '': pinn.headerTextFont = pinnFont
        if color != '': pinn.headerTextColor = pinnColor
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

    def move(self, x, y):
        self.xPos = x
        self.yPos = y

    def resize(self, x, y):
        self.xScale = x
        self.yScale = y

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
        self.headerText = headerText
        self.bodyText = bodyText
        self.xScale = defaultTextPinnWidth
        self.yScale = defaultTextPinnHeight
        self.type = "Text"

    def updateHeader(self, text, size, font, color):
        textUpdateHandler(self, "Header", text, size, font, color)

    def updateBody(self, text, size, font, color):
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
        self.captionText = captionText
        self.imageFilepath = imageFilepath # Add a check for the image's specific dimensions later,
        self.xScale = minImagePinnSize     # with the larger dimension around 300 or 400, and the
        self.yScale = minImagePinnSize     # smaller one calculated from the image's aspect ratio.
        self.imageSizeX = 0
        self.imageSizeY = 0
        self.type = "Image"

    def updateCaption(self, text, size, font, color):
        textUpdateHandler(self, "Caption", text, size, font, color)

    def readjustSize(self):
        if self.imageSizeX <= 0 or self.imageSizeY <= 0:
            return -1 # Return a special value to warn the caller that it may need to re-import the image.
        if self.imageSizeX > self.xScale or self.imageSizeY > self.yScale:
            self.xScale = self.imageSizeX
            self.yScale = self.imageSizeY
            return True # Pinn was successfully resized.
        return False # Pinn did not need to be resized.

    def updateImage(self, filepath):
        # Write logic to import image from filepath
        self.imageSizeX = 0 # Replace with image's X & Y size in pixels
        self.imageSizeY = 0
        if self.readjustSize() == -1:
            error("Error reading image file: Read invalid dimensions!")
        else:
            self.imageFilepath = filepath

class audioPinn(pinn):
    headerText = ""
    headerTextSize = defaultHeaderSize
    headerTextColor = defaultTextColor
    headerTextFont = defaultFont
    audioFilepath = None
    audioLength = 0
    def __init__(self, name, headerText, audioFilepath):
        super().__init__(name)
        self.headerText = headerText
        self.audioFilepath = audioFilepath
        self.audioLength = 0 # Replace with a check for the length of the audio file in seconds
        self.xScale = minAudioPinnWidth + min(self.audioLength, maxAudioPinnWidth)
        self.yScale = defaultAudioPinnHeight
        self.type = "Audio"

    def updateHeader(self, text, size, font, color):
        textUpdateHandler(self, "Header", text, size, font, color)

    def updateAudio(self, filepath):
        FAKELEN = 10 # Write logic to import audio from filepath
        if FAKELEN > 0:
            self.audioLength = FAKELEN
            self.audioFilepath = filepath
        else:
            error("Error reading audio file: Read a non-positive length.")
