import sqlite3

def get_games():
    conn = sqlite3.connect('scrabble.db')
    c = conn.cursor()
    c.execute('SELECT * FROM GAMES')
    result = c.fetchall()
    return result
