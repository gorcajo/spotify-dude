"""
    The Spotify Dude app!
"""

import random
import traceback

from logger import Logger
from apiclient import ApiClient
from dbmanager import DbManager
from mailer import Mailer


class Dude(object):
    
    def __init__(self, logger: Logger, db: DbManager):
        self.logger = logger
        self.db = db


    def roulette(self, must_send_mail=False):
        """Sends an email with the next user to add a song in every playlist inside the DB"""

        mailer = Mailer(subject="Spotify update!")
        there_were_changes = False

        self.logger.debug("Initializing Spotify API client...")
        api = ApiClient()
        self.logger.debug(f"... success, access key gotten: [{api.get_access_token()}]")

        self.logger.debug("Getting all the playlists from DB...")
        playlists = self.db.get_all_playlists()
        self.logger.debug(f"... found {len(playlists)} playlists")

        for playlist in playlists:
            try:
                self.logger.debug(f"Getting all tracks in [{playlist.name}] from Spotify API...")
                tracks = api.get_all_tracks_from_playlist(playlist.spotify_id)
                self.logger.debug(f"... gotten {len(tracks)} tracks")

                self.logger.debug("Checking the playlist name...")
                current_name = api.get_playlist_name_from_id(playlist.spotify_id)

                if playlist.name != current_name:
                    playlist.name = current_name
                    self.db.update_playlist_name(playlist, current_name)
                    self.logger.debug(f"... the name of the playlist has changed to [{current_name}]")
                else:
                    self.logger.debug("... no name change")

                if playlist.songs_last_seen == len(tracks):
                    self.logger.debug("There are no song changes, playlist skipped")
                    continue
                else:
                    self.logger.debug("There are song changes, an update will be made...")
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

                mailer.add_new_element(
                    playlist,
                    last_adder,
                    last_track_name,
                    last_track_artists,
                    next_adder)

                self.db.update_playlist_songs(playlist, len(tracks))

            except:
                self.logger.warn(f"Exception happened:\n{traceback.format_exc()}")

        self.logger.debug("There are no more playlists to check")

        if must_send_mail and there_were_changes:
            self.logger.debug("Preparing and sending the mail...")
            mailer.send_mail()
            self.logger.debug("... email sent")
