import unittest
# Assuming your class files are named board.py and pin.py
from board import Board  
from pin import textPinn

class TestBoardSearch(unittest.TestCase):

    def setUp(self):
        """Set up a mock board with test pins before each test."""
        # Setup mock pins matching expected attributes (title, content)
        pin1 = textPinn("Pin 1", "Meeting Notes", "Discuss project milestones")
        pin1.title = pin1.headerText
        pin1.content = pin1.bodyText

        pin2 = textPinn("Pin 2", "Shopping List", "Buy apples and milk")
        pin2.title = pin2.headerText
        pin2.content = pin2.bodyText

        # Initialize board with pins
        self.board = Board()
        self.board.pins = [pin1, pin2]

    def test_search_valid_keyword(self):
        """Test searching for a term in the title or content."""
        results = self.board.search("Meeting")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Meeting Notes")

    def test_search_case_insensitive(self):
        """Test that search ignores uppercase/lowercase differences."""
        results = self.board.search("apples")
        self.assertEqual(len(results), 1)

    def test_search_empty_query(self):
        """Test returning empty list on empty or None input."""
        self.assertEqual(self.board.search(""), [])
        self.assertEqual(self.board.search(None), [])

    def test_search_no_match(self):
        """Test returning empty list when no matches exist."""
        self.assertEqual(self.board.search("nonexistent"), [])

if __name__ == "__main__":
    unittest.main()
