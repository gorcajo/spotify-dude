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
    
    def __init__(self, logger: Logger, db_manager: DbManager, mailer: Mailer, debug_mode=True):
        self.logger = logger
        self.db = db_manager
        self.mailer = mailer
        self.debug_mode = debug_mode


    def roulette(self):
        """Sends an email with the next user to add a song in every playlist inside the DB"""

        there_were_changes = False

        self.logger.debug("Initializing Spotify API client...")
        spotify = SpotifyClient()
        self.logger.debug(f"... success, access key gotten: [{spotify.get_access_token()}]")

        self.logger.debug("Getting all the playlists from DB...")
        stored_playlists = self.db.get_all_playlists()
        self.logger.debug(f"... found {len(stored_playlists)} playlists")

        for stored_playlist in stored_playlists:
            try:
                self.logger.debug(f"Getting all songs in [{stored_playlist.name}] from Spotify API...")
                songs = spotify.get_all_songs_from_playlist(stored_playlist.spotify_id)
                self.logger.debug(f"... gotten {len(songs)} songs")

                self.logger.debug("Checking playlist name...")
                current_name = spotify.get_playlist_name_from_id(stored_playlist.spotify_id)

                if stored_playlist.name != current_name:
                    stored_playlist.name = current_name
                    self.db.update_playlist_name(stored_playlist, current_name)
                    self.logger.debug(f"... the name of the playlist has changed to [{current_name}]")
                else:
                    self.logger.debug("... no name change")

                if stored_playlist.songs_last_seen == len(songs):
                    self.logger.debug("There are no song changes, playlist skipped")
                elif stored_playlist.songs_last_seen < len(songs):
                    self.logger.debug(f"Somebody added songs (stored: {stored_playlist.songs_last_seen}, now: {len(songs)}), an update will be made")
                    self._update_with_added_song(stored_playlist, songs[-1], len(songs))
                    there_were_changes = True
                else:
                    self.logger.debug(f"Somebody deleted songs (stored: {stored_playlist.songs_last_seen}, now: {len(songs)}), an update will be made")
                    self._update_with_deleted_song(stored_playlist, len(songs))
                    there_were_changes = True

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")

        self.logger.debug("There are no more playlists to check")

        if not self.debug_mode and there_were_changes:
            self.logger.debug("Preparing and sending the mail...")
            self.mailer.send_mail()
            self.logger.debug("... email sent")
    

    def _update_with_added_song(self, stored_playlist: Playlist, last_spotify_song: dict, current_song_count: int):
        self.logger.debug(f"Getting the last adder user from DB...")
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

        self.logger.debug(f"Next random adder: '{next_adder.name}'")

        self.mailer.add_new_element_as_new_song(
            stored_playlist,
            adder,
            song_name,
            artists,
            next_adder)

        if not self.debug_mode:
            self.logger.debug(f"Updating playlist [{stored_playlist.name}] in DB...")
            self.db.update_playlist_songs(stored_playlist, current_song_count)
            self.logger.debug(f"... done")
    

    def _update_with_deleted_song(self, stored_playlist: Playlist, current_song_count: int):
        self.logger.debug(f"Getting all users from DB to do the lottery...")
        all_users = self.db.get_all_users()
        next_adder = random.choice(all_users)
        self.logger.debug(f"Next random adder: '{next_adder.name}'")

        self.mailer.add_new_element_as_deleted_song(stored_playlist, next_adder)

        if not self.debug_mode:
            self.logger.debug(f"Updating playlist [{stored_playlist.name}] in DB...")
            self.db.update_playlist_songs(stored_playlist, current_song_count)
            self.logger.debug(f"... done")
