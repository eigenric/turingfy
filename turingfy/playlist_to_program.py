"""
Extrae un programa Post Turing a partir de una playlist ejecutable de Spotify, usando la playlist base de instrucciones para mapear tokens.
"""
from .constants import ORDERED_INSTRUCTION_NAMES
from .playlist_translator import (
    build_token_to_song_from_playlist,
    playlist_to_post_program,
)
from .playlist_utils import (
    get_instruction_dict_from_playlist,
    get_spotify_client,
    get_tracks_from_playlist,
)


def extract_post_program_from_playlist(
    sp, exec_playlist_id, base_playlist_id=None
):
    exec_tracks = get_tracks_from_playlist(sp, exec_playlist_id)

    playlist_token_map = get_instruction_dict_from_playlist(
        sp, base_playlist_id, ORDERED_INSTRUCTION_NAMES
    )
    # Construir lista de instrucciones (track dicts) a partir de exec_tracks
    post_program, program_track_ids = playlist_to_post_program(
        exec_tracks, playlist_token_map
    )

    return post_program, program_track_ids
