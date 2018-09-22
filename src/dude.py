"""
    The Spotify Dude app!
"""

import random
import traceback

from entities import Playlist
from logger import Logger
from spotifyclient import SpotifyClient
from dbmanager import DbManager
from mailer import Mailer


class Dude(object):
    
    def __init__(self, logger: Logger, db_manager: DbManager, spotify_client: SpotifyClient, mailer: Mailer, debug_mode=True):
        self.logger = logger
        self.db = db_manager
        self.spotify = spotify_client
        self.mailer = mailer
        self.debug_mode = debug_mode


    def roulette(self):
        """Sends an email with the next user to add a song in every playlist inside the DB"""

        there_were_changes = False

        stored_playlists = self.db.get_all_playlists()

        for stored_playlist in stored_playlists:
            try:
                songs = self.spotify.get_all_songs_from_playlist(stored_playlist)

                current_name = self.spotify.get_playlist_name_from_id(stored_playlist)

                if stored_playlist.name != current_name:
                    stored_playlist.name = current_name
                    self.db.update_playlist_name(stored_playlist, current_name)
                    self.logger.debug(f"The name of the playlist has changed to [{current_name}]")
                else:
                    self.logger.debug("No change in playlist name")

                if stored_playlist.songs_last_seen == len(songs):
                    self.logger.debug("There are no song changes, playlist skipped")
                elif stored_playlist.songs_last_seen < len(songs):
                    self.logger.debug(f"Somebody added songs (before: {stored_playlist.songs_last_seen}, now: {len(songs)}), an update will be made")
                    self._update_with_added_song(stored_playlist, songs[-1], len(songs))
                    there_were_changes = True
                else:
                    self.logger.debug(f"Somebody deleted songs (before: {stored_playlist.songs_last_seen}, now: {len(songs)}), an update will be made")
                    self._update_with_deleted_song(stored_playlist, len(songs))
                    there_were_changes = True

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")

        self.logger.debug("There are no more playlists to check")

        if not self.debug_mode and there_were_changes:
            self.mailer.send_mail()


    def statistics(self):
        """Sends an email with the statistics of all playlists"""
        pass
    

    def _update_with_added_song(self, stored_playlist: Playlist, last_spotify_song: dict, current_song_count: int):
        self.logger.debug(f"Retrieving the last song added along with its data")

        adder = self.db.find_user_by_spotify_id(last_spotify_song["added_by"]["id"])

        artists = ""
        for artist in last_spotify_song["track"]["artists"]:
            artists += artist["name"] + ", "
        artists = artists[:-2]

        song_name = last_spotify_song["track"]["name"]

        self.logger.debug(f"Last song [{song_name}] by [{artists}] added by [{adder.name}]")

        next_adder = adder

        self.logger.debug(f"Getting all users from DB to do the lottery...")
        all_users = self.db.get_all_users()

        while next_adder.id == adder.id:
            next_adder = random.choice(all_users)

        self.logger.debug(f"Next random adder: [{next_adder.name}]")

        self.mailer.add_new_element_as_new_song(
            stored_playlist,
            adder,
            song_name,
            artists,
            next_adder)

        if not self.debug_mode:
            self.db.update_playlist_songs(stored_playlist, current_song_count)
    

    def _update_with_deleted_song(self, stored_playlist: Playlist, current_song_count: int):
        self.logger.debug(f"Getting all users from DB to do the lottery...")
        all_users = self.db.get_all_users()
        next_adder = random.choice(all_users)
        self.logger.debug(f"Next random adder: [{next_adder.name}]")

        self.mailer.add_new_element_as_deleted_song(stored_playlist, next_adder)

        if not self.debug_mode:
            self.logger.debug(f"Updating playlist [{stored_playlist.name}] in DB...")
            self.db.update_playlist_songs(stored_playlist, current_song_count)
            self.logger.debug(f"... done")
