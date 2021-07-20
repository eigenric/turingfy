import os
import time
from pprint import pprint
from sys import exit

import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

user_auth = "riki319"
user_program = "riki319"

program_name = "Turing Machine - Palindrome"

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

devices = sp.devices()["devices"]
computer_device = next(
    device for device in devices if device["type"] == "Computer"
)

if not computer_device["is_active"]:
    sp.transfer_playback(computer_device["id"])

playlists = sp.user_playlists(user_program)
program = next(pl for pl in playlists["items"] if pl["name"] == program_name)
word = program["description"]
instructions = [
    {"index": i, "name": item["track"]["name"], "uri": item["track"]["uri"]}
    for i, item in enumerate(sp.playlist_tracks(program["id"])["items"])
]

reader_head = 0
accepted = False

no_goto_instructions = (
    "Delete",
    "Left",
    "Right",
    "Start Again",
    "Right to End",
)
reader_head = 0
t = 3

current_instruction = instructions[0]
halt = (
    "Yes" in current_instruction["name"] or "No" in current_instruction["name"]
)

while not halt:
    print(word)
    print(current_instruction["name"])
    sp.add_to_queue(current_instruction["uri"])
    time.sleep(t)
    sp.next_track()

    if current_instruction["name"] == "If":
        next_index = current_instruction["index"] + 1
        goto_index = current_instruction["index"] + 2
        line_number_index = current_instruction["index"] + 3

        goto = instructions[goto_index]

        if goto["name"] != "Goto":
            print("Incorrect Syntax: Missing Goto")
            exit(1)

        symbol = instructions[next_index]
        line_number = instructions[line_number_index]

        sp.add_to_queue(symbol["uri"])
        sp.add_to_queue(goto["uri"])
        sp.add_to_queue(line_number["uri"])

        if symbol["name"] == "Zero":
            symbol = "0"
        elif symbol["name"] == "One":
            symbol = "1"
        elif symbol["name"] == "Blank Space":
            symbol = "#"

        if word[reader_head] == symbol:
            current_instruction = instructions[int(line_number["name"])]
        else:
            next_instruction_index = current_instruction["index"] + 4
            current_instruction = instructions[next_instruction_index]

    elif current_instruction["name"] == "Goto":
        line_number_index = current_instruction["index"] + 1
        line_number = instructions[line_number_index]

        sp.add_to_queue(line_number["uri"])

        if line_number["name"] == "Zero":
            line_number["name"] = "0"
        elif line_number["name"] == "One":
            line_number["name"] = "1"

        current_instruction = instructions[int(line_number["name"])]

        sp.add_to_queue(line_number["uri"])
        time.sleep(t)
        sp.next_track()

        current_instruction = instructions[int(line_number["name"])]

    elif current_instruction["name"] in no_goto_instructions:

        if current_instruction["name"] == "Delete":
            word = word[:reader_head] + "#" + word[reader_head + 1 :]
            if user_auth == user_program:
                sp.user_playlist_change_details(
                    user_program, program["id"], description=word
                )

        elif current_instruction["name"] == "Left":
            reader_head -= 1

        elif current_instruction["name"] == "Right":
            reader_head += 1

        elif current_instruction["name"] == "Start Again":
            reader_head = len(word) - len(word.lstrip("#")) - 1

        elif current_instruction["name"] == "Right to End":
            reader_head = len(word.rstrip("#"))

        next_instruction_index = current_instruction["index"] + 1
        current_instruction = instructions[next_instruction_index]

    halt = (
        "Yes" in current_instruction["name"]
        or "No" in current_instruction["name"]
    )


sp.start_playback()

sp.add_to_queue(current_instruction["uri"])
time.sleep(t)
sp.next_track()

if "Yes" in current_instruction["name"]:
    print(f"La palabra {word} ha sido aceptada por {program_name}")
elif "No" in current_instruction["name"]:
    print(f"La palabra {word} ha sido rechazada por {program_name}")

# TODO: Manage playlist pagination.
# while playlists:
#   for i, playlist in enumerate(playlists["items"]):
#       print(f"\t{i + 1 + playlists["offset"]} {playlist["uri"]} {playlist["name"]}")
#       if playlists["next"]:
#           playlists = sp.next(playlists)
#       else:
#           playlists = None
