"""
    The Spotify Dude app!
"""

import datetime
import hashlib
import random
import requests
import traceback

from entities import Playlist
from entities import Song
from entities import User
from entities import Plottable
from logger import Logger
from spotifyclient import SpotifyClient
from dbmanager import DbManager
from mailer import Mailer
import statsplotter


class Dude(object):
    
    def __init__(self, logger, db_manager, spotify_client, mailer, debug_mode = True):
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
                    self.logger.debug("The name of the playlist has been changed to '" + current_name + "'")
                else:
                    self.logger.debug("No change in playlist name")

                spotify_songs = self.spotify.get_all_songs_from_playlist(playlist)

                if playlist.songs_last_seen == len(spotify_songs):
                    spotify_songs_hash = hashlib.md5(str(spotify_songs).encode()).hexdigest()

                    if spotify_songs_hash == playlist.songs_hash:
                        self.logger.debug("There are no song changes, playlist skipped")
                    else:
                        self.logger.debug("Somebody changed songs (before: " + playlist.songs_hash + ", now: " + spotify_songs_hash + "), an update will be made")
                        self._update_with_changed_songs(playlist, spotify_songs, spotify_songs_hash)
                        there_were_changes = True

                elif playlist.songs_last_seen < len(spotify_songs):
                    self.logger.debug("Somebody added songs (before: " + str(playlist.songs_last_seen) + ", now: " + str(len(spotify_songs)) + "), an update will be made")
                    self._update_with_added_song(playlist, spotify_songs)
                    there_were_changes = True

                else:
                    self.logger.debug("Somebody deleted songs (before: " + str(playlist.songs_last_seen) + ", now: " + len(spotify_songs) + "), an update will be made")
                    spotify_songs_hash = hashlib.md5(str(spotify_songs).encode()).hexdigest()
                    self._update_with_deleted_songs(playlist, len(spotify_songs), spotify_songs_hash)
                    there_were_changes = True

            except:
                self.logger.warn("Exception happened:\n" + traceback.format_exc())

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

                self.logger.debug("Generating 'songs per user' graph...")

                songs_added_per_user = {}

                for song in songs:
                    if song.added_by.name not in songs_added_per_user:
                        songs_added_per_user[song.added_by.name] = 1
                    else:
                        songs_added_per_user[song.added_by.name] += 1

                plottable = Plottable("Canciones/persona", "Canciones", songs_added_per_user)
                graph_path = statsplotter.plot_as_bar_graph(plottable)
                self.mailer.add_new_graph(graph_path)
                self.logger.debug("... done")

                # Activity stats:

                self.logger.debug("Generating 'songs per user' graph...")

                plottable = Plottable("Actividad de las últimas semanas", "Canciones puestas")

                self._obtain_oldest_song(songs).added_at

                activity = {}

                for year in range(2018, datetime.datetime.now().year + 1):
                    for week in range(1, 52 + 1):
                        year_now = datetime.datetime.now().year
                        week_now = datetime.datetime.now().isocalendar()[1]

                        if year == year_now and week == week_now + 1:
                            break

                        for song in songs:
                            if week == song.added_at.isocalendar()[1] and year == song.added_at.year:
                                yearweek = year + "-" + week

                                if yearweek not in activity:
                                    activity[yearweek] = 1
                                else:
                                    activity[yearweek] += 1
                            else:
                                if yearweek not in activity:
                                    activity[yearweek] = 0

                for value in activity.values():
                    plottable.add_value("", value)
                
                plottable.x_axis = plottable.x_axis[-4:]
                plottable.y_axis = plottable.y_axis[-4:]

                graph_path = statsplotter.plot_as_line_graph(plottable)
                self.mailer.add_new_graph(graph_path)
                self.logger.debug("... done")

                # Sending mail:

                if not self.debug_mode:
                    self.mailer.send_mail("Spotify statistics!")
                else:
                    self.mailer.generate_body("Spotify statistics!", [])

            except:
                self.logger.warn("Exception happened:\n" + traceback.format_exc())
    

    def _update_with_added_song(self, playlist, spotify_songs):
        self.logger.debug("Retrieving the last song added along with its data")

        all_users = self.db.get_all_users()
        songs = self._convert_spotify_songs(spotify_songs, all_users)
        most_recent_song = self._obtain_most_recent_song(songs)
        self.logger.debug("Most recently added song song was '" + str(most_recent_song) + "'")

        next_adder = most_recent_song.added_by

        while next_adder.id == most_recent_song.added_by.id:
            next_adder = random.choice(all_users)

        self.logger.debug("Next random adder: '" + next_adder.name + "'")

        self.mailer.add_new_event_as_new_song(playlist, most_recent_song.added_by, most_recent_song, next_adder)

        if not self.debug_mode:
            new_songs_hash = hashlib.md5(str(spotify_songs).encode()).hexdigest()
            self.db.update_playlist_songs(playlist, len(songs), new_songs_hash)
    

    def _update_with_deleted_songs(self, playlist, current_song_count, new_songs_hash):
        self.logger.debug("Getting all users from DB to do the lottery...")
        all_users = self.db.get_all_users()
        next_adder = random.choice(all_users)
        self.logger.debug("Next random adder: '" + next_adder.name + "'")

        self.mailer.add_new_event_as_deleted_song(playlist, next_adder)

        if not self.debug_mode:
            self.db.update_playlist_songs(playlist, current_song_count, new_songs_hash)
    

    def _update_with_changed_songs(self, playlist, spotify_songs, new_hash):
        all_users = self.db.get_all_users()
        songs = self._convert_spotify_songs(spotify_songs, all_users)
        most_recent_song = self._obtain_most_recent_song(songs)
        self.logger.debug("After changes, most recent song is '" + most_recent_song.name + "'")

        next_adder = random.choice(all_users)
        self.logger.debug("Next random adder: '" + next_adder.name + "'")

        self.mailer.add_new_event_as_changed_songs(playlist, most_recent_song, next_adder)

        if not self.debug_mode:
            self.db.update_playlist_songs_hash(playlist, new_hash)


    def _convert_spotify_songs(self, spotify_songs, users):
        users_dict = {}

        for user in users:
            users_dict[user.spotify_id] = user

        songs = []

        for spotify_song in spotify_songs:
            added_by_spotify_id = spotify_song["added_by"]["id"]
            added_by = users_dict[added_by_spotify_id]
            songs += [Song(spotify_song, added_by)]
        
        return songs


    def _obtain_most_recent_song(self, songs):
        most_recent_song = None
        most_recent_added_at = datetime.datetime.now() - datetime.timedelta(days=1000*365)

        for song in songs:
            if song.added_at > most_recent_added_at:
                most_recent_song = song
                most_recent_added_at = song.added_at
        
        return most_recent_song


    def _obtain_oldest_song(self, songs):
        most_recent_song = None
        most_recent_added_at = datetime.datetime.now() + datetime.timedelta(days=1000*365)

        for song in songs:
            if song.added_at < most_recent_added_at:
                most_recent_song = song
                most_recent_added_at = song.added_at
        
        return most_recent_song