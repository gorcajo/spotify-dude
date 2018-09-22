from sqlite3 import Row

class User(object):
    """User entity"""

    def __init__(self, row: Row):
        self.id = row["id"]
        self.name = row["name"]
        self.spotify_id = row["spotify_id"]
        self.mail = row["mail"]


    def __str__(self):
        return str((self.id, self.name, self.spotify_id, self.mail))


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
        return str((self.id, self.name, self.spotify_id))


    def __repr__(self):
        return self.__str__()
