"""
Construye y reordena la playlist base de instrucciones en Spotify según el orden estándar definido en turingfy/constants.py.
Asegura que todas las canciones necesarias estén presentes y en el orden correcto.
"""
from constants import ORDERED_INSTRUCTION_NAMES
from playlist_utils import (
    add_missing_tracks,
    get_instruction_playlist,
    get_spotify_client,
    reorder_playlist,
)

sp = get_spotify_client()
pl = get_instruction_playlist(sp)
BASE_PLAYLIST_ID = pl["id"]

add_missing_tracks(sp, BASE_PLAYLIST_ID, ORDERED_INSTRUCTION_NAMES)
reorder_playlist(sp, BASE_PLAYLIST_ID, ORDERED_INSTRUCTION_NAMES)

print("Playlist base de instrucciones lista y ordenada.")
