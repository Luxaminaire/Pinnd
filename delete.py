## Jack Dillon
import sqlite3

def delete_note(note_id):
    connection = sqlite3.connect("corkboard.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM StickyNote WHERE noteID = ?",
        (note_id,)
    )

    connection.commit()
    connection.close()
	
def delete_note(note_id):
    deleted = delete_note_db(note_id)