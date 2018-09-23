"""Manages the mail sending"""

import base64
import os
import smtplib
import requests
from typing import List

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
        self.new_songs = []
        self.deleted_songs = []


    def add_new_event_as_new_song(self, playlist: Playlist, last_adder: User, song: Song, next_adder: User):
        """Adds a new element"""

        self.new_songs += [{
            "playlist": playlist,
            "last_adder": last_adder,
            "song": song,
            "next_adder": next_adder
        }]


    def add_new_event_as_deleted_song(self, playlist: Playlist, next_adder: User):
        """Adds a new element"""

        self.deleted_songs += [{
            "playlist": playlist,
            "next_adder": next_adder
        }]


    def send_mail(self):
        """Sends an email"""

        self.logger.debug("Getting all mail receivers from DB...")
        receivers = self.db.get_all_users()

        mail_addresses = []

        for receiver in receivers:
            mail_addresses += [receiver.mail]

        body = self._generate_body(receivers)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, mail_addresses, body.encode("utf-8"))
        server.quit()

        self.logger.debug("... email sent")


    def dump_mail_to_file(self, filename):
        """Dumps the email contents to a file, for development purposes"""

        self.logger.debug("Getting all mail receivers from DB...")
        receivers = self.db.get_all_users()

        with open(filename, "w") as file:
            file.write(self._generate_body(receivers))
    

    def _generate_body(self, receivers: List[User]) -> str:
        self.logger.debug("Generating email contents...")

        receivers_line = ""

        for receiver in receivers:
            receivers_line += f"{receiver.name}<{receiver.mail}>, "

        receivers_line = receivers_line[:-2]

        body = ""
        body += f"To: {receivers_line}\r\n"
        body += f"From: Spotify Dude<{MAIL_SENDER}>\r\n"
        body += f"Subject: {self.subject}\r\n"
        body += "MIME-Version: 1.0\r\n"
        body += 'Content-Type: multipart/related; boundary="multipart_related_boundary"\r\n'
        body += "\r\n"

        body += f"--multipart_related_boundary\r\n"
        body += "Content-Type: text/html; charset=UTF-8\r\n"
        body += "Content-Transfer-Encoding: 7bit\r\n"
        body += "\r\n"
        body += f"<html><head></head><body>\r\n<h1>{self.subject}</h1>\r\n"

        attachment_index = 0
        attachments = []

        for element in self.new_songs:
            body += f"<h2>{element['playlist'].name}</h2>\n"
            body += f"<p>El último en añadir una canción fue <strong>{element['last_adder'].name}</strong>:</p>\n"
            body += f'<p>"{element["song"].name}" de {element["song"].get_artists_str()}</p>\n'

            if element["song"].cover_url is not None:
                cid = f"cover{attachment_index}"

                attachments += [{
                    "source": "url",
                    "url": element["song"].cover_url,
                    "cid": cid
                }]

                body += f"<img src='cid:{cid}' alt='portada'/>\n"

                attachment_index += 1

            body += f"<p>Le toca añadir a... <strong>{element['next_adder'].name}</strong>!</p>\n"

        for element in self.deleted_songs:
            body += f"<h2>{element['playlist'].name}</h2>\n"
            body += f"<p>Alguien ha borrado una canción!</p>\n"
            body += f"<p>Le toca añadir a... <strong>{element['next_adder'].name}</strong>!</p>\n"
        
        body = f"{body}</body></html>\r\n"

        for attachment in attachments:
            body += "\r\n"
            body += f"--multipart_related_boundary\r\n"
            body += f'Content-Type: image/jpeg; name="{attachment["cid"]}.jpg"\r\n'
            body += "Content-Transfer-Encoding: base64\r\n"
            body += f"Content-ID: <{attachment['cid']}>\r\n"
            body += f'Content-Disposition: inline; filename="{attachment["cid"]}.jpg"\r\n'
            body += "\r\n"

            if attachment["source"] == "url":
                self.logger.debug(f"Getting image from '{attachment['url']}' to attach it...")
                body += base64.b64encode(requests.get(attachment["url"]).content).decode("utf-8")
            elif attachment["source"] == "tmpfile":
                with open(attachment["path"], "rb") as file:
                    body += base64.b64encode(file.read()).decode("utf-8")
                os.remove(attachment["path"])
            else:
                raise ValueError()
        
        loggable_html = ""

        for line in body.splitlines():
            if line[:4] != "/9j/":
                loggable_html += f"{line}\r\n"
            else:
                loggable_html += "[base64-string]\r\n"

        self.logger.debug(f"... email generated:\n{loggable_html[:-1]}")

        return body
