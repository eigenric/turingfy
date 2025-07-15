"""
Funciones para traducir entre programas Post Turing y playlists de canciones-token (y viceversa).
"""


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
    token_to_song = {
        track["name"].strip().upper(): track for track in instructions_playlist
    }
    return create_playlist_from_program(program_lines, token_to_song)


def build_token_to_song_from_playlist(playlist_tracks):
    """
    Dada una lista de canciones de Spotify (dicts), devuelve un diccionario instrucción->canción,
    usando el nombre de la canción (en mayúsculas, con espacios) como clave.
    Si hay varias canciones con el mismo nombre, la última sobrescribe.
    """
    token_to_song = {}
    for track in playlist_tracks:
        name = track["name"].strip().upper()
        token_to_song[name] = track
    return token_to_song


def program_to_playlist_tokens(program_lines):
    """
    Convierte un programa Post Turing (lista de instrucciones) a una lista de tokens/canciones.
    Ejemplo: 'IF 0' -> ['IF', '0']
    """
    playlist = []
    for line in program_lines:
        tokens = line.strip().split()
        playlist.extend(tokens)
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
        if token == "IF":
            program.append(f"IF {playlist_tokens[i+1]}")
            i += 2
        elif token == "GOTO":
            program.append(f"GOTO {playlist_tokens[i+1]}")
            i += 2
        else:
            program.append(token)
            i += 1
    return program
