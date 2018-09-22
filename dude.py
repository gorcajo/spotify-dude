"""
    The Spotify Dude app!
"""

import random
import traceback

from logger import Logger
from spotifyclient import SpotifyClient
from dbmanager import DbManager
from mailer import Mailer


class Dude(object):
    
    def __init__(self, logger: Logger, db: DbManager, mailer: Mailer):
        self.logger = logger
        self.db = db
        self.mailer = mailer


    def roulette(self, debug_mode=True):
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
                self.logger.debug(f"Getting all tracks in [{stored_playlist.name}] from Spotify API...")
                tracks = spotify.get_all_tracks_from_playlist(stored_playlist.spotify_id)
                self.logger.debug(f"... gotten {len(tracks)} tracks")

                self.logger.debug("Checking playlist name...")
                current_name = spotify.get_playlist_name_from_id(stored_playlist.spotify_id)

                if stored_playlist.name != current_name:
                    stored_playlist.name = current_name
                    self.db.update_playlist_name(stored_playlist, current_name)
                    self.logger.debug(f"... the name of the playlist has changed to [{current_name}]")
                else:
                    self.logger.debug("... no name change")

                if stored_playlist.songs_last_seen == len(tracks):
                    self.logger.debug("There are no song changes, playlist skipped")
                    continue
                else:
                    self.logger.debug("There are song changes, an update will be made")
                    there_were_changes = True

                last_adder = ""
                last_track_name = ""
                last_track_artists = ""

                for playlist_track in tracks:
                    adder = self.db.find_user_by_spotify_id(playlist_track["added_by"]["id"])
                    track = playlist_track["track"]

                    artists = ""
                    for track_artist in track["artists"]:
                        artists += track_artist["name"] + ", "
                    artists = artists[:-2]

                    last_adder = adder
                    last_track_name = track["name"]
                    last_track_artists = artists

                self.logger.debug(f"Last song [{last_track_name}] by [{last_track_artists}] added by [{last_adder.name}]")

                next_adder = last_adder

                all_users = self.db.get_all_users()

                while next_adder.id == last_adder.id:
                    next_adder = random.choice(all_users)

                self.logger.debug(f"Next random adder: '{next_adder.name}'")

                self.mailer.add_new_element(
                    stored_playlist,
                    last_adder,
                    last_track_name,
                    last_track_artists,
                    next_adder)

                if not debug_mode:
                    self.logger.debug(f"Updating playlist [{stored_playlist.name}] in DB...")
                    self.db.update_playlist_songs(stored_playlist, len(tracks))
                    self.logger.debug(f"... done")

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")

        self.logger.debug("There are no more playlists to check")

        if not debug_mode and there_were_changes:
            self.logger.debug("Preparing and sending the mail...")
            self.mailer.send_mail()
            self.logger.debug("... email sent")
