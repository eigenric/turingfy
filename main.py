"""
main.py
Script principal: sincroniza la ejecución de un programa Post Turing con la reproducción de una playlist de Spotify.
"""
from pprint import pprint

from turingfy.playlist_to_program import extract_post_program_from_playlist
from turingfy.playlist_utils import (
    get_instruction_playlist,
    get_playlist_by_name,
    get_spotify_client,
)
from turingfy.program_to_playlist import create_playlist_from_post_program
from turingfy.spotify_post_machine import SpotifyPostTuringMachine

# Define aquí el nombre de la playlist ejecutable y el programa Post Turing
PROGRAM_PLAYLIST_NAME = "palindrome.tfy"
POST_PROGRAM = [
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

sp = get_spotify_client()
base_playlist_id = get_instruction_playlist(sp)["id"]
playlist_id = get_playlist_by_name(sp, PROGRAM_PLAYLIST_NAME)["id"]

# Crea la playlist ejecutable si no existe
if playlist_id is None:
    playlist_id = create_playlist_from_post_program(
        sp, POST_PROGRAM, PROGRAM_PLAYLIST_NAME, base_playlist_id
    )
    print(
        f"Playlist ejecutable '{PROGRAM_PLAYLIST_NAME}' lista para sincronización."
    )
else:
    print(
        f"Playlist ejecutable '{PROGRAM_PLAYLIST_NAME}' ya existe. Utilizando su ID."
    )

post_program, program_track_ids = extract_post_program_from_playlist(
    sp, playlist_id, base_playlist_id
)


machine = SpotifyPostTuringMachine(playlist_id, sp, program_track_ids, delay=5)
machine.load_program(post_program)
machine.run()
