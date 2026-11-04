import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name('corkboard.db')

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db

def initialize():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            view_x REAL NOT NULL DEFAULT 0, view_y REAL NOT NULL DEFAULT 0,
            zoom REAL NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY, board_id INTEGER NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
            title TEXT NOT NULL DEFAULT '', body TEXT NOT NULL DEFAULT '',
            image TEXT NOT NULL DEFAULT '', audio TEXT NOT NULL DEFAULT '',
            x REAL NOT NULL, y REAL NOT NULL, width REAL NOT NULL DEFAULT 260,
            height REAL NOT NULL DEFAULT 240, color TEXT NOT NULL DEFAULT '#ffe66d',
            z INTEGER NOT NULL DEFAULT 1
        );
        ''')
        if not db.execute('SELECT id FROM boards LIMIT 1').fetchone():
            db.execute("INSERT INTO boards(name) VALUES ('My Corkboard')")

def boards():
    with connect() as db:
        return [dict(row) for row in db.execute('SELECT * FROM boards ORDER BY id')]

def notes(board_id):
    with connect() as db:
        return [dict(row) for row in db.execute('SELECT * FROM notes WHERE board_id=? ORDER BY z,id', (board_id,))]

def board_exists(board_id):
    with connect() as db:
        return db.execute('SELECT 1 FROM boards WHERE id=?', (board_id,)).fetchone() is not None

def add_board(name):
    with connect() as db:
        cur = db.execute('INSERT INTO boards(name) VALUES (?)', (name,))
        return cur.lastrowid

def update_board(board_id, changes):
    if not changes: return False
    with connect() as db:
        cur = db.execute('UPDATE boards SET '+', '.join(f'{k}=?' for k in changes)+' WHERE id=?', (*changes.values(), board_id))
        return cur.rowcount > 0

def add_note(board_id, note):
    with connect() as db:
        z = db.execute('SELECT COALESCE(MAX(z),0)+1 FROM notes WHERE board_id=?', (board_id,)).fetchone()[0]
        cur = db.execute('INSERT INTO notes(board_id,title,body,image,audio,x,y,width,height,color,z) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                         (board_id, note['title'], note['body'], note['image'], note['audio'], note['x'], note['y'], note['width'], note['height'], note['color'], z))
        return dict(db.execute('SELECT * FROM notes WHERE id=?', (cur.lastrowid,)).fetchone())

def get_note(note_id):
    with connect() as db:
        row = db.execute('SELECT * FROM notes WHERE id=?', (note_id,)).fetchone()
        return dict(row) if row else None

def update_note(note_id, changes):
    if not changes: return get_note(note_id)
    with connect() as db:
        db.execute('UPDATE notes SET '+', '.join(f'{k}=?' for k in changes)+' WHERE id=?', (*changes.values(), note_id))
    return get_note(note_id)

def delete_note(note_id):
    with connect() as db:
        return db.execute('DELETE FROM notes WHERE id=?', (note_id,)).rowcount > 0

def layer_note(note_id, front):
    with connect() as db:
        note = db.execute('SELECT board_id FROM notes WHERE id=?', (note_id,)).fetchone()
        if not note: return None
        bound = db.execute(('SELECT COALESCE(MAX(z),0)+1' if front else 'SELECT COALESCE(MIN(z),0)-1')+' FROM notes WHERE board_id=?', (note['board_id'],)).fetchone()[0]
        db.execute('UPDATE notes SET z=? WHERE id=?', (bound,note_id))
    return get_note(note_id)
