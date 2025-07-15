"""
Funciones para traducir entre programas Post Turing y playlists de canciones-token (y viceversa).
"""

from .constants import ORDERED_INSTRUCTION_NAMES


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


def create_playlist_from_program(program_lines, token_to_song):
    """
    Dado un programa Post Turing (lista de instrucciones) y un diccionario instrucción->canción,
    devuelve la playlist (lista de dicts de canciones en orden).
    """
    playlist = []
    for line in program_lines:
        instr = line.strip().upper()
        song = token_to_song.get(instr)
        if not song:
            raise ValueError(f"No hay canción para la instrucción '{instr}'")
        playlist.append(song)
    return playlist


def create_playlist_from_post_program_and_instructions_playlist(
    program_lines, instructions_playlist
):
    """
    Dado un programa Post Turing (lista de instrucciones) y una playlist de instrucciones (lista de canciones),
    devuelve la playlist resultante para ese programa usando el mapeo nombre->canción de la playlist de instrucciones.
    """
    # Construye el mapeo instrucción->canción
    token_to_song = {}
    for i, track in enumerate(instructions_playlist):
        if i < len(ORDERED_INSTRUCTION_NAMES):
            token_to_song[ORDERED_INSTRUCTION_NAMES[i]] = track
    return create_playlist_from_program(program_lines, token_to_song)


def build_token_to_song_from_playlist(playlist_tracks):
    """
    Dada una lista de canciones de Spotify (dicts), devuelve un diccionario instrucción->canción,
    usando el nombre de la canción (en mayúsculas, con espacios) como clave.
    Si hay varias canciones con el mismo nombre, la última sobrescribe.
    """
    token_to_song = {}
    for i, track in enumerate(playlist_tracks):
        if i < len(ORDERED_INSTRUCTION_NAMES):
            token_to_song[ORDERED_INSTRUCTION_NAMES[i]] = track
    return token_to_song


def program_to_playlist_tokens(program_lines, token_to_song):
    """
    Convierte un programa Post Turing (lista de instrucciones) a una lista de tokens/canciones.
    Ejemplo: 'IF 0' -> ['IF', '0']
    """
    playlist = []
    for line in program_lines:
        tokens = line.strip().split()
        if len(tokens) > 1 and (
            tokens[0].upper() == "IF" or tokens[0].upper() == "GOTO"
        ):
            for token in tokens:
                song = token_to_song.get(token.upper())
                if not song:
                    raise ValueError(
                        f"No hay canción para la instrucción '{token}'"
                    )
                playlist.append(song)
        else:
            song = token_to_song.get(line.strip().upper())
            if not song:
                raise ValueError(
                    f"No hay canción para la instrucción '{line.strip()}'"
                )
            playlist.append(song)
    return playlist


def playlist_tokens_to_program(playlist_tokens):
    """
    Convierte una lista de canciones/tokens a instrucciones Post Turing.
    Ejemplo: ['IF', '0', 'GOTO', '7', 'YES'] -> ['IF 0', 'GOTO 7', 'YES']
    """
    program = []
    i = 0
    while i < len(playlist_tokens):
        token = playlist_tokens[i].upper()
        if token == "IF" and i + 1 < len(playlist_tokens):
            program.append(f"IF {playlist_tokens[i+1]}")
            i += 2
            continue
        if token == "GOTO" and i + 1 < len(playlist_tokens):
            program.append(f"GOTO {playlist_tokens[i+1]}")
            i += 2
            continue
        program.append(playlist_tokens[i])
        i += 1
    return program


def playlist_to_post_program(exec_tracks, playlist_token_map):
    """
    Dada una lista de tracks (playlist ejecutable) y un diccionario (track_id,track_name)->instruccion,
    devuelve el programa Post Turing fusionando IF/GOTO y la lista de track_ids.
    """
    instructions = [
        {"uri": track["uri"], "name": track["name"]} for track in exec_tracks
    ]
    post_program = []
    program_track_ids = []
    idx = 0
    while idx < len(instructions):
        track = instructions[idx]
        track_id = track["uri"].split(":")[-1]
        track_name = track["name"]
        instr = playlist_token_map.get((track_id, track_name))
        if instr is None:
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
    return post_program, program_track_ids
