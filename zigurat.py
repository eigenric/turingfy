import os
from pprint import pprint
from sys import exit

import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

user = "riki319"
program_name = "Turing Machine - Palindrome"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="streaming",
    )
)

playlists = sp.user_playlists(user)
program = next(pl for pl in playlists["items"] if pl["name"] == program_name)
word = program["description"]
instructions = [
    {"index": i, "name": item["track"]["name"], "uri": item["track"]["uri"]}
    for i, item in enumerate(sp.playlist_tracks(program["id"])["items"])
]

reader_head = 0
accepted = False

current_instruction = instructions[0]
halt = (
    "Yes" in current_instruction["name"] or "No" in current_instruction["name"]
)

while not halt:
    sp.add_to_queue(current_instruction["uri"])

    if "Yes" in current_instruction["name"]:
        accepted = True
        break
    elif "No" in current_instruction["name"]:
        break

    next_instruction_index = current_instruction["index"] + 1
    current_instruction = instructions[next_instruction_index]

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

    elif current_instruction["name"] == "Delete":
        word[reader_head] = "#"
        sp.user_playlist_change_details(user, program["id"], description=word)

    elif current_instruction["name"] == "Left":
        reader_head -= 1

    elif current_instruction["name"] == "Right":
        reader_head += 1

    elif current_instruction["name"] == "Start Again":
        reader_head = -1

    elif current_instruction["name"] == "Right to End":
        reader_head = len(word)

    elif current_instruction["name"] == "Goto":
        line_number_index = current_instruction["index"] + 1
        line_number = instructions[line_number_index]

        sp.add_to_queue(line_number["uri"])

        current_instruction = instructions[int(line_number["name"])]

    halt = (
        "Yes" in current_instruction["name"]
        or "No" in current_instruction["name"]
    )

if accepted:
    print(f"La palabra {word} ha sido aceptada por {program_name}")
else:
    print(f"La palabra {word} ha sido rechazada por {program_name}")


sp.start_playback()

# TODO: Manage playlist pagination.
# while playlists:
# for i, playlist in enumerate(playlists['items']):
# print(f"\t{i + 1 + playlists['offset']} {playlist['uri']} {playlist['name']}")
# if playlists['next']:
# playlists = sp.next(playlists)
# else:
# playlists = None
