#!/bin/bash

APP_DIR="/opt/spotify-dude"
DB_FILE="$APP_DIR/data/dude.db"

function main() {
    if [ $# -eq 1 ]; then
        if [ "$1" == "--sqlite" ]; then
            if [ -f $DB_FILE ]; then
                enterSqliteShell
            else
                echo "App not installed yet. See the script source code."
                exit 3
            fi
        elif [ "$1" == "--installdb" ]; then
            installDb
        else
            echo "Wrong argument '$1'. See the script source code."
            exit 2
        fi
    else
        echo "Wrong arguments. See the script source code."
        exit 1
    fi
}

function enterSqliteShell() {
    sqlite3 -header -column $DB_FILE
}

function installDb() {
    if [ -d $APP_DIR ]; then
        sqlite3 $DB_FILE "
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            spotify_id TEXT,
            mail TEXT
            )"

        sqlite3 $DB_FILE "
            CREATE TABLE IF NOT EXISTS playlists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            spotify_id TEXT,
            songs_last_seen INTEGER
            )"

        echo "DB successfully installed."
    else
        echo "You must manually copy the app to '$APP_DIR/'' before install:"
        echo "  'sudo cp <your-local-copy> /opt'"
        exit 4
    fi
}

main $@
