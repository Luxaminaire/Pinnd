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
        self.setCentralWidget(self.central_widget);


        #We made a basic button. TODO: Learn to customize it.
        self.button = QPushButton("Press Me!", self.central_widget)
        self.button.setGeometry(0, 0, 100, 100) #Define a button's size, otherwise it fills screen
        self.button.setCheckable(True)
        self.button.clicked.connect(self.the_button_was_clicked) #Determines which function is used on click

        self.button2 = QPushButton("Offset button!", self.central_widget)
        self.button2.setGeometry(150, 0, 200, 100)
        self.button2.clicked.connect(self.theOtherButton)





    #Define a behavior
    def the_button_was_clicked(self, checked=False):
        print("Clicked!")
        self.button.setText("I'm imPRESSED")
        self.setWindowTitle("This got changed too!")

    #Define a second behavior
    def theOtherButton(self, checked=False):
        self.button2.setText("setGeometry: x, y, width, height")
        self.setWindowTitle("TODO: Come up with better button names")


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


