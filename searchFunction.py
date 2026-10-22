class Pinn:
  #A single Pinn with a title and with content
  def __init__(self, title, content):
    self.title = title
    self.content = content
    
class PinnBoard:
  #Board holding a collection of pinns and allows searching
  def __init__(self):
    #Initializes an empty list to store all the pinns
    self.pins = []
    
    
#"I want to search for a keyword and get results"
def search(searchQuery, pinnBoard):
  
    #Step 1: Handle empty search string
    if not searchQuery:
      return []
  
    #Step 2: Convert the search query to lowercase
    searchTerm = searchQuery.lower()

    #Step 3: Initialize an empty list of search results
    searchResults = []

    #Step 4: Loop through each pinn on the pinn board 
    for pinn in pinnBoard:

      #Step 5: Convert the Pinn Title and Pinn Content to lowercase
        pinnTitle = pinn.title.lower()
        pinnContent = pinn.content.lower()

      #Step 6: Check if the keyword exists in the title or content
        if searchTerm in pinnTitle or searchTerm in pinnContent:
          #Step 7: Add the matching pinn to the results
          searchResults.append(pinn)

    #Step 8: Return the search results
    return searchResults

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



          
