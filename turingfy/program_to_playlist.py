"""
Convierte un programa Post Turing en una playlist ejecutable en Spotify, usando la playlist base de instrucciones.
"""
from pprint import pprint

from .playlist_translator import (
    build_token_to_song_from_playlist,
    program_to_playlist_tokens,
)
from .playlist_utils import (
    get_instruction_playlist,
    get_spotify_client,
    get_tracks_from_playlist,
)


def create_playlist_from_post_program(
    sp, post_program, playlist_name, base_playlist_id=None
):
    """
    Crea una playlist ejecutable en Spotify a partir de un programa Post Turing.

    Args:
        sp (spotipy.client.Spotify): Cliente de Spotify.
        post_program (list): Programa Post Turing.
        playlist_name (str): Nombre de la playlist ejecutable.
        base_playlist_id (str, optional): ID de la playlist base de instrucciones. Defaults to None.

    Returns:
        str: ID de la playlist ejecutable creada.
    """
    if base_playlist_id is None:
        pl = get_instruction_playlist(sp)
        base_playlist_id = pl["id"]

    base_tracks = get_tracks_from_playlist(sp, base_playlist_id)
    token_to_song = build_token_to_song_from_playlist(base_tracks)
    tokens = program_to_playlist_tokens(post_program, token_to_song)

    user_id = sp.me()["id"]
    new_playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    track_ids = [song["id"] for song in tokens]
    uris = [f"spotify:track:{tid}" for tid in track_ids]
    sp.playlist_add_items(new_playlist["id"], uris)
    return new_playlist["id"]
