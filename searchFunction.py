# Defines a method to search the board, expecting a string query and returning a list
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
