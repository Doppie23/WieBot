import os
import random
import re
import spotipy
from dotenv import load_dotenv
load_dotenv()
from spotipy.oauth2 import SpotifyClientCredentials

from youtube_search import YoutubeSearch

def spotify_nummers(PLAYLIST_LINK) -> list:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    # authenticate
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

    # create spotify session object
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # get uri from https link
    if match := re.match(r"https://open.spotify.com/playlist/(.*)\?", PLAYLIST_LINK):
        playlist_uri = match.groups()[0]
    else:
        raise ValueError("Expected format: https://open.spotify.com/playlist/...")

    results = session.playlist_tracks(playlist_uri)
    tracks = results['items']
    while results['next']:
        results = session.next(results)
        tracks.extend(results['items'])

    nummers_spotify = []

    for track in tracks:
        name = track["track"]["name"]
        artists = ", ".join(
            [artist["name"] for artist in track["track"]["artists"]]
        )
        nummer_arstist = name + ' ' + artists
        tuple = (nummer_arstist, name, artists)
        nummers_spotify.append(tuple)

    return nummers_spotify

def get_yt_id(search_query):
    results = YoutubeSearch(search_query, max_results=1).to_dict()
    id = results[0]['id']

    return id

def spotify_naar_youtubeid(url, aantal_nummers) -> list:
    nummers_spotify = spotify_nummers(url)
    randomnummers = random.sample(nummers_spotify, aantal_nummers)

    id_name_artist_list = []

    for tuple_nummer in randomnummers:
        search_query = tuple_nummer[0]
        name = tuple_nummer[1]
        artist = tuple_nummer[2]
        yt_id = get_yt_id(search_query)
        id_name_artist = (yt_id, name, artist)
        id_name_artist_list.append(id_name_artist)

    return id_name_artist_list