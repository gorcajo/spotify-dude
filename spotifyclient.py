"""Calls to RESTful APIs"""

import base64
import requests

import confmanager as conf


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


    def __init__(self):
        self.user_id = conf.get("USER_ID")
        self._access_token = None

        basic_auth = f"{conf.get('CLIENT_ID')}:{conf.get('CLIENT_SECRET')}"
        basic_auth = base64.b64encode(basic_auth.encode("utf-8")).decode("utf-8")

        response = self._post(
            url="https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {basic_auth}"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": conf.get("REFRESH_TOKEN")
            }
        )

        self._access_token = response["access_token"]


    def get_access_token(self):
        """Returns a reduced version of the access token, suitable for logging"""
        reduced_token = f"{self._access_token[:8]}...{self._access_token[-8:]}"
        return reduced_token


    def get_playlist_name_from_id(self, playlist_id: str):
        """Returns the name of the playlist given its ID"""

        response = self._get(f"{SpotifyClient.BASE_URL}/users/{self.user_id}/playlists/{playlist_id}")
        return response["name"]


    def get_all_tracks_from_playlist(self, playlist_id: str):
        """Returns a list of Spotify's track objects corresponding to the playlist ID given"""

        tracks = []

        url = f"{SpotifyClient.BASE_URL}/users/{self.user_id}/playlists/{playlist_id}/tracks"

        while url:
            response = self._get(url)

            if response["next"] != url:
                url = response["next"]
            else:
                url = None

            tracks += response["items"]

        return tracks


    def get_all_playlists(self, page: int):
        """Returns a list of Spotify's playlist objects belonging to me"""

        response = self._get(f"{SpotifyClient.BASE_URL}/users/{self.user_id}/playlists?limit=50&offset={50 * page}")

        return response["items"]


    def _post(self, url:str, headers: dict = None, data: dict = None) -> dict:
        response = requests.post(url, headers=headers, data=data)

        if response.status_code != 200:
            raise RestError(f"{response.status_code}: {response.json()}")
        else:
            return response.json()


    def _get(self, url:str, data: dict = None) -> dict:
        headers = {"Authorization": f"Bearer {self._access_token}"}
        response = requests.get(url, headers=headers, data=data)

        if response.status_code != 200:
            raise RestError(f"{response.status_code}: {response.json()}")
        else:
            return response.json()


class RestError(Exception):
    """Exception to be raised when an unexpected status code from a RESTful API is gotten"""
    pass
