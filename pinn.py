pinnList = []
defaultTextPinnWidth = 250
defaultTextPinnHeight = 450
minImagePinnSize = 100
maxAudioPinnWidth = 450
minAudioPinnWidth = 200
defaultAudioPinnHeight = 100
defaultBackgroundColor = "FFAA1B"
defaultTextColor = "000000"
defaultFont = "Arial"
defaultHeaderSize = 14
defaultBodySize = 11
defaultCaptionSize = 12

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

    def __del__(self):
        for pinn in pinnList:
            if pinn.pinnID > self.pinnID:
                pinn.pinnID -= 1
        pinnList.remove(self)

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

class imagePinn(pinn):
    captionText = ""
    captionTextSize = defaultCaptionSize
    captionTextColor = defaultTextColor
    captionTextFont = defaultFont
    imageFilepath = None
    def __init__(self, name, captionText, imageFilepath):
        super().__init__(name)
        self.captionText = captionText
        self.imageFilepath = imageFilepath # Add a check for the image's specific dimensions later,
        self.xScale = minImagePinnSize     # with the larger dimension around 300 or 400, and the
        self.yScale = minImagePinnSize     # smaller one calculated from the image's aspect ratio.
        self.type = "Image"

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
