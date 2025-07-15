import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Configura las credenciales
client_id = os.environ.get("SPOTIPY_CLIENT_ID")
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")

# Autentica y obtiene el token de acceso
client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# URI de la playlist
playlist_uri = "spotify:playlist:1TGnAeGRWCVZsYxdBPjStO"

# Obtiene los datos de la playlist
playlist = sp.playlist(playlist_uri)

# Procesa y muestra la información de la playlist
for track in playlist["tracks"]["items"]:
    track_name = track["track"]["name"]
    track_artist = track["track"]["artists"][0]["name"]
    print(f"{track_name} by {track_artist}")
