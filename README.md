# Spotify Dude

A simple bot to make colaborative Spotify playlists with friends funnier.

## I. Requirements

- A Linux machine with:
    - Python 3.6.
    - SQLite3.
- A Spotify account (free or premium).

## II. Installation

The installation process is not friendly at all by now :(

1. Clone the repo into `/opt`:
```
git clone https://github.com/gorcajo/spotify-dude.git /opt/spotify-dude
```

2. Copy the conf file template into the real conf file:
```
cp /opt/spotify-dude/data/dude.conf.template /opt/spotify-dude/data/dude.conf
```

3. Create a new app in your Spotify Developer Console: https://beta.developer.spotify.com/dashboard

4. Get your Client ID and Client Secret from the app you just created.

5. Get the refresh token following the instructions in `file:///opt/spotify-dude/tools/tokensgetter.html` with your browser.

6. Fill out the conf file (see steps 3 thru 5):
```
vim /opt/spotify-dude/data/dude.conf
```

7. Install the SQLite DB:
```
/opt/spotify-dude/run --dbinstall
```

8. (Optional) Run `/opt/spotify-dude/run --help` to know more about the bot.

9. Add a new cron entry with `crontab -e` like:
```
# Spotify Dude every 5 minutes:
*/5 * * * * /opt/spotify-dude/run --roulette --silent
```

## III. Usage

The process of adding friends or playlist is not friendly neither :(

1. Enter the SQLite3 shell: `/opt/spotify-dude/tools/run --dbshell`

2. Insert some data in both `users` and `playlists` tables:
```
    sqlite> insert into users(name, spotify_id, mail) values
    sqlite> ('your name', 'your spotify user id', 'your email address'),
    sqlite> ('friend name', 'friend spotify user id', 'friend email address'),
    sqlite> ('another friend name', 'another friend spotify user id', 'another friend email address');

    sqlite> insert into playlists(name, spotify_id, songs_last_seen) values
    sqlite> ('a playlist name', 'playlist spotify id', 0)
    sqlite> ('another playlist name', 'another playlist spotify id', 0);
```

3. Let cron and this bot do their magic.

4. You can check the logs at `/opt/spotify-dude/logs/` (if you left that parameter as default in `dude.conf`).
