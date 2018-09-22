from datetime import datetime
from sqlite3 import Row


class User(object):
    """User entity"""

    def __init__(self, row: Row):
        self.id = row["id"]
        self.name = row["name"]
        self.spotify_id = row["spotify_id"]
        self.mail = row["mail"]


    def __str__(self):
        return f"ID={self.id}, Name='{self.name}', SpotifyID='{self.spotify_id}', Mail='{self.mail}'"


    def __repr__(self):
        return self.__str__()


class Playlist(object):
    """Playlist entity"""

    def __init__(self, row: Row):
        self.id = row["id"]
        self.name = row["name"]
        self.spotify_id = row["spotify_id"]
        self.songs_last_seen = row["songs_last_seen"]


    def __str__(self):
        return f"ID={self.id}, Name='{self.name}', SpotifyID='{self.spotify_id}'"


    def __repr__(self):
        return self.__str__()


class Song(object):

    def __init__(self, spotify_song: dict, adder_by: User):
        self.spotify_id = spotify_song["track"]["id"]
        self.name = spotify_song["track"]["name"]

        self.artists = ""

        for artist in spotify_song["track"]["artists"]:
            self.artists += artist["name"] + ", "

        self.artists = self.artists[:-2]

        self.adder_by = adder_by
        self.added_at = datetime.strptime(spotify_song["added_at"], "%Y-%m-%dT%H:%M:%SZ")
        
        biggest_cover_width = 0
        self.cover_url = None

        for cover in spotify_song["track"]["album"]["images"]:
            if cover["width"] > biggest_cover_width:
                self.cover_url = cover["url"]
                biggest_cover_width = cover["width"]


    def __str__(self):
        return str(f"'{self.name}' by '{self.artists}' added by '{self.adder_by.name}'")


    def __repr__(self):
        return self.__str__()
