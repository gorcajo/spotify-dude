#!/usr/bin/env python3.6

import argparse
import traceback

from dude import Dude
from logger import Logger
from dbmanager import DbManager
from mailer import Mailer


def main():
    """Main entrance to the app"""

    parser = argparse.ArgumentParser()

    group_operation = parser.add_mutually_exclusive_group(required=True)
    group_operation.add_argument("-r", "--roulette",   action="store_true", help="runs a roulette if there was a song recently added")

    parser.add_argument("-d", "--debug", action="store_true", help="enables debug mode")

    group_verbosity = parser.add_mutually_exclusive_group(required=False)
    group_verbosity.add_argument("-v", "--verbose", action="store_true", help="enables verbose output to stdout")
    group_verbosity.add_argument("-s", "--silent", action="store_true", help="silences completely any output to stdout")

    args = parser.parse_args()

    logger = Logger(verbose_mode=args.verbose, silent_mode=args.silent)
    logger.info("Started")

    try:
        db = DbManager(logger=logger)
        mailer = Mailer(logger=logger, db_manager=db, subject="Spotify update!")
        dude = Dude(logger=logger, db_manager=db, mailer=mailer, debug_mode=args.debug)

        if args.roulette:
            dude.roulette()
    
    except:
        logger.error(f"Exception happened:\n{traceback.format_exc()}")

    logger.info("Finished")


if __name__ == "__main__":
    main()
