"""DB manager"""

import sqlite3
from typing import List

import confmanager as conf
from entities import Playlist
from entities import User


class DbError(Exception):
    """Exception to be raised during a bad query"""
    pass


class DbManager(object):

    def __init__(self):
        self.db_file = conf.get("DB_FILE")


    def find_user_by_spotify_id(self, spotify_id: int) -> User:
        """Returns the user with the given Spotify ID """

        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.cursor().execute(f"SELECT * FROM users WHERE spotify_id = '{spotify_id}'").fetchall()

            if not rows:
                return None
            elif len(rows) == 1:
                return User(rows[0])
            else:
                raise DbError(f"Found more than one user with spotify_id = '{spotify_id}'")


    def find_playlist_by_spotify_id(self, spotify_id: str) -> Playlist:
        """Returns the playlist with the given Spotify ID"""

        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.cursor().execute(f"SELECT * FROM playlists WHERE spotify_id = '{spotify_id}'").fetchall()

            if not rows:
                return None
            elif len(rows) == 1:
                return Playlist(rows[0])
            else:
                raise DbError("Found more than one playlist with spotify_id = '" + spotify_id + "'")


    def update_playlist_name(self, playlist: Playlist, new_name: str):
        """Updates the playlist's songs"""

        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row

            qry = "\n".join([
                f"UPDATE",
                f"  playlists",
                f"SET",
                f"  name = '{new_name}'",
                f"WHERE",
                f"  id = {playlist.id}",
            ])

            conn.cursor().execute(qry)


    def update_playlist_songs(self, playlist: Playlist, new_song_count: int):
        """Updates the playlist's songs"""

        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row

            qry = "\n".join([
                f"UPDATE",
                f"  playlists",
                f"SET",
                f"  songs_last_seen = {new_song_count}",
                f"WHERE",
                f"  id = {playlist.id}",
            ])

            conn.cursor().execute(qry)


    def get_all_users(self) -> List[User]:
        """Returns a list with all users"""

        users = []

        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.cursor().execute("SELECT * FROM users").fetchall()

            for row in rows:
                users.append(User(row))

        return users


    def get_all_playlists(self) -> List[Playlist]:
        """Returns a list with all playlists"""

        playlists = []

        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.cursor().execute("SELECT * FROM playlists").fetchall()

            for row in rows:
                playlists.append(Playlist(row))

        return playlists
