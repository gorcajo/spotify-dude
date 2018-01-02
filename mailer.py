"""Manages the mail sending"""

import smtplib

import confmanager as conf
import dbmanager as db

MAIL_SENDER = conf.get("MAIL_SENDER")
MAIL_PASSWORD = conf.get("MAIL_PASSWORD")

class Mailer(object):
    """
        Mailer class for manage mailing
    """

    def __init__(self, subject):
        self.subject = subject
        self.email_content = ""

    def add_new_element(self, playlist, last_adder, track_name, track_artists, next_adder):
        """Adds a new element, consisting in the playlist name just modified,
        the last adder, the track's name and the track's artists"""

        self.email_content += "<h2>" + playlist.name + "</h2>"
        self.email_content += "<p>El último en añadir una canción fue "
        self.email_content += "<strong>" + last_adder.name + "</strong>"
        self.email_content += ":</p>"
        self.email_content += "<p>   \"" + track_name + "\" de " + track_artists + "</p>"
        self.email_content += "<p>Le toca a... <strong>" + next_adder.name + "</strong>!</p>"

    def send_mail(self):
        """Sends an email"""

        receivers = db.get_all_users()
        receivers_line = ""
        mail_addresses = []

        for receiver in receivers:
            receivers_line += receiver.name + "<" + receiver.mail + ">, "
            mail_addresses.append(receiver.mail)

        body = ""
        body += "To: " + receivers_line + "\r\n"
        body += "From: Spotify Dude<" + MAIL_SENDER + ">" +  "\r\n"
        body += "Subject: " + self.subject +  "\r\n"
        body += "MIME-Version: 1.0" +  "\r\n"
        body += "Content-type: text/html" +  "\r\n"
        body += "\r\n"
        body += "<html><head></head><body><h1>" + self.subject + "</h1>"
        body += self.email_content + "</body></html>"

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(MAIL_SENDER, MAIL_PASSWORD)
        server.sendmail(MAIL_SENDER, mail_addresses, body.encode("utf-8"))
        server.quit()
