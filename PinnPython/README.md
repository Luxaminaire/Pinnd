Before this project gets turned into an executable, we will be working with its source code.

However, to work on this project, you will need...

-Python
-PySide6 installed (and 'long path names' enabled)
-Any images or resources the program needs

The Pinnboard.py is all that's needed to run the app for now,
we will have to figure out reading and writing to/from SQL and files later.

Using AI help, apparently a virtual environment is needed to run this,
but with explicit instructions NOT to share this environment, that it needs to be local.

.gitignore, thus, ignores uploading .venv when uploading to Github.

Create your own .venv virtual environment, navigating to the file, and in the terminal...

python -m venv .venv
.venv\Scripts\activate.bat

A .venv file should show up.

Once this environment is activated, if you don't have PySide6, install it:

python -m pip install PySide6

If .venv is correctly in the folder with the project and PySide6 is installed, that test_pyside.py should run fine.
If you run into a filepath error, enable 'long path names' and restart your rig.

###

Finally, here's a nice tutorial on Python GUIs using PySide6:
https://www.pythonguis.com/tutorials/pyside6-creating-your-first-window/#what-is-the-qt-event-loop

###

QWidget has a LOT of classes and functions. QToolBar, QTooltip, QLabel, QToolButton, functions like qDrawPlainRect() and qDrawInPanel(), and more.

Documentation at:
https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html