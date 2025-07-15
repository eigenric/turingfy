import os
import time
from pprint import pprint
from sys import exit

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from scripts.playlist_instructions_map import (
    BASE_PLAYLIST_ID,
    get_instruction_dict_from_playlist,
    ordered_instruction_names,
)
from turingfy.spotify_post_machine import SpotifyPostTuringMachine
from turingfy.turing_machine import PostTuringMachine

load_dotenv()

CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

user_auth = "riki319"
user_program = "riki319"
program_name = "palindrome.tfy"

t = 5
scope = "user-modify-playback-state playlist-modify-public user-read-playback-state"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        username=user_auth,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope,
    )
)

# Espera hasta que haya dispositivos
while True:
    devices = sp.devices()["devices"]
    if devices:
        break
    print("Buscando dispositivos...")
    time.sleep(2)

computer_device = next(
    device for device in devices if device["type"] == "Speaker"
)
if not computer_device["is_active"]:
    sp.transfer_playback(computer_device["id"])

playlists = sp.user_playlists(user_program)
program = next(pl for pl in playlists["items"] if pl["name"] == program_name)
playlist_id = program["id"]

instructions = [
    {
        "index": i,
        "name": item["track"]["name"],
        "artist": item["track"]["artists"][0]["name"],
        "uri": item["track"]["uri"],
    }
    for i, item in enumerate(sp.playlist_tracks(playlist_id)["items"])
]
print("Playlist instructions:")
pprint(instructions)

playlist_token_map = get_instruction_dict_from_playlist(
    sp, BASE_PLAYLIST_ID, ordered_instruction_names
)

# Construir el programa Post a partir de la playlist y el diccionario
post_program = []
program_track_ids = []
idx = 0
while idx < len(instructions):
    track = instructions[idx]
    track_id = track["uri"].split(":")[-1]
    track_name = track["name"]
    instr = playlist_token_map.get((track_id, track_name))
    if instr is None:
        print(
            f"ADVERTENCIA: No se encontró instrucción para track {track_name} ({track_id})"
        )
        idx += 1
        continue
    instr = instr.upper()
    # Fusionar IF y GOTO
    if instr == "IF" and idx + 1 < len(instructions):
        next_track = instructions[idx + 1]
        next_id = next_track["uri"].split(":")[-1]
        next_name = next_track["name"]
        next_instr = playlist_token_map.get((next_id, next_name))
        if next_instr:
            post_program.append(f"IF {next_instr}")
            program_track_ids.append(track_id)
            idx += 2
            continue
    if instr == "GOTO" and idx + 1 < len(instructions):
        next_track = instructions[idx + 1]
        next_id = next_track["uri"].split(":")[-1]
        next_name = next_track["name"]
        next_instr = playlist_token_map.get((next_id, next_name))
        if next_instr:
            post_program.append(f"GOTO {next_instr}")
            program_track_ids.append(track_id)
            idx += 2
            continue
    post_program.append(instr)
    program_track_ids.append(track_id)
    idx += 1

print("\nPrograma Post Turing generado:")
pprint(post_program)

machine = SpotifyPostTuringMachine(playlist_id, sp, program_track_ids, delay=t)
machine.load_program(post_program)
machine.run()
