"""Calls to RESTful APIs"""

import base64
import json
import requests
from typing import List

import confmanager as conf
from entities import Playlist
from entities import Song
from logger import Logger


class HttpMethod(object):
    """Just like a Java enum"""

    get = 0
    post = 1
    put = 2
    patch = 3
    delete = 4


class SpotifyClient(object):
    """Manages calls to the Spotify API"""

    BASE_URL = "https://api.spotify.com/v1"


    def __init__(self, logger: Logger):
        self.logger = logger

        self.logger.debug("Initializing Spotify API client...")

        self.user_id = conf.get("USER_ID")
        self._access_token = None

        basic_auth = conf.get('CLIENT_ID') + ":" + conf.get('CLIENT_SECRET')
        basic_auth = base64.b64encode(basic_auth.encode("utf-8")).decode("utf-8")

        response = requests.post(
            url="https://accounts.spotify.com/api/token",
            headers={"Authorization": "Basic " + basic_auth},
            data={
                "grant_type": "refresh_token",
                "refresh_token": conf.get("REFRESH_TOKEN")
            }
        )

        if response.status_code == 200:
            self._access_token = response.json()["access_token"]
        else:
            raise RestError(str(response.status_code) + ": " + json.dumps(response.json()))
        
        self.logger.debug("... success, access key gotten: '" + self._access_token[:8] + "..." + self._access_token[-8:] + "'")


    def get_name_from_playlist(self, playlist: Playlist) -> str:
        """Returns the name of the playlist given its ID"""

        self.logger.debug("Getting the name of the playlist with SpotifyID ["  + playlist.spotify_id + "] from Spotify API...")
        response = self._get(SpotifyClient.BASE_URL + "/users/" + self.user_id + "/playlists/" + playlist.spotify_id)
        self.logger.debug("... got '" + response['name'] + "'")

        return response["name"]


    def get_all_songs_from_playlist(self, playlist: Playlist) -> dict:
        """Returns a list of Spotify's track objects corresponding to the playlist ID given"""

        self.logger.debug("Getting all songs in '" + playlist.name + "' from Spotify API...")

        tracks = []

        url = SpotifyClient.BASE_URL + "/users/" + self.user_id + "/playlists/" + playlist.spotify_id + "/tracks"

        while url:
            response = self._get(url)

            if response["next"] != url:
                url = response["next"]
            else:
                url = None

            tracks += response["items"]

        self.logger.debug("... gotten " + str(len(tracks)) + " songs")

        return tracks


    def get_genres_from_song_list(self, songs: List[Song]) -> List[str]:
        """Returns a list of genres associated with the song's artist"""

        self.logger.debug("Getting all genres associated with " + str(len(songs)) + " songs from Spotify API...")

        genres = []

        for song in songs:
            for artist in song.artists:
                response = self._get("{SpotifyClient.BASE_URL}/artists/{artist.spotify_id}")
                genres += response["genres"]

        self.logger.debug("... gotten " + str(len(genres)))

        return genres


    def _get(self, url:str, data: dict = None) -> dict:
        headers = {"Authorization": "Bearer " + self._access_token}
        response = requests.get(url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise RestError(str(response.status_code) + ": " + json.dumps(response.json()))


class RestError(Exception):
    """Exception to be raised when an unexpected status code from a RESTful API is gotten"""
    pass
