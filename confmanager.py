"""Manages the mail sending"""

CONF_FILE = "/opt/spotify-dude/data/dude.conf"

def get(key):
    """Returns the value corresponding to the gibven key"""

    value = None

    with open(CONF_FILE) as file:
        for line in file:
            pair = line.strip("\n").split("=")

            if pair[0] == key:
                value = pair[1]
                break

    return value
