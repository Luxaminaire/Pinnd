pinnList = []

class pinn:
    name = ""
    pinnID = 0
    xPos = 0
    yPos = 0
    xScale = 0
    yScale = 0
    layer = 0
    type = "Base"
    def __init__(self, name):
        self.name = name
        pinnList.append(self)
        self.pinnID = len(pinnList)

    def move(self, x, y):
        self.xPos = x
        self.yPos = y

class textPinn(pinn):
    headerText = ""
    bodyText = ""
    def __init__(self, name, headerText, bodyText):
        super().__init__(name)
        self.headerText = headerText
        self.headerTextSize = 14
        self.bodyText = bodyText
        self.bodyTextSize = 11
        self.xScale = 250
        self.yScale = 450
        self.type = "Text"
