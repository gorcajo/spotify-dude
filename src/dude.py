"""
    The Spotify Dude app!
"""

import datetime
import hashlib
import random
import requests
import traceback
from typing import List

from entities import Playlist
from entities import Song
from entities import User
from logger import Logger
from spotifyclient import SpotifyClient
from dbmanager import DbManager
from mailer import Mailer
import statsplotter


class Dude(object):
    
    def __init__(self, logger: Logger, db_manager: DbManager, spotify_client: SpotifyClient, mailer: Mailer, debug_mode: bool = True):
        self.logger = logger
        self.db = db_manager
        self.spotify = spotify_client
        self.mailer = mailer
        self.debug_mode = debug_mode


    def roulette(self):
        """Sends an email with the next user to add a song in every playlist inside the DB"""

        there_were_changes = False

        playlists = self.db.get_all_playlists()

        for playlist in playlists:
            try:
                current_name = self.spotify.get_name_from_playlist(playlist)

                if playlist.name != current_name:
                    playlist.name = current_name
                    self.db.update_playlist_name(playlist, current_name)
                    self.logger.debug(f"The name of the playlist has been changed to [{current_name}]")
                else:
                    self.logger.debug("No change in playlist name")

                spotify_songs = self.spotify.get_all_songs_from_playlist(playlist)

                if playlist.songs_last_seen == len(spotify_songs):
                    spotify_songs_hash = hashlib.md5(str(spotify_songs).encode()).hexdigest()

                    if spotify_songs_hash == playlist.songs_hash:
                        self.logger.debug("There are no song changes, playlist skipped")
                    else:
                        self.logger.debug(f"Somebody changed songs (before: {playlist.songs_hash}, now: {spotify_songs_hash}), an update will be made")
                        self._update_with_changed_songs(playlist, spotify_songs, spotify_songs_hash)
                        there_were_changes = True

                elif playlist.songs_last_seen < len(spotify_songs):
                    self.logger.debug(f"Somebody added songs (before: {playlist.songs_last_seen}, now: {len(spotify_songs)}), an update will be made")
                    self._update_with_added_song(playlist, spotify_songs)
                    there_were_changes = True

                else:
                    self.logger.debug(f"Somebody deleted songs (before: {playlist.songs_last_seen}, now: {len(spotify_songs)}), an update will be made")
                    spotify_songs_hash = hashlib.md5(str(spotify_songs).encode()).hexdigest()
                    self._update_with_deleted_songs(playlist, len(spotify_songs), spotify_songs_hash)
                    there_were_changes = True

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")

        self.logger.debug("There are no more playlists to check")

        if there_were_changes:
            if not self.debug_mode:
                self.mailer.send_mail("Spotify update!")
            else:
                self.mailer.generate_body("Spotify update!", [])


    def statistics(self):
        """Sends an email with the statistics of all playlists"""
        playlists = self.db.get_all_playlists()

        all_users = {}

        for user_in_db in self.db.get_all_users():
            all_users[user_in_db.spotify_id] = user_in_db

        for playlist in playlists:
            try:
                # Getting all songs:

                songs = []

                for spotify_song in self.spotify.get_all_songs_from_playlist(playlist):
                    adder = all_users[spotify_song["added_by"]["id"]]
                    songs += [Song(spotify_song, adder)]

                # Songs per user stats:

                songs_added_per_user = {}

                for song in songs:
                    if song.added_by.name not in songs_added_per_user:
                        songs_added_per_user[song.added_by.name] = 1
                    else:
                        songs_added_per_user[song.added_by.name] += 1

                self.logger.debug("Generating 'songs per user' graph...")
                # graph_path = statsplotter.dict_as_bar_graph(songs_added_per_user, "Canciones/persona", "Canciones")
                # self.mailer.add_new_stat(graph_path)
                self.logger.debug("... done")

                # Songs per genre stats:
                
                songs_per_genre = {}
                genres = []

                if not self.debug_mode:
                    genres = self.spotify.get_genres_from_song_list(songs)
                else:
                    genres = ["rock"]*16 + ["metal"]*8 + ["blues"]*4 + ["jazz"]*2 + ["classic"]

                for genre in genres:
                    if genre not in songs_per_genre:
                        songs_per_genre[genre] = 1
                    else:
                        songs_per_genre[genre] += 1

                self.logger.debug("Generating 'songs per genre' graph...")
                # graph_path = statsplotter.dict_as_bar_graph(songs_per_genre, "Canciones/genero", "Canciones")
                # self.mailer.add_new_stat(graph_path)
                self.logger.debug("... done")

                # Sending mail:

                if not self.debug_mode:
                    self.mailer.send_mail("Spotify statistics!")
                else:
                    self.mailer.generate_body("Spotify statistics!", [])

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")
    

    def _update_with_added_song(self, playlist: Playlist, spotify_songs: List[dict]):
        self.logger.debug(f"Retrieving the last song added along with its data")

        all_users = self.db.get_all_users()
        songs = self._convert_spotify_songs(spotify_songs, all_users)
        most_recent_song = self._obtain_most_recent_song(songs)
        self.logger.debug(f"Most recently added song song was [{most_recent_song}]")

        next_adder = most_recent_song.added_by

        while next_adder.id == most_recent_song.added_by.id:
            next_adder = random.choice(all_users)

        self.logger.debug(f"Next random adder: [{next_adder.name}]")

        self.mailer.add_new_event_as_new_song(playlist, most_recent_song.added_by, most_recent_song, next_adder)

        if not self.debug_mode:
            new_songs_hash = hashlib.md5(str(spotify_songs).encode()).hexdigest()
            self.db.update_playlist_songs(playlist, len(songs), new_songs_hash)
    

    def _update_with_deleted_songs(self, playlist: Playlist, current_song_count: int, new_songs_hash: str):
        self.logger.debug(f"Getting all users from DB to do the lottery...")
        all_users = self.db.get_all_users()
        next_adder = random.choice(all_users)
        self.logger.debug(f"Next random adder: [{next_adder.name}]")

        self.mailer.add_new_event_as_deleted_song(playlist, next_adder)

        if not self.debug_mode:
            self.db.update_playlist_songs(playlist, current_song_count, new_songs_hash)
    

    def _update_with_changed_songs(self, playlist: Playlist, spotify_songs: List[dict], new_hash: str):
        all_users = self.db.get_all_users()
        songs = self._convert_spotify_songs(spotify_songs, all_users)
        most_recent_song = self._obtain_most_recent_song(songs)
        self.logger.debug(f"After changes, most recent song song is [{most_recent_song}]")
        
        next_adder = random.choice(all_users)
        self.logger.debug(f"Next random adder: [{next_adder.name}]")

        self.mailer.add_new_event_as_changed_songs(playlist, most_recent_song, next_adder)

        if not self.debug_mode:
            self.db.update_playlist_songs_hash(playlist, new_hash)


    def _convert_spotify_songs(self, spotify_songs: List[dict], users: List[User]) -> List[Song]:
        users_dict = {}

        for user in users:
            users_dict[user.spotify_id] = user

        songs = []

        for spotify_song in spotify_songs:
            added_by_spotify_id = spotify_song["added_by"]["id"]
            added_by = users_dict[added_by_spotify_id]
            songs += [Song(spotify_song, added_by)]
        
        return songs


    def _obtain_most_recent_song(self, songs: List[Song]):
        most_recent_song: Song = None
        most_recent_added_at = datetime.datetime.now() - datetime.timedelta(days=1000*365)

        for song in songs:
            if song.added_at > most_recent_added_at:
                most_recent_song = song
                most_recent_added_at = song.added_at
        
        return most_recent_song
