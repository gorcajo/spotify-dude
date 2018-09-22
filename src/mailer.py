"""Manages the mail sending"""

import smtplib

import confmanager as conf
from dbmanager import DbManager
from entities import Playlist
from entities import User
from entities import Song
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


    def add_new_event_as_new_song(self, playlist: Playlist, last_adder: User, song: Song, next_adder: User, cover_b64: str = None):
        """Adds a new element, consisting in the playlist name just modified,
        the last adder, the track's name and the track's artists"""

        element = f"<h2>{playlist.name}</h2>\n"
        element += f"<p>El último en añadir una canción fue <strong>{last_adder.name}</strong>:</p>\n"
        element += f'<p>"{song.name}" de {song.artists}</p>\n'

        if cover_b64 is not None:
            element += f"<img src='data:image/png;base64, {cover_b64}' alt='portada'/>\n"

        element += f"<p>Le toca añadir a... <strong>{next_adder.name}</strong>!</p>\n"
        self.email_contents += [element]


    def add_new_event_as_deleted_song(self, playlist: Playlist, next_adder: User):
        """Adds a new element, consisting in the playlist name just modified,
        the last adder, the track's name and the track's artists"""

        element = f"<h2>{playlist.name}</h2>\n"
        element += f"<p>Alguien ha borrado una canción!</p>\n"
        element += f"<p>Le toca añadir a... <strong>{next_adder.name}</strong>!</p>\n"
        self.email_contents += [element]


    def send_mail(self):
        """Sends an email"""

        self.logger.debug("Getting all mail receivers from DB...")
        receivers = self.db.get_all_users()
        self.logger.debug(f"... gotten {len(receivers)} receivers")

        receivers_line = ""
        mail_addresses = []

        for receiver in receivers:
            receivers_line += f"{receiver.name}<{receiver.mail}>, "
            mail_addresses += [receiver.mail]

        body = ""
        body += f"To: {receivers_line}\r\n"
        body += f"From: Spotify Dude<{MAIL_SENDER}>\r\n"
        body += f"Subject: {self.subject}\r\n"
        body += "MIME-Version: 1.0\r\n"
        body += "Content-type: text/html\r\n"
        body += "\r\n"

        body += self._generate_html()

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, mail_addresses, body.encode("utf-8"))
        server.quit()

        self.logger.debug("... email sent")


    def dump_html_to_file(self, filename):
        """Dumps the HTML to a file, for development purposes"""

        with open(filename, "w") as file:
            file.write(self._generate_html())
    

    def _generate_html(self) -> str:
        self.logger.debug("Generating email HTML...")

        html = f"<html>\n<head></head>\n<body>\n<h1>{self.subject}</h1>\n"

        for element in self.email_contents:
            html += f"{element}\n"
        
        html = f"{html[:-1]}</body>\n</html>\n"

        loggable_html = ""

        for line in html.splitlines():
            if line[:4] != "<img":
                loggable_html += f"{line}\n"
            else:
                loggable_html += "<img/>\n"

        self.logger.debug(f"... done:\n{loggable_html[:-1]}")

        return html
