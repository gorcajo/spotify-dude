"""
    The Spotify Dude app!
"""

import base64
import random
import requests
import traceback

from entities import Playlist
from entities import Song
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
                spotify_songs = self.spotify.get_all_songs_from_playlist(playlist)
                current_name = self.spotify.get_name_from_playlist(playlist)

                if playlist.name != current_name:
                    playlist.name = current_name
                    self.db.update_playlist_name(playlist, current_name)
                    self.logger.debug(f"The name of the playlist has changed to [{current_name}]")
                else:
                    self.logger.debug("No change in playlist name")

                if playlist.songs_last_seen == len(spotify_songs):
                    self.logger.debug("There are no song changes, playlist skipped")
                elif playlist.songs_last_seen < len(spotify_songs):
                    self.logger.debug(f"Somebody added songs (before: {playlist.songs_last_seen}, now: {len(spotify_songs)}), an update will be made")
                    self._update_with_added_song(playlist, spotify_songs[-1], len(spotify_songs))
                    there_were_changes = True
                else:
                    self.logger.debug(f"Somebody deleted songs (before: {playlist.songs_last_seen}, now: {len(spotify_songs)}), an update will be made")
                    self._update_with_deleted_song(playlist, len(spotify_songs))
                    there_were_changes = True

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")

        self.logger.debug("There are no more playlists to check")

        if there_were_changes:
            if not self.debug_mode:
                self.mailer.send_mail()
            else:
                self.mailer.dump_html_to_file("/tmp/mail.html")


    def statistics(self):
        """Sends an email with the statistics of all playlists"""
        stored_playlists = self.db.get_all_playlists()

        all_users = {}

        for user_in_db in self.db.get_all_users():
            all_users[user_in_db.spotify_id] = user_in_db

        for playlist in stored_playlists:
            try:
                songs = []

                for spotify_song in self.spotify.get_all_songs_from_playlist(playlist):
                    adder = all_users[spotify_song["added_by"]["id"]]
                    songs += [Song(spotify_song, adder)]
                
                songs_added_per_user = {}

                for song in songs:
                    if song.added_by.name not in songs_added_per_user:
                        songs_added_per_user[song.added_by.name] = 1
                    else:
                        songs_added_per_user[song.added_by.name] += 1
                
                # TODO:
                self.logger.debug("Generating 'songs per user' graph...")
                graph_base64 = statsplotter.dict_as_bar_graph(songs_added_per_user, "Canciones/persona", "Canciones")
                print(graph_base64)
                self.logger.debug("... done")

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")
    

    def _update_with_added_song(self, playlist: Playlist, last_spotify_song: dict, current_song_count: int):
        self.logger.debug(f"Retrieving the last song added along with its data")

        adder = self.db.find_user_by_spotify_id(last_spotify_song["added_by"]["id"])
        song = Song(last_spotify_song, adder)

        self.logger.debug(f"Last song was [{song}]")

        next_adder = adder

        self.logger.debug(f"Getting all users from DB to do the lottery...")
        all_users = self.db.get_all_users()

        while next_adder.id == adder.id:
            next_adder = random.choice(all_users)

        self.logger.debug(f"Next random adder: [{next_adder.name}]")

        self.mailer.add_new_event_as_new_song(playlist, adder, song, next_adder)

        if not self.debug_mode:
            self.db.update_playlist_songs(playlist, current_song_count)
    

    def _update_with_deleted_song(self, playlist: Playlist, current_song_count: int):
        self.logger.debug(f"Getting all users from DB to do the lottery...")
        all_users = self.db.get_all_users()
        next_adder = random.choice(all_users)
        self.logger.debug(f"Next random adder: [{next_adder.name}]")

        self.mailer.add_new_event_as_deleted_song(playlist, next_adder)

        if not self.debug_mode:
            self.logger.debug(f"Updating playlist [{playlist.name}] in DB...")
            self.db.update_playlist_songs(playlist, current_song_count)
            self.logger.debug(f"... done")
