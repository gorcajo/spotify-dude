"""Manages the mail sending"""

CONF_FILE = "/opt/spotify-dude/data/dude.conf"
conf_data = {}

with open(CONF_FILE) as file:
    for line in file:
        line = line.split("#")[0].strip()

        if line and len(line.split("=")) >= 2:
            key = line.split("=")[0].strip()
            value = "=".join(line.split("=")[1:]).strip()

            conf_data[key] = value


def get(key: str) -> str:
    return conf_data[key]
