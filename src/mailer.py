"""Manages the mail sending"""

import base64
import imghdr
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

    def __init__(self, logger: Logger, db_manager: DbManager):
        self.logger = logger
        self.db = db_manager
        self.new_songs = []
        self.deleted_songs = []
        self.stats = []


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


    def add_new_stat(self, imagepath: str):
        """Adds a new element"""

        self.stats += [imagepath]


    def send_mail(self, subject: str):
        """Sends an email"""

        self.logger.debug("Getting all mail receivers from DB...")
        receivers = self.db.get_all_users()

        mail_addresses = [receiver.mail for receiver in receivers]
        body = self.generate_body(subject, receivers)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, mail_addresses, body.encode("utf-8"))
        server.quit()

        self.logger.debug("... email sent")
    

    def generate_body(self, subject: str, receivers: List[User]) -> str:
        self.logger.debug("Generating email contents...")

        receivers_elements = [f"{receiver.name}<{receiver.mail}>" for receiver in receivers]
        receivers_line = ", ".join(receivers_elements)

        body = ""
        body += f"To: {receivers_line}\r\n"
        body += f"From: Spotify Dude<{MAIL_SENDER}>\r\n"
        body += f"Subject: {subject}\r\n"
        body += "MIME-Version: 1.0\r\n"
        body += 'Content-Type: multipart/related; boundary="multipart_related_boundary"\r\n'
        body += "\r\n"

        body += f"--multipart_related_boundary\r\n"
        body += "Content-Type: text/html; charset=UTF-8\r\n"
        body += "Content-Transfer-Encoding: 7bit\r\n"
        body += "\r\n"
        body += f"<html><head></head><body>\r\n<h1>{subject}</h1>\r\n"

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

                body += f"<img src='cid:{cid}' alt='loading cover...'/>\n"

                attachment_index += 1

            body += f"<p>Le toca añadir a... <strong>{element['next_adder'].name}</strong>!</p>\n"

        for element in self.deleted_songs:
            body += f"<h2>{element['playlist'].name}</h2>\n"
            body += f"<p>Alguien ha borrado canciones!</p>\n"
            body += f"<p>Le toca añadir a... <strong>{element['next_adder'].name}</strong>!</p>\n"
        
        for imagepath in self.stats:
            cid = f"stats{attachment_index}"

            attachments += [{
                "source": "tmpfile",
                "path": imagepath,
                "cid": cid
            }]

            attachment_index += 1

            body += f"<img src='cid:{cid}' alt='loading graph...'/>\n"

        
        body = f"{body}</body></html>\r\n"

        for attachment in attachments:
            base64_string = ""

            if attachment["source"] == "url":
                self.logger.debug(f"Getting image from '{attachment['url']}' to attach it...")
                base64_string = base64.b64encode(requests.get(attachment["url"]).content).decode("utf-8")
            elif attachment["source"] == "tmpfile":
                self.logger.debug(f"Getting image from '{attachment['path']}' to attach it...")
                with open(attachment["path"], "rb") as file:
                    base64_string = base64.b64encode(file.read()).decode("utf-8")
                self.logger.debug(f"Removing '{attachment['path']}'...")
                os.remove(attachment["path"])
            else:
                self.logger.warn(f"Attachment source {attachment['path']} unknown")
                continue

            body += "\r\n"
            body += f"--multipart_related_boundary\r\n"

            if _guess_file_format_from_base64(base64_string) == "jpeg":
                body += f'Content-Type: image/jpeg; name="{attachment["cid"]}.jpg"\r\n'
            elif _guess_file_format_from_base64(base64_string) == "png":
                body += f'Content-Type: image/png; name="{attachment["cid"]}.png"\r\n'
            else:
                if attachment["source"] == "url":
                    self.logger.warn(f"Attachment format for '{attachment['url']}' unknown")
                elif attachment["source"] == "tmpfile":
                    self.logger.warn(f"Attachment format for '{attachment['path']}' unknown")
                continue

            body += "Content-Transfer-Encoding: base64\r\n"
            body += f"Content-ID: <{attachment['cid']}>\r\n"

            if base64_string[:4] == "/9j/":
                body += f'Content-Disposition: inline; filename="{attachment["cid"]}.jpg"\r\n'
            elif base64_string[:4] == "iVBO":
                body += f'Content-Disposition: inline; filename="{attachment["cid"]}.png"\r\n'

            body += "\r\n"
            body += base64_string
            body += "\r\n"
        
        loggable_html = ""

        for line in body.splitlines():
            if len(line) < 512:
                loggable_html += f"{line}\r\n"
            else:
                loggable_html += "[line too long to be logged]\r\n"

        self.logger.debug(f"... email generated:\n{loggable_html[:-1]}")

        return body


def _guess_file_format_from_base64(base64_string: str) -> str:
    sample = base64_string.strip()[:44]
    sample_bytes = base64.b64decode(sample)

    for test_function in imghdr.tests:
        image_format = test_function(sample_bytes, None)

        if image_format:
            return image_format
