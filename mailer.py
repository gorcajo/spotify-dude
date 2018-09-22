"""Manages the mail sending"""

import smtplib

import confmanager as conf
from dbmanager import DbManager
from entities import Playlist
from entities import User
from logger import Logger


MAIL_SENDER = conf.get("MAIL_SENDER")
MAIL_PASSWORD = conf.get("MAIL_PASSWORD")


class Mailer(object):
    """
        Mailer class for manage mailing
    """

    def __init__(self, logger: Logger, db_manager: DbManager, subject: str):
        self.logger = logger
        self.db = db_manager
        self.subject = subject
        self.email_contents = []


    def add_new_element_as_new_song(self, playlist: Playlist, last_adder: User, track_name: str, track_artists: str, next_adder: User):
        """Adds a new element, consisting in the playlist name just modified,
        the last adder, the track's name and the track's artists"""

        element = f"<h2>{playlist.name}</h2>"
        element += f"<p>El último en añadir una canción fue "
        element += f"<strong>{last_adder.name}</strong>"
        element += f":</p>"
        element += f'<p>   "{track_name}" de {track_artists}</p>'
        element += f"<p>Le toca añadir a... <strong>{next_adder.name}</strong>!</p>"
        self.email_contents += [element]


    def add_new_element_as_deleted_song(self, playlist: Playlist, next_adder: User):
        """Adds a new element, consisting in the playlist name just modified,
        the last adder, the track's name and the track's artists"""

        element = f"<h2>{playlist.name}</h2>"
        element += f"<p>Alguien ha borrado una canción!</p>"
        element += f"<p>Le toca añadir a... <strong>{next_adder.name}</strong>!</p>"
        self.email_contents += [element]


    def send_mail(self):
        """Sends an email"""

        self.logger.debug(f"Getting all mail receivers from DB...")
        receivers = self.db.get_all_users()
        self.logger.debug(f"... gotten {len(receivers)} receivers")

        receivers_line = ""
        mail_addresses = []

        for receiver in receivers:
            receivers_line += receiver.name + f"<{receiver.mail}>, "
            mail_addresses.append(receiver.mail)

        body = ""
        body += f"To: {receivers_line}\r\n"
        body += f"From: Spotify Dude<{MAIL_SENDER}>\r\n"
        body += f"Subject: {self.subject}\r\n"
        body += "MIME-Version: 1.0\r\n"
        body += "Content-type: text/html\r\n"
        body += "\r\n"
        body += f"<html><head></head><body><h1>{self.subject}</h1>\n"

        for element in self.email_contents:
            body += f"{element}\n"
        
        body += "</body></html>"

        self.logger.debug(f"Generated email body:\n{body}")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, mail_addresses, body.encode("utf-8"))
        server.quit()
