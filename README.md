# Spotify Dude

A simple app to make colaborative Spotify playlists with friends funnier.

## I. Requirements

- A Linux machine.
- A Spotify account (free or premium).

## II. Installation

The installation process is not friendly at all by now :(

1. Clone the repo into `/opt`:
```
git clone https://github.com/gorcajo/spotify-dude.git /opt/spotify-dude
```

2. Install the SQLite DB:
```
/opt/spotify-dude/tools/helper.sh --installdb
```

3. Create a new app in your Spotify Developer Console: https://beta.developer.spotify.com/dashboard

4. Get your Client ID and Client Secret from the app you just created.

5. Get the refresh token following the instructions in `file:///opt/spotify-dude/tools/tokensgetter.html` with your browser.

6. Copy the conf file template into the real conf file:
```
cp /opt/spotify-dude/data/dude.conf.template /opt/spotify-dude/data/dude.conf
```

7. Fill out the conf file (see steps 4 and 5):
```
vim /opt/spotify-dude/data/dude.conf
```

8. Add a new cron entry with `crontab -e` like:
```
# Spotify Dude every 5 minutes:
*/5 * * * * ' python /opt/spotify-dude/dude.py --run
```

## III. Usage

The process of adding friends or playlist is not friendly neither :(

1. Enter the SQLite3 shell: `/opt/spotify-dude/tools/helper.sh --sqlite`

2. Insert some data in both `users` and `playlists` tables:
```
    insert into users(name, spotify_id, mail) values
    ('your name', 'your spotify user id', 'your email address'),
    ('friend name', 'friend spotify user id', 'friend email address'),
    ('another friend name', 'another friend spotify user id', 'another friend email address');

    insert into playlists(name, spotify_id, songs_last_seen) values
    ('a playlist name', 'playlist spotify id', 0)
    ('another playlist name', 'another playlist spotify id', 0);
```

3. Let cron do its magic.
