import os
import sys

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

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
        scope="playlist-read-private playlist-modify-private playlist-modify-public",
    )
)

INSTRUCTIONS_PLAYLIST_NAME = "instructions"
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
    "17",
    "25",
    "29",
    "30",
]

# Export explícito para otros scripts
__all__ = [
    "get_instruction_dict_from_playlist",
    "BASE_PLAYLIST_ID",
    "ordered_instruction_names",
]

user_id = sp.me()["id"]
playlists = sp.user_playlists(user_id)
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


def get_instruction_dict_from_playlist(
    sp,
    playlist_id=BASE_PLAYLIST_ID,
    ordered_instruction_names=ordered_instruction_names,
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


# --- USO: ---
trackid_to_instruction = get_instruction_dict_from_playlist(
    sp, BASE_PLAYLIST_ID, ordered_instruction_names
)
print("\nDiccionario Spotify ID -> Instrucción (orden playlist):")
for tid, instr in trackid_to_instruction.items():
    print(f"{tid}: {instr}")

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


# --- Tokenización robusta usando los nombres de canciones de la playlist ---
def tokenize_program_with_playlist_tokens(program_lines, valid_tokens):
    """
    Tokeniza el programa usando solo los tokens válidos (frases) de la playlist, greedy por el match más largo.
    """
    tokens = []
    valid_tokens_upper = [tok.upper() for tok in valid_tokens]
    for line in program_lines:
        words = line.strip().upper().split()
        i = 0
        while i < len(words):
            matched = False
            for j in range(len(words), i, -1):
                candidate = " ".join(words[i:j])
                if candidate in valid_tokens_upper:
                    tokens.append(candidate)
                    i = j
                    matched = True
                    break
            if not matched:
                tokens.append(words[i])
                i += 1
    return tokens


if __name__ == "__main__":
    # --- Crear la playlist ejecutable del programa usando el diccionario SOLO si no existe ---
    EXEC_PLAYLIST_NAME = "palindrome.tfy"
    user_id = sp.current_user()["id"]
    existing_playlists = sp.user_playlists(user_id)["items"]
    exec_playlist = next(
        (pl for pl in existing_playlists if pl["name"] == EXEC_PLAYLIST_NAME),
        None,
    )

    if exec_playlist:
        print(
            f"Playlist ejecutable ya existe: {exec_playlist['external_urls']['spotify']}"
        )
    else:
        # Usar los nombres de las canciones de la playlist como tokens válidos
        playlist_tokens = [
            track["name"].strip().upper() for track in base_tracks
        ]
        program_tokens = tokenize_program_with_playlist_tokens(
            post_program, playlist_tokens
        )

        # Mapea cada token a su canción-id
        instruction_to_id = {
            v.upper(): k for k, v in trackid_to_instruction.items()
        }
        playlist_ids = []
        missing = []
        for token in program_tokens:
            track_id = instruction_to_id.get(token.upper())
            if not track_id:
                missing.append(token)
            else:
                playlist_ids.append(track_id)

        if missing:
            print(
                "\nERROR: No se pudo encontrar canción para los siguientes tokens del programa:"
            )
            for token in set(missing):
                print(f"- {token}")
            print(
                "No se creará la playlist ejecutable hasta que todos los tokens tengan canjción."
            )
        else:
            # Crear la playlist ejecutable en Spotify
            playlist_name = "palindrome.tfy"
            new_playlist = sp.user_playlist_create(
                user_id, playlist_name, public=False
            )
            uris = [f"spotify:track:{tid}" for tid in playlist_ids]
            sp.playlist_add_items(new_playlist["id"], uris)
            print(
                f"\nPlaylist ejecutable creada: {new_playlist['external_urls']['spotify']}"
            )
