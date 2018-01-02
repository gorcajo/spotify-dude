"""Manages the calls to Spotify API"""

import base64
import requests

import confmanager as conf

CLIENT_ID = conf.get("CLIENT_ID")
CLIENT_SECRET = conf.get("CLIENT_SECRET")
REFRESH_TOKEN = conf.get("REFRESH_TOKEN")

def get_all_tracks_from_playlist(token, playlist_id):
    """Returns a list of Spotify's track objects corresponding to the playlist ID given"""

    url = "https://api.spotify.com/v1/users/reth5/playlists/" + playlist_id + "/tracks"
    headers = {"Authorization": "Bearer " + token}
    data = {}
    response = requests.get(url, headers=headers, data=data)

    if response.status_code != 200:
        raise RestError(str(response.status_code) + ": " + str(response.json()["error"]["message"]))
    else:
        return response.json()["items"]

def get_playlist_ids_from_name_list(token, names):
    """Returns a list of IDs corresponding to the playlist name list given"""

    playlist_ids = []

    page = 0
    while True:
        playlists = get_all_playlists(token, page)

        if len(playlists) <= 0:
            break

        for playlist in playlists:
            name = playlist["name"]

            for list_name in names:
                if name == list_name:
                    playlist_ids.append(playlist["id"])
                    break

        page += 1

    return playlist_ids

def get_all_playlists(token, page):
    """Returns a list of Spotify's playlist objects belonging to me"""

    offset = 50 * page
    url = "https://api.spotify.com/v1/users/reth5/playlists?limit=50&offset=" + str(offset)
    headers = {"Authorization": "Bearer " + token}
    data = {}
    response = requests.get(url, headers=headers, data=data)

    if response.status_code != 200:
        raise RestError(str(response.status_code) + ": " + str(response.json()["error"]["message"]))
    else:
        return response.json()["items"]

def get_access_token():
    """Returns the access token"""

    url = "https://accounts.spotify.com/api/token"

    headers = {"Authorization": "Basic " + encode_base64(CLIENT_ID + ":" + CLIENT_SECRET)}

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise RestError(str(response.status_code) + ": " + str(response.json()))
    else:
        return response.json()["access_token"]

def encode_base64(string):
    """Returns a string containing the base64 encoded string"""

    string = string.encode("utf-8")
    return base64.b64encode(string).decode("utf-8")

def decode_base64(string):
    """Returns the decoded version from a base64 encoded string"""

    string = string.encode("utf-8")
    return base64.b64decode(string).decode("utf-8")

class RestError(Exception):
    """Exception to be raised when an unexpected status code from a RESTful API is gotten"""
    pass
