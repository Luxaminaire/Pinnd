# Defines a class Pinn to represent an individual Pinn
class Pinn:
  """A single Pinn with a title and content."""
  
  # The constructor method that initializes a new Pinn object, expecting strings for title & content
  def __init__(self, title: str, content: str):
    self.title = title
    self.content = content

  # Defines how the Pinn object is represented as a string
  def __repr__(self):
    return f"Pinn(title='{self.title}')"

# Defines a class named PinnBoard to manage a collection of Pinns
class PinnBoard:
  """Board holding a collection of pinns and allows searching"""

  # The constructor method that initializes a new PinnBoard object
  def __init__(self):
    # Creates an empty list attribute to store the Pinn objects
    self.pinns = []

  # Define a method to add a new Pinn to the board, hinting it expects a Pinn object
  def add_pinn(self, pinn: "Pinn"):
    """Adds a Pinn to the board."""
    # Append the passed Pinn object to the board's internal list of pins
    self.pins.append(pinn)
    
# Define a method to search the board, expecting a string query and returning a list
    def search(self, search_query: str) -> list:
        """Searches the board for a keyword in titles or content."""
        
        # Check if the search query is empty or None
        if not search_query:
            # If the search query is empty, immediately return an empty list
            return []
            
        # Convert the search query to lowercase to ensure the search is case-insensitive
        search_term = search_query.lower()
        
        # Return a dynamically generated list (using a list comprehension) containing the search results
        return [
            # Grab the specific 'pinn' object from the iteration...
            pinn for pinn in self.pins
            # ...but only include it if the lowercase search term exists in the lowercase title OR lowercase content
            if search_term in pinn.title.lower() or search_term in pinn.content.lower()
        ]

"""
FOUND THIS ONLINE: BASICALLY MY CODE SUCKS AND SOMEONE WAS ABLE TO DO THIS IN 7 LINES
class PinnBoard:
    # ... (init and add_pinn stay the same) ...

    def search(self, searchQuery):
        if not searchQuery:
            return []
            
        searchTerm = searchQuery.lower()
        
        # Returns a new list containing only the pins where the condition is true
        return [pinn for pinn in self.pinns 
                if searchTerm in pinn.title.lower() or searchTerm in pinn.content.lower()]

"""



          
