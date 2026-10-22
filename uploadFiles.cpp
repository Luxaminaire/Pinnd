// Commands
int getBoardID();
void saveBoard(boardID);
void setAutosave(int seconds);
void  deleteAccount(int userID);

// This should be a list of all settings
int userID = 937467824958093;
bool isSafetyPin = false;
int autosaveSeconds = 30;

// Psuedo-code for user settings
// Toggle security pin
if (isSafetyPin) isSafetyPin = false;
else isSafetyPin = true;

// Save board
saveBoard(getBoardID());

// How often to autosave
int userInput;
std::cin >> userInput;
setAutosave(userInput);

// Delete user
char isDeleted;
std::cout << "Are you sure?\nThis action can not be undone. (y/n): ";
std::cin >> isDeleted;
if (isDeleted == 'y') deleteAccount(userID);

