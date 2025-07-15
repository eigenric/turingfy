"""
Ejemplo de uso de playlist_translator + Spotipy:
- Crear una playlist de Spotify a partir de un programa Post Turing y canciones-token base.
- Recuperar el programa Post Turing desde una playlist ordenada de canciones.
"""
import os
import sys

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from turingfy.playlist_translator import (
    build_token_to_song_from_playlist,
    create_playlist_from_program,
    playlist_tokens_to_program,
    program_to_playlist_tokens,
)

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

load_dotenv()
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-public playlist-modify-private playlist-read-private",
    )
)

# 1. Obtener canciones base de playlist de tokens
INSTRUCTIONS_PLAYLIST_NAME = "instructions"

# Busca el ID de la playlist por nombre
user_id = sp.me()["id"]
playlists = sp.user_playlists(user_id)
print("Tus playlists disponibles:")
for pl in playlists["items"]:
    print(f"- '{pl['name']}' (ID: {pl['id']})")
base_playlist = next(
    (
        pl
        for pl in playlists["items"]
        if pl["name"].strip().lower() == INSTRUCTIONS_PLAYLIST_NAME
    ),
    None,
)
if not base_playlist:
    raise ValueError(
        f"No se encontró la playlist '{INSTRUCTIONS_PLAYLIST_NAME}' en tu cuenta de Spotify."
    )
BASE_PLAYLIST_ID = base_playlist["id"]

base_tracks = [
    item["track"] for item in sp.playlist_tracks(BASE_PLAYLIST_ID)["items"]
]
token_to_song = build_token_to_song_from_playlist(base_tracks)

# Busca y añade canciones para los números necesarios si no existen ya
needed_numbers = ["2", "9", "25", "29", "30"]
existing_names = set(track["name"].strip().upper() for track in base_tracks)
for num in needed_numbers:
    if num.upper() in existing_names:
        print(f"La canción '{num}' ya está en la playlist base.")
        continue
    # Buscar canción exacta en Spotify
    results = sp.search(q=f"track:{num}", type="track", limit=1)
    items = results["tracks"]["items"]
    if items:
        track = items[0]
        print(
            f"Añadiendo '{track['name']}' de {track['artists'][0]['name']} a la playlist base."
        )
        sp.playlist_add_items(BASE_PLAYLIST_ID, [track["uri"]])
    else:
        print(f"No se encontró canción llamada '{num}'.")

# Orden deseado de instrucciones en la playlist
ordered_instruction_names = [
    "IF",
    "0",
    "1",
    "#",
    "GOTO",
    "DELETE",
    "LEFT",
    "RIGHT",
    "RIGHT TO THE END",
    "START AGAIN",
    "YES",
    "NO",
    "2",
    "9",
    "25",
    "29",
    "30",
]

# Vuelve a obtener la lista actualizada de canciones base
base_tracks = [
    item["track"] for item in sp.playlist_tracks(BASE_PLAYLIST_ID)["items"]
]
token_to_song = build_token_to_song_from_playlist(base_tracks)

# Construye la playlist reordenada según el orden deseado (si existe la canción)
ordered_tracks = []
for name in ordered_instruction_names:
    track = token_to_song.get(name.upper())
    if track:
        ordered_tracks.append(track)
    else:
        print(
            f"ADVERTENCIA: No se encontró la canción '{name}' en la playlist base."
        )

# Reemplaza el contenido de la playlist base con el orden correcto
uris = [track["uri"] for track in ordered_tracks]
sp.playlist_replace_items(BASE_PLAYLIST_ID, uris)
print(
    "La playlist 'instructions' ha sido reordenada y completada según el orden especificado."
)

# 2. Programa Post Turing de ejemplo
post_program = [
    "START AGAIN",
    "GOTO 2",
    "IF #",
    "GOTO 29",
    "IF 0",
    "GOTO 9",
    "IF 1",
    "GOTO 17",
    "GOTO 30",
    "DELETE",
    "RIGHT TO THE END",
    "LEFT",
    "IF #",
    "GOTO 29",
    "IF 0",
    "GOTO 25",
    "GOTO 30",
    "DELETE",
    "RIGHT TO THE END",
    "LEFT",
    "IF #",
    "GOTO 29",
    "IF 1",
    "GOTO 25",
    "GOTO 30",
    "DELETE",
    "START AGAIN",
    "RIGHT",
    "GOTO 2",
    "YES",
    "NO",
]

# 3. Crear la playlist ejecutable usando el sistema de tokens

# Obtén la playlist de instrucciones actualizada
instructions_playlist = [
    item["track"] for item in sp.playlist_tracks(BASE_PLAYLIST_ID)["items"]
]
token_to_song = build_token_to_song_from_playlist(instructions_playlist)

# Traduce el programa a tokens
tokens = program_to_playlist_tokens(post_program)

# Validación previa: asegúrate de que todos los tokens existen en la playlist de instrucciones
missing_tokens = [
    token for token in tokens if token.upper() not in token_to_song
]
if missing_tokens:
    print(
        "ERROR: Los siguientes tokens no tienen canción asociada en la playlist 'instructions':"
    )
    for token in set(missing_tokens):
        print(f"- {token}")
    # Intentar buscar y añadir automáticamente canciones sugeridas para cada token
    for token in set(missing_tokens):
        print(f"Buscando sugerencia en Spotify para el token '{token}'...")
        results = sp.search(q=f"track:{token}", type="track", limit=1)
        items = results["tracks"]["items"]
        if items:
            track = items[0]
            print(
                f"Añadiendo '{track['name']}' de {track['artists'][0]['name']} a la playlist 'instructions'."
            )
            sp.playlist_add_items(BASE_PLAYLIST_ID, [track["uri"]])
        else:
            print(
                f"No se encontró ninguna canción sugerida para el token '{token}'. Añádela manualmente si es necesario."
            )
    print("Vuelve a ejecutar el script para continuar el flujo.")
    exit(1)

# Mapea cada token a la canción correspondiente
ordered_playlist = [token_to_song[token.upper()] for token in tokens]

# 4. Crear la playlist en Spotify a partir del programa
new_playlist_name = "palindrome.tfy"
new_playlist = sp.user_playlist_create(
    user_id, new_playlist_name, public=False
)
ordered_uris = [track["uri"] for track in ordered_playlist]
sp.playlist_add_items(new_playlist["id"], ordered_uris)
print(f"Playlist creada: {new_playlist['external_urls']['spotify']}")

# 5. Recuperar el programa desde una playlist ejecutable (.tfy)

ordered_tracks = [
    item["track"] for item in sp.playlist_tracks(new_playlist["id"])["items"]
]
tokens_from_playlist = [
    track["name"].strip().upper() for track in ordered_tracks
]
recovered_program = playlist_tokens_to_program(tokens_from_playlist)
print("Programa recuperado desde la playlist ejecutable:")
for line in recovered_program:
    print(line)

# 5. Recuperar el programa desde una playlist (flujo inverso)
ordered_tracks = [
    item["track"] for item in sp.playlist_tracks(new_playlist["id"])["items"]
]
tokens = [track["name"].strip().upper() for track in ordered_tracks]
recovered_program = playlist_tokens_to_program(tokens)
print("Programa recuperado:")
for line in recovered_program:
    print(line)
