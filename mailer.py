"""Manages the mail sending"""

import smtplib

import confmanager as conf
from dbmanager import DbManager
from entities import Playlist
from entities import User


MAIL_SENDER = conf.get("MAIL_SENDER")
MAIL_PASSWORD = conf.get("MAIL_PASSWORD")


class Mailer(object):
    """
        Mailer class for manage mailing
    """

    def __init__(self, subject: str):
        self.subject = subject
        self.email_content = ""


    def add_new_element(self, playlist: Playlist, last_adder: User, track_name: str, track_artists: str, next_adder: User):
        """Adds a new element, consisting in the playlist name just modified,
        the last adder, the track's name and the track's artists"""

        self.email_content += f"<h2>{playlist.name}</h2>"
        self.email_content += f"<p>El último en añadir una canción fue "
        self.email_content += f"<strong>{last_adder.name}</strong>"
        self.email_content += f":</p>"
        self.email_content += f'<p>   "{track_name}" de {track_artists}</p>'
        self.email_content += f"<p>Le toca a... <strong>{next_adder.name}</strong>!</p>"


    def send_mail(self):
        """Sends an email"""

        db = DbManager()
        receivers = db.get_all_users()
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
        body += f"<html><head></head><body><h1>{self.subject}</h1>"
        body += f"{self.email_content}</body></html>"

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, mail_addresses, body.encode("utf-8"))
        server.quit()
