
import json
import uuid

with open('userSettings.json', 'r') as file:
    settings = json.load(file)

user_profile = {
    "userID": settings["userID"]
}

# Commands

def getBoardID():
    return input("Enter board ID: ")

def saveBoard(boardID):
    print("Saving board " + str(boardID) + "...")

def setAutosave(seconds):
    settings["autosaveSeconds"] = int(seconds)

def deleteAccount(userID):
    print("Deleting account " + str(userID) + "...")

# Generate unique user ID
def generateUserID():
    return uuid.uuid4().int >> 64

# Pseudo-code for user settings

# Toggle security pin
if settings["isSafetyPin"]:
    settings["isSafetyPin"] = False
    print("SafetyPin setting is off.\n")
else:
    settings["isSafetyPin"] = True
    print("SafetyPin setting is on.\n")

# Save board
boardID = getBoardID()
saveBoard(boardID)
print("Pinboard " + str(boardID) + " has been saved.\n")

# How often to autosave
userInput = input("How often to autosave?: ")
setAutosave(userInput)
print("Autosaves every " + userInput + " seconds.\n")

# Delete user
isDeleted = input(
    "Are you sure?\nThis action cannot be undone. (y/n): "
)

if isDeleted.lower() == 'y':
    deleteAccount(user_profile["userID"])
    print("Goodbye!\n")

# Save updated settings to JSON
with open('userSettings.json', 'w') as file:
    json.dump(settings, file, indent=4)
