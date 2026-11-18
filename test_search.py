"""
test_search.py - Unit tests for the Pinn-D search feature.

Run it in PyCharm: right-click the file -> Run 'Python tests in test_search'.
Or from a terminal in that folder:  python -m unittest test_search -v
"""
import os
import sys
import unittest

# Run Qt without opening real windows, so tests also work on machines with no display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QWidget

import pinn
from pinn import Pinn

try:
    import search
except ImportError:  # the team may have kept the old file name
    import searchFunction as search

app = QApplication.instance() or QApplication(sys.argv)


def makeTextPinn(parent, title, body):
    note = Pinn(parent, "Text")
    note.topBar.text.setText(title)
    note.bodyText.text.setText(body)
    pinn.pinnList.append(note)
    return note


def isFaded(note):
    return note.graphicsEffect() is not None


class SearchTests(unittest.TestCase):
    def setUp(self):
        pinn.pinnList.clear()
        self.parent = QWidget()
        self.groceries = makeTextPinn(self.parent, "Groceries", "buy milk and eggs")
        self.homework = makeTextPinn(self.parent, "Homework", "read chapter 3")

    def tearDown(self):
        pinn.pinnList.clear()

    # TC-1: matching is case-insensitive and checks the body text
    def test_body_match_ignores_case(self):
        search.applySearch("MILK")
        self.assertFalse(isFaded(self.groceries))
        self.assertTrue(isFaded(self.homework))

    # TC-2: matching checks the title
    def test_title_match(self):
        search.applySearch("homework")
        self.assertTrue(isFaded(self.groceries))
        self.assertFalse(isFaded(self.homework))

    # TC-3: a partial word is enough
    def test_partial_word_match(self):
        search.applySearch("groc")
        self.assertFalse(isFaded(self.groceries))
        self.assertTrue(isFaded(self.homework))

    # TC-4: a query that matches nothing fades every Pinn
    def test_no_match_fades_everything(self):
        search.applySearch("zebra")
        self.assertTrue(isFaded(self.groceries))
        self.assertTrue(isFaded(self.homework))

    # TC-5: clearing the search restores every Pinn
    def test_empty_query_restores_everything(self):
        search.applySearch("milk")
        search.applySearch("")
        self.assertFalse(isFaded(self.groceries))
        self.assertFalse(isFaded(self.homework))

    # TC-6: a query of only spaces counts as empty
    def test_whitespace_query_counts_as_empty(self):
        search.applySearch("zebra")
        search.applySearch("   ")
        self.assertFalse(isFaded(self.groceries))
        self.assertFalse(isFaded(self.homework))

    # TC-7: a Pinn with no body text (Image/Audio Pinn) matches on title only and does not crash
    def test_pinn_without_body_matches_title_only(self):
        picture = makeTextPinn(self.parent, "Vacation photo", "")
        picture.bodyText = None  # Image and Audio Pinns have bodyText = None
        search.applySearch("vacation")
        self.assertFalse(isFaded(picture))
        search.applySearch("milk")
        self.assertTrue(isFaded(picture))

    # TC-8: searching again changes the result instead of stacking effects
    def test_changing_query_updates_results(self):
        search.applySearch("milk")
        self.assertTrue(isFaded(self.homework))
        search.applySearch("chapter")
        self.assertFalse(isFaded(self.homework))
        self.assertTrue(isFaded(self.groceries))

    # TC-9: faded Pinns use the configured opacity
    def test_faded_opacity_value(self):
        search.applySearch("zebra")
        self.assertAlmostEqual(self.groceries.graphicsEffect().opacity(), search.FADED_OPACITY)

    # TC-10: special characters are treated as plain text, not patterns
    def test_special_characters(self):
        makeTextPinn(self.parent, "Code", "learn c++ and 100% of regex .*")
        search.applySearch("c++")
        self.assertFalse(isFaded(pinn.pinnList[-1]))
        search.applySearch(".*")
        self.assertFalse(isFaded(pinn.pinnList[-1]))
        self.assertTrue(isFaded(self.groceries))

    # TC-11: searching an empty board does nothing and does not crash
    def test_empty_board(self):
        pinn.pinnList.clear()
        search.applySearch("anything")


if __name__ == "__main__":
    unittest.main(verbosity=2)
