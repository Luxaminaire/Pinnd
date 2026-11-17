"""
searchFunction.py - Search bar for Pinn-D.

Searches the title (and body text, for Text Pinns) of every Pinn in pinn.pinnList.
Pinns that match stay normal; everything else fades out. Clearing the box restores all Pinns.

Usage in main.py:
    from search import SearchToolBar
    self.searchBar = SearchToolBar(self)
    self.addToolBar(self.searchBar)
"""

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QToolBar, QLineEdit, QGraphicsOpacityEffect

import pinn

FADED_OPACITY = 0.25  # How see-through non-matching Pinns become (0.0 - 1.0)


def pinnText(item):
    """Return (title, body) for a Pinn. Image/Audio Pinns have no body text."""
    title = item.topBar.text.text()
    body = item.bodyText.text.toPlainText() if item.bodyText is not None else ""
    return title, body


def pinnMatches(item, term):
    """Case-insensitive check of a Pinn's title and body against a lowercase search term."""
    if not term:
        return True
    title, body = pinnText(item)
    return term in title.lower() or term in body.lower()


def applySearch(query):
    """Fade every Pinn that doesn't match the query. An empty query restores everything."""
    term = query.strip().lower()
    for item in pinn.pinnList:
        effect = item.graphicsEffect()
        if pinnMatches(item, term):
            if effect is not None:
                item.setGraphicsEffect(None)  # Back to normal
        else:
            if effect is None:
                effect = QGraphicsOpacityEffect(item)
                effect.setOpacity(FADED_OPACITY)
                item.setGraphicsEffect(effect)


class SearchToolBar(QToolBar):
    def __init__(self, parent):
        super().__init__("Search", parent)
        self.setMovable(False)

        self.box = QLineEdit()
        self.box.setPlaceholderText("Search Pinns... (Ctrl+F)")
        self.box.setClearButtonEnabled(True)
        self.box.setFixedWidth(250)
        self.box.textChanged.connect(applySearch)
        self.addWidget(self.box)

        # Ctrl+F jumps to the search box from anywhere in the window
        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), parent)
        self.shortcut.activated.connect(self.focusSearch)

    def focusSearch(self):
        self.box.setFocus()
        self.box.selectAll()

    def refresh(self):
        """Re-apply the current search. Call this after creating a new Pinn."""
        applySearch(self.box.text())
