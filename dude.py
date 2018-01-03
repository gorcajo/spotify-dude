"""
    The Spotify Dude app!
"""

import sys
import random
import traceback

import logger
from apiclient import ApiClient
import dbmanager as db
from mailer import Mailer

ARGUMENTS = {
    "roulette": "--roulette",
    "roulette-test": "--roulette-test"
}

def main():
    """Main entrance to the app"""

    if len(sys.argv) == 2:
        if sys.argv[1] not in ARGUMENTS.values():
            print_usage()
        else:
            logger.info("Dude started")

            try:
                if sys.argv[1] == ARGUMENTS["roulette"]:
                    roulette(must_send_mail=True)
                elif sys.argv[1] == ARGUMENTS["roulette-test"]:
                    roulette(must_send_mail=False)
            except:
                logger.error("Exception happened:\n" + traceback.format_exc())

            logger.info("Finished, dude")
    else:
        print_usage()

def roulette(must_send_mail=False):
    """Sends an email with the next user to add a song in every playlist inside the DB"""

    mailer = Mailer(subject="Spotify update!")
    there_were_changes = False

    logger.debug("Initializing Spotify API client...")
    api = ApiClient()
    logger.debug("... success, access key gotten: [" + api.get_access_token() + "]")

    logger.debug("Getting all the playlists from DB...")
    playlists = db.get_all_playlists()
    logger.debug("... found " + str(len(playlists)) + " playlists")

    for playlist in playlists:
        try:
            logger.debug("Getting all tracks in [" + playlist.name + "] from Spotify API...")
            tracks = api.get_all_tracks_from_playlist(playlist.spotify_id)
            logger.debug("... gotten " + str(len(tracks)) + " tracks")

            logger.debug("Checking the playlist name...")
            current_name = api.get_playlist_name_from_id(playlist.spotify_id)

            if playlist.name != current_name:
                playlist.name = current_name
                db.update_playlist_name(playlist, current_name)
                logger.debug("... the name of the playlist has changed to [" + current_name + "]")
            else:
                logger.debug("... no name change")

            if playlist.songs_last_seen == len(tracks):
                logger.debug("There are no song changes, playlist skipped")
                continue
            else:
                logger.debug("There are changes, an update will be made...")
                there_were_changes = True

            last_adder = ""
            last_track_name = ""
            last_track_artists = ""

            for playlist_track in tracks:
                adder = db.find_user_by_spotify_id(playlist_track["added_by"]["id"])
                track = playlist_track["track"]

                artists = ""
                for track_artist in track["artists"]:
                    artists += track_artist["name"] + ", "
                artists = artists[:-2]

                last_adder = adder
                last_track_name = track["name"]
                last_track_artists = artists

            log_msg = ""
            log_msg += "Last song [" + last_track_name + "] "
            log_msg += "by [" + last_track_artists + "] "
            log_msg += "added by [" + last_adder.name + "]"
            logger.debug(log_msg)

            next_adder = last_adder

            all_users = db.get_all_users()

            while next_adder.id == last_adder.id:
                next_adder = random.choice(all_users)

            logger.debug("Next random adder: '" + next_adder.name + "'")

            mailer.add_new_element(
                playlist,
                last_adder,
                last_track_name,
                last_track_artists,
                next_adder)

            db.update_playlist_songs(playlist, len(tracks))

        except:
            logger.warn("Exception happened:\n" + traceback.format_exc())

    logger.debug("There are no more playlists to check")

    if must_send_mail and there_were_changes:
        logger.debug("Preparing and sending the mail...")
        mailer.send_mail()
        logger.debug("... email sent")

def print_usage():
    """Prints the app usage"""

    script_name = sys.argv[0]

    usage = "\n"
    usage += "USAGE\n"
    usage += "\n"
    usage += "  python " + script_name + " <argument>\n"
    usage += "\n"
    usage += "ARGUMENTS\n"
    usage += "\n"
    usage += "  " + ARGUMENTS["roulette"] + "\n"
    usage += "      Rolls the roulette\n"
    usage += "\n"
    usage += "  " + ARGUMENTS["roulette-test"] + "\n"
    usage += "      Rolls the roulette without sending the email\n"
    usage += "\n"
    usage += "EXAMPLES\n"
    usage += "\n"

    for argument in list(ARGUMENTS.values()):
        usage += "  python " + script_name + " " + argument + "\n"

    print(usage)

main()
