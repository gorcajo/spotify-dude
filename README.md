# spotify-dude

A simple app to make colaborative Spotify playlists funnier with friends.

## Requirements

- A Linux machine
- A Spotify account (free or premium)

## Installation

1. Clone the repo into `/opt`:

```sudo git clone https://github.com/gorcajo/spotify-dude.git /opt/spotify-dude```

2. Install the SQLite DB:

```/opt/spotify-dude/tools/helper.sh --installdb```

3. Create a new app in your Spotify Developer Console:

https://beta.developer.spotify.com/dashboard

4. Get your Client ID and Client Secret from the app you just created.

5. Get the refresh token following the instructions in `spotify-dude/tools/tokensgetter.html`:

file:///opt/spotify-dude/tools/tokensgetter.html

6. Fill out the conf file:

`$APP_DIR/data/dude.conf.template`

7. Rename it with:

`sudo mv $APP_DIR/data/dude.conf.template $APP_DIR/data/dude.conf`

8. Add a new cron entry with `sudo crontab -e` like:

```*/5 * * * * ' python $APP_DIR/dude.py --run```

## Usage

1. Let cron do its magic :)
