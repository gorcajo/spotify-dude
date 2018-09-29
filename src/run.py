#!/usr/bin/env python3.6

import argparse
import traceback

from dude import Dude
from logger import Logger
import dbmanager
from dbmanager import DbManager
from mailer import Mailer
from spotifyclient import SpotifyClient


def main():
    """Main entrance to the app"""

    parser = argparse.ArgumentParser()

    group_operation = parser.add_mutually_exclusive_group(required=True)
    group_operation.add_argument("--roulette",   action="store_true", help="sends an email with the next user to add a song in every playlist")
    group_operation.add_argument("--statistics", action="store_true", help="sends a statistics mail")
    group_operation.add_argument("--dbinstall",  action="store_true", help="installs the database")
    group_operation.add_argument("--dbshell",    action="store_true", help="enters the SQLite shell")

    parser.add_argument("--debug", action="store_true", help="enables debug mode")

    group_verbosity = parser.add_mutually_exclusive_group(required=False)
    group_verbosity.add_argument("--verbose", action="store_true", help="enables verbose output to stdout")
    group_verbosity.add_argument("--silent",  action="store_true", help="silences completely any output to stdout")

    args = parser.parse_args()

    logger = Logger(verbose_mode=args.verbose, silent_mode=args.silent)

    if args.dbinstall:
        dbmanager.install_database()
    elif args.dbshell:
        dbmanager.enter_sqlite_shell()
    else:
        try:
            logger.info("Started")
            
            db = DbManager(logger=logger)
            spotify = SpotifyClient(logger=logger)
            mailer = Mailer(logger=logger, db_manager=db)
            dude = Dude(logger=logger, db_manager=db, spotify_client=spotify, mailer=mailer, debug_mode=args.debug)

            if args.roulette:
                dude.roulette()
            elif args.statistics:
                dude.statistics()

            logger.info("Finished")
        
        except:
            logger.error(f"Exception happened:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
