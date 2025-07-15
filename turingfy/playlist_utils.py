"""
playlist_utils.py
Helpers para autenticación Spotify, búsqueda y validación de playlists, y utilidades generales.
"""
import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from turingfy.constants import INSTRUCTIONS_PLAYLIST_NAME


def get_spotify_client():
    """Devuelve un cliente Spotify autenticado usando variables de entorno (.env)."""
    load_dotenv()
    client_id = os.environ.get("SPOTIPY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI")
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-modify-public playlist-modify-private playlist-read-private",
        )
    )
    return sp


def get_playlist_by_name(sp, name, user_id=None):
    """Busca una playlist por nombre exacto para el usuario autenticado."""
    if user_id is None:
        user_id = sp.me()["id"]
    playlists = sp.user_playlists(user_id)
    for pl in playlists["items"]:
        if pl["name"].strip().lower() == name.strip().lower():
            return pl
    return None


def get_instruction_playlist(sp, user_id=None):
    """Devuelve la playlist base de instrucciones o lanza ValueError si no existe."""
    pl = get_playlist_by_name(sp, INSTRUCTIONS_PLAYLIST_NAME, user_id)
    if not pl:
        raise ValueError(
            f"No se encontró la playlist '{INSTRUCTIONS_PLAYLIST_NAME}' en tu cuenta de Spotify."
        )
    return pl


def get_tracks_from_playlist(sp, playlist_id):
    """Devuelve una lista de tracks (dicts) de una playlist por ID."""
    results = sp.playlist_tracks(playlist_id)
    return [item["track"] for item in results["items"]]


def add_missing_tracks(sp, playlist_id, needed_names):
    """
    Añade canciones faltantes (por nombre exacto) a la playlist base si no existen ya.
    """
    tracks = get_tracks_from_playlist(sp, playlist_id)
    existing_names = set(track["name"].strip().upper() for track in tracks)
    for name in needed_names:
        if name.upper() in existing_names:
            continue
        results = sp.search(q=f"track:{name}", type="track", limit=1)
        items = results["tracks"]["items"]
        if items:
            track = items[0]
            sp.playlist_add_items(playlist_id, [track["uri"]])
            print(
                f"Añadida '{track['name']}' de {track['artists'][0]['name']} a la playlist base."
            )
        else:
            print(f"No se encontró canción llamada '{name}'.")


def reorder_playlist(sp, playlist_id, ordered_names):
    """
    Reordena la playlist base según el orden dado de nombres (si existen en la playlist).
    """
    tracks = get_tracks_from_playlist(sp, playlist_id)
    name_to_track = {track["name"].strip().upper(): track for track in tracks}
    ordered_tracks = []
    for name in ordered_names:
        track = name_to_track.get(name.upper())
        if track:
            ordered_tracks.append(track)
        else:
            print(
                f"ADVERTENCIA: No se encontró la canción '{name}' en la playlist base."
            )
    uris = [track["uri"] for track in ordered_tracks]
    if uris:
        sp.playlist_replace_items(playlist_id, uris)
        print(
            "La playlist base ha sido reordenada según el orden especificado."
        )


def get_instruction_dict_from_playlist(
    sp, playlist_id, ordered_instruction_names
):
    """
    Devuelve un diccionario {spotify_id: {'name': nombre, 'id': spotify_id, 'instruction': instruccion}} usando el orden de la playlist y la lista de instrucciones.
    """
    base_tracks = [
        item["track"] for item in sp.playlist_tracks(playlist_id)["items"]
    ]
    trackid_to_instruction = {}
    num_tracks = len(base_tracks)
    num_instr = len(ordered_instruction_names)
    if num_tracks != num_instr:
        print(
            f"ADVERTENCIA: El número de canciones ({num_tracks}) no coincide con el número de instrucciones ({num_instr}). Solo se mapearán las coincidencias posibles."
        )
    for idx, track in enumerate(base_tracks):
        if idx < num_instr:
            trackid_to_instruction[
                (track["id"], track["name"])
            ] = ordered_instruction_names[idx]
        else:
            print(
                f"Canción extra en la playlist: '{track['name']}' (ID: {track['id']})"
            )
    if num_tracks < num_instr:
        print(
            "\nFALTAN canciones en la playlist para cubrir todas las instrucciones. Faltan:"
        )
        for name in ordered_instruction_names[num_tracks:]:
            print(f"- {name}")
    return trackid_to_instruction
