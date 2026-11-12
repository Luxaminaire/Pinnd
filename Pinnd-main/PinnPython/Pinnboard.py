#From ChatGPT, after installing PySide6, these are the instructions to create a blank window
#Without PySide6, and without enabling long path names, this will not work

import sys

#"QSize" allows resizing widgets. 
from PySide6.QtCore import QSize, Qt

#QApplication is needed for events, QWidget has many objects and functions
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QMenu


#This is a first attempt at a draggable note class
#This draggableNote's mouse events are local, they only apply to the widget on top!
class draggableNote(QWidget): #Custom subclass of QWidget
    def __init__(self, parent=None): #Constructor. Initialize with (self, checked=False)
        super().__init__(parent)

        #Drag offset remembers where in a note a user has clicked. VERY relevant for pinpointing where a click happened.
        self.drag_offset = None
        self.delete_callback = None  # Set by MainWindow when this note is created

        self.setMinimumSize(100, 75)#Minimum note size
        self.resize(200, 150)#This is our default size of new notes
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        #Styling! Control color, border, and other things! CSS terms apply here!
        #Colors are ordered in R G B.
        self.setStyleSheet("""
            QWidget {
                background-color: #fff59d;
                border: 2px solid #b0b538;
            }
        """)

        #Color of the top bar of each note
        self.topBar = draggableNoteBar(self) #Widget within widget! This is the bar along the top of the note!
        self.topBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) #Color will not show if this is not included
        self.topBar.setGeometry(2, 2, self.width() - 4, 25) #All geometry calculations are made relative to the parent note
        self.topBar.setStyleSheet("""
            background-color: #d9e458;
            border: none;
            """)
        self.topBar.raise_() #The top bar has to sit ON TOP of the note
        self.topBar.show()

        #This initiates the resize cube 'handle' at the bottom-right of every bar, allowing resizing
        self.resizeHandle = noteResize(self)
        self.resizeHandle.raise_()
        self.resizeHandle.show()
        self.resizeHandle.move(
                    self.width() - self.resizeHandle.width()-2,
                    self.height() - self.resizeHandle.height()-2
                )

    def showContextMenu(self, global_position):
        # Open the menu at the mouse pointer, regardless of which part of the note was clicked.
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Pin")
        selected_action = menu.exec(global_position)

        if selected_action == delete_action and self.delete_callback is not None:
            self.delete_callback(self)  # Delete immediately; no confirmation dialog.

    def contextMenuEvent(self, event):
        self.showContextMenu(event.globalPos())
        event.accept()

    def resizeEvent(self, event): #This handles resizing of notes
        self.topBar.setGeometry(2, 2, self.width() - 4, 25) #The top bar needs to remain consistent across the top!

        self.resizeHandle.move(
        self.width() - self.resizeHandle.width() - 2,
        self.height() - self.resizeHandle.height() - 2
    )
        super().resizeEvent(event)



#This is the bar along the top that drags the note around.
#This should be the blueprint on how to create clickable 'areas' of the pin.
#Color should be handled by draggableNote itself, not here. This area down here should handle events.
class draggableNoteBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.drag_offset = None

    def contextMenuEvent(self, event):
        self.parentWidget().showContextMenu(event.globalPos())
        event.accept()

    #This is the "what happens when pressed" event
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:#Use this to determine what key determines the event.
            # Convert the click position into the note's coordinates
            self.drag_offset = self.mapToParent(
                event.position().toPoint()
            )

            self.parentWidget().raise_() #Bring this pinn above other widgets
            event.accept()

    #This is the "what happens when held/moved" event
    def mouseMoveEvent(self, event):
        if (
            self.drag_offset is not None #Remember where inside the pinn the mouse was pressed
            and event.buttons() & Qt.MouseButton.LeftButton 
        ):
            note = self.parentWidget()

            current_position = self.mapToParent(
                event.position().toPoint()
            )

            new_position = ( #Calculate the note's new position. Calculates new_position based on where the mouse is.
                note.pos() #Note's current position
                + current_position #Mouse's current position within the note
                - self.drag_offset
            )

            note.move(new_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = None
            event.accept()

#This is the noteResize widget! 
class noteResize(QWidget):
    def __init__(self, parent=None):
            super().__init__(parent)

            self.dragStartPosition = None #Keeps track of where the mouse is 'originally'
            self.originalSize = None
            self.setFixedSize(16, 16) #This is the clickable resize area

            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) #Nothing works without this, put it in every time.
            #Can change colors of the resize button to keep track of where it is, but can also remove all color too
            self.setStyleSheet("""
            QWidget {
                background-color: #c9b458;
                border: 1px solid #8f7d2f;
            }
        """)

    def contextMenuEvent(self, event):
        self.parentWidget().showContextMenu(event.globalPos())
        event.accept()

    #These are the mouse press events for pressing, holding, and releasing the mouse.
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.globalPosition().toPoint()
            self.originalSize = self.parentWidget().size()
            event.accept()

    def mouseMoveEvent(self, event):
        if (self.dragStartPosition is not None
            and event.buttons() & Qt.MouseButton.LeftButton):

            currentPosition = event.globalPosition().toPoint()
            movement = currentPosition - self.dragStartPosition

            newWidth = self.originalSize.width() + movement.x()
            newHeight = self.originalSize.height() + movement.y()

            note = self.parentWidget()

            newWidth = max(newWidth, note.minimumWidth()) #Can't shrink a note smaller than the minimum!
            newHeight = max(newHeight, note.minimumHeight())

            note.resize(newWidth, newHeight) #Now that the heights and widths are defined, use them here
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = None
            self.originalSize = None
            event.accept()



#This important subclass lets us further customize our MainWindow and its buttons.
#MainWindow is our 'background'. We can add to it using this class.
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

        #Array of notes! Important for tracking note ID
        self.noteList = []


        #We made a basic button. TODO: Learn to customize it. This is a test button, just mess around.
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





    def deletePinn(self, note):
        # Keep the internal note list in sync with the displayed widgets.
        if note in self.noteList:
            self.noteList.remove(note)
            note.hide()
            note.deleteLater()  # Qt safely destroys the widget after its current event.

    #Define a button behavior
    def the_button_was_clicked(self, checked=False):
        print("Clicked!")
        self.button.setText("I'm imPRESSED")
        self.setWindowTitle("This got changed too!")
        note = draggableNote(self.central_widget)
        note.delete_callback = self.deletePinn
        offset = len(self.noteList) * 10 #This creates notes in slightly different positions
        note.move(250 + offset, 150 + offset)
        self.noteList.append(note) #This appends the pinn to the noteList.
        note.show()

    #Define imagePinn creation behavior TODO: make
    def makeImagePinn(self, checked=False):
        self.imageButton.setText("This button will\nhandle I.Pinns")
        self.setWindowTitle("setGeometry: x, y, width, height")

    #Define textPinn creation behavior
    def makeTextPinn(self, checked=False):
        self.textButton.setText("Make this create\na text pinn")
        note = draggableNote(self.central_widget)
        note.delete_callback = self.deletePinn
        offset = len(self.noteList) * 20
        note.move(250, 150)
        self.noteList.append(note)
        note.show()

    #Define soundPinn creation behavior TODO: make
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


