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


class Artist(object):

    def __init__(self, spotify_artist: dict):
        self.name = spotify_artist["name"]
        self.spotify_id = spotify_artist["id"]


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.__str__()


class Song(object):

    def __init__(self, spotify_song: dict, added_by: User):
        self.spotify_id = spotify_song["track"]["id"]
        self.name = spotify_song["track"]["name"]
        self.album_spotify_id = spotify_song["track"]["album"]["id"]

        self.artists = []

        for spotify_artist in spotify_song["track"]["artists"]:
            self.artists += [Artist(spotify_artist)]

        self.added_at = datetime.strptime(spotify_song["added_at"], "%Y-%m-%dT%H:%M:%SZ")
        
        self.cover_url = None

        if len(spotify_song["track"]["album"]["images"]) > 0:
            biggest_cover_width = 0
            
            for cover in spotify_song["track"]["album"]["images"]:
                if cover["width"] > biggest_cover_width:
                    self.cover_url = cover["url"]
                    biggest_cover_width = cover["width"]
                    
        self.added_by = added_by


    def __str__(self):
        return f"'{self.name}' by '{self.get_artists_str()}' added by '{self.added_by.name}'"


    def __repr__(self):
        return self.__str__()
    

    def get_artists_str(self):
        if len(self.artists) > 1:
            artists_names = [artist.name for artist in self.artists[:-1]]

            return ", ".join(artists_names) + " y " + self.artists[-1].name
        else:
            return self.artists[0].name
