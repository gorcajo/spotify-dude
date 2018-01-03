"""DB manager"""

import sqlite3

import confmanager as conf

DB_FILE = conf.get("DB_FILE")

class User(object):
    """
        User entity
    """

    def __init__(self, row):
        self.id = row["id"]
        self.name = row["name"]
        self.spotify_id = row["spotify_id"]
        self.mail = row["mail"]

    def __str__(self):
        return str((self.id, self.name, self.spotify_id, self.mail))

class Playlist(object):
    """
        Playlist entity
    """

    def __init__(self, row):
        self.id = row["id"]
        self.name = row["name"]
        self.spotify_id = row["spotify_id"]
        self.songs_last_seen = row["songs_last_seen"]

    def __str__(self):
        return str((self.id, self.name, self.spotify_id))

def find_user_by_spotify_id(spotify_id):
    """Returns the user with the given Spotify ID """

    conn = sqlite3.connect(DB_FILE)

    with conn:
        conn.row_factory = sqlite3.Row

        rows = conn.cursor().execute(
            "SELECT * FROM users WHERE spotify_id = '" + spotify_id + "'"
        ).fetchall()

        if not rows:
            return None
        elif len(rows) == 1:
            return User(rows[0])
        else:
            raise DbError("Found more than one user with spotify_id = '" + spotify_id + "'")

def find_playlist_by_spotify_id(spotify_id):
    """Returns the playlist with the given Spotify ID"""

    conn = sqlite3.connect(DB_FILE)

    with conn:
        conn.row_factory = sqlite3.Row

        rows = conn.cursor().execute(
            "SELECT * FROM playlists WHERE spotify_id = '" + spotify_id + "'"
        ).fetchall()

        if not rows:
            return None
        elif len(rows) == 1:
            return Playlist(rows[0])
        else:
            raise DbError("Found more than one playlist with spotify_id = '" + spotify_id + "'")

def update_playlist_name(playlist, new_name):
    """Updates the playlist's songs"""

    conn = sqlite3.connect(DB_FILE)

    with conn:
        conn.row_factory = sqlite3.Row

        qry = ""
        qry += "UPDATE\n"
        qry += "  playlists\n"
        qry += "SET\n"
        qry += "  name = '" + str(new_name) + "'\n"
        qry += "WHERE id = " + str(playlist.id)

        conn.cursor().execute(qry)

def update_playlist_songs(playlist, new_song_count):
    """Updates the playlist's songs"""

    conn = sqlite3.connect(DB_FILE)

    with conn:
        conn.row_factory = sqlite3.Row

        qry = ""
        qry += "UPDATE\n"
        qry += "  playlists\n"
        qry += "SET\n"
        qry += "  songs_last_seen = " + str(new_song_count) + "\n"
        qry += "WHERE id = " + str(playlist.id)

        conn.cursor().execute(qry)

def get_all_users():
    """Returns a list with all users"""

    users = []

    conn = sqlite3.connect(DB_FILE)

    with conn:
        conn.row_factory = sqlite3.Row

        rows = conn.cursor().execute("SELECT * FROM users").fetchall()

        for row in rows:
            users.append(User(row))

    return users

def get_all_playlists():
    """Returns a list with all playlists"""

    playlists = []

    conn = sqlite3.connect(DB_FILE)

    with conn:
        conn.row_factory = sqlite3.Row

        rows = conn.cursor().execute("SELECT * FROM playlists").fetchall()

        for row in rows:
            playlists.append(Playlist(row))

    return playlists

class DbError(Exception):
    """Exception to be raised during a bad query"""
    pass
