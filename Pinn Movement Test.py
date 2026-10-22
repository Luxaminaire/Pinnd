#Everything in one file for the time being, will separate into multiple files once complexity begins rising.
globalPinnID = 0 #Global Pinn ID that stays consistent for all three types of Pinns (text, image, audio).

class Pinn: #Pinn superclass with basic information. Will add more details such as scale values & PIN protection later.
    name = ""
    pinnID = 0
    xPos = 0
    yPos = 0
    layer = 0
    
    def __init__(self, name):
        global globalPinnID
        globalPinnID += 1
        self.name = name
        self.pinnID = globalPinnID

    def move(self, x, y):
        self.xPos = x
        self.yPos = y
        
class TextPinn(Pinn): #Text Pinn subclass, with header & body text. Will add more details such as fonts & colors later.
    headerText = ""
    bodyText = ""
    
    def __init__(self, name, headerText, bodyText):
        super().__init__(name)
        self.headerText = headerText
        self.bodyText = bodyText

def dragPinn(pinn): #Function simplified until GUI framework has been chosen.
    test = 0
    while test < 10: #Loop until test value is 10 instead of waiting for mouse to be released since we don't have a GUI yet.
        pinn.move(test,0)
        test += 1

testPinn = TextPinn("Test Pinn", "Test Header", "This is a body text!")
dragPinn(testPinn)
