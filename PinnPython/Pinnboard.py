#From ChatGPT, after installing PySide6, these are the instructions to create a blank window
#Without PySide6, and without enabling long path names, this will not work

import sys

#"QSize" allows resizing widgets. 
from PySide6.QtCore import QSize, Qt

#QApplication is needed for events, QWidget has many objects and functions
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton

#This subclass lets us further customize our MainWindow and its buttons.
#MainWindow is our 'background'. We can leave it generic, or add to it using this subclass.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMouseTracking(True) #This adds mouse tracking. TODO: Learn mouseMove events.

        self.setWindowTitle("Pinnboard 1")
        #.setFixedSize(), .setMinimumSize(), and .setMaximumSize() are also possible
        self.setMinimumSize(QSize(400, 300))

        #Sets a single central widget for entire window. Can have many buttons.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)


        #We made a basic button. TODO: Learn to customize it.
        self.button = QPushButton("Press Me!", self.central_widget)
        self.button.setGeometry(0, 0, 100, 100) #Define a button's size, otherwise it fills screen
        self.button.setCheckable(True)
        self.button.clicked.connect(self.the_button_was_clicked) #Determines which function is used on click

        #MakeImage button
        self.imageButton = QPushButton("Offset button!", self.central_widget)
        self.imageButton.setGeometry(100, 0, 100, 100)
        self.imageButton.clicked.connect(self.makeImagePinn)

        #MakeText button
        self.textButton = QPushButton("Text Note button!", self.central_widget)
        self.textButton.setGeometry(100, 100, 100, 100)
        self.textButton.clicked.connect(self.makeTextPinn)

        #MakeSound button
        self.soundButton = QPushButton("Sound Pinn \nbutton!", self.central_widget)
        self.soundButton.setGeometry(0, 100, 100, 100)
        self.soundButton.clicked.connect(self.makeSoundPinn)





    #Define a behavior
    def the_button_was_clicked(self, checked=False):
        print("Clicked!")
        self.button.setText("I'm imPRESSED")
        self.setWindowTitle("This got changed too!")

    #Define a second behavior
    def makeImagePinn(self, checked=False):
        self.imageButton.setText("This button will\nhandle I.Pinns")
        self.setWindowTitle("setGeometry: x, y, width, height")

    def makeTextPinn(self, checked=False):
        self.textButton.setText("Make this create\na text pinn")

    def makeSoundPinn(self, checked=False):
        self.soundButton.setText("Make this create\na sound pinn")




#One QApplication instance per application
#Can be QApplication([]) if we don't intend to pass any arguments
#Holds 'event loop', listens for clicks and presses.
app = QApplication(sys.argv)





#In QT, 'top' widgets are windows. Things can be placed on them, they can't go on anything else.
#This window holds our UI.
window = MainWindow()
window.setWindowTitle("Pinnboard or PinnBoard?")
window.resize(1000, 700) #Establishes a default size, but can be shrunk/expanded elswhere.
window.show()

#Do not write any gui-related code after app.exec()!
app.exec()


