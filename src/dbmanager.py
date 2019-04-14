"""DB manager"""

import os
import sqlite3
import subprocess
import sys
from typing import List

import confmanager as conf
from entities import Playlist
from entities import User
from logger import Logger


class DbError(Exception):
    """Exception to be raised during a bad query"""
    pass


class DbManager(object):

    def __init__(self, logger: Logger):
        self.logger = logger
        self.db_file = conf.get("DB_FILE")


    def find_user_by_spotify_id(self, spotify_id: int) -> User:
        """Returns the user with the given Spotify ID """

        with sqlite3.connect(self.db_file) as conn:
            conn.set_trace_callback(self._log_query)
            conn.row_factory = sqlite3.Row

            qry = "SELECT * FROM users WHERE spotify_id = ?"
            rows = conn.cursor().execute(qry, [spotify_id]).fetchall()

            self.logger.debug("... gotten " + str(len(rows)) + " rows")

            if not rows:
                return None
            elif len(rows) == 1:
                return User(rows[0])
            else:
                raise DbError("Found more than one user with spotify_id = " + str({spotify_id}))


    def find_playlist_by_spotify_id(self, spotify_id: str) -> Playlist:
        """Returns the playlist with the given Spotify ID"""

        with sqlite3.connect(self.db_file) as conn:
            conn.set_trace_callback(self._log_query)
            conn.row_factory = sqlite3.Row

            qry = "SELECT * FROM playlists WHERE spotify_id = ?"
            rows = conn.cursor().execute(qry, [spotify_id]).fetchall()

            self.logger.debug("... gotten " + str(len(rows)) + " rows")

            if not rows:
                return None
            elif len(rows) == 1:
                return Playlist(rows[0])
            else:
                raise DbError("Found more than one playlist with spotify_id = '" + spotify_id + "'")


    def update_playlist_name(self, playlist: Playlist, new_name: str):
        """Updates the playlist's songs"""

        with sqlite3.connect(self.db_file) as conn:
            conn.set_trace_callback(self._log_query)
            conn.row_factory = sqlite3.Row

            qry = "\n".join([
                "UPDATE",
                "  playlists",
                "SET",
                "  name = ?",
                "WHERE",
                "  id = ?",
            ])

            conn.cursor().execute(qry, [new_name, playlist.id])
            
            self.logger.debug("... done")


    def update_playlist_songs(self, playlist: Playlist, new_song_count: int, new_hash: str):
        """Updates the playlist's songs"""
        
        with sqlite3.connect(self.db_file) as conn:
            conn.set_trace_callback(self._log_query)
            conn.row_factory = sqlite3.Row

            qry = "\n".join([
                "UPDATE",
                "  playlists",
                "SET",
                "  songs_last_seen = ?,",
                "  songs_hash = ?",
                "WHERE",
                "  id = ?",
            ])

            conn.cursor().execute(qry, [new_song_count, new_hash, playlist.id])
            conn.commit()
            
            self.logger.debug("... done")
    

    def update_playlist_songs_hash(self, playlist: Playlist, new_hash: str):
        """Updates the playlist's songs hash"""

        with sqlite3.connect(self.db_file) as conn:
            conn.set_trace_callback(self._log_query)
            conn.row_factory = sqlite3.Row

            qry = "\n".join([
                "UPDATE",
                "  playlists",
                "SET",
                "  songs_hash = ?",
                "WHERE",
                "  id = ?",
            ])

            conn.cursor().execute(qry, [new_hash, playlist.id])
            
            self.logger.debug("... done")


    def get_all_users(self) -> List[User]:
        """Returns a list with all users"""

        users = []

        with sqlite3.connect(self.db_file) as conn:
            conn.set_trace_callback(self._log_query)
            conn.row_factory = sqlite3.Row

            qry = "SELECT * FROM users"
            rows = conn.cursor().execute(qry).fetchall()

            self.logger.debug("... gotten " + str(len(rows)) + " rows")

            for row in rows:
                users.append(User(row))

        return users


    def get_all_playlists(self) -> List[Playlist]:
        """Returns a list with all playlists"""

        playlists = []

        with sqlite3.connect(self.db_file) as conn:
            conn.set_trace_callback(self._log_query)
            conn.row_factory = sqlite3.Row

            qry = "SELECT * FROM playlists"
            rows = conn.cursor().execute(qry).fetchall()
            
            self.logger.debug("... gotten " + str(len(rows)) + " rows")

            for row in rows:
                playlists.append(Playlist(row))

        return playlists
    

    def _log_query(self, query: str):
        log_lines = []

        for line in query.splitlines():
            log_lines += [line.strip()]

        self.logger.debug(' '.join(log_lines))


def install_database():
    db_file = conf.get("DB_FILE")
    db_directory = "/".join(db_file.split("/")[:-1])

    if not os.path.isdir(db_directory):
        print("Application not correctly or yet installed. See 'README.md'")
        sys.exit(1)

    if os.path.isfile(db_file):
        print("Database already installed.")
        sys.exit(1)

    qry_create_table_users = "\n".join([
        "CREATE TABLE IF NOT EXISTS users(",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    name TEXT,",
        "    spotify_id TEXT,",
        "    mail TEXT",
        ")",
    ])

    qry_create_table_playlists = "\n".join([
        "CREATE TABLE IF NOT EXISTS playlists(",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    name TEXT,",
        "    spotify_id TEXT,",
        "    songs_last_seen INTEGER,",
        "    songs_hash TEXT",
        ")",
    ])

    subprocess.run(["sqlite3", db_file, qry_create_table_users])
    subprocess.run(["sqlite3", db_file, qry_create_table_playlists])

    print("Database successfully installed.")


def enter_sqlite_shell():
    db_file = conf.get("DB_FILE")

    if not os.path.isfile(db_file):
        print("App not installed yet. See 'README.md'.")
        sys.exit(1)
        
    subprocess.run(["sqlite3", "-header", "-column", db_file])
