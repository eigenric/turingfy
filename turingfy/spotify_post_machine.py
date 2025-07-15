import time

from turingfy.turing_machine import PostTuringMachine


class SpotifyPostTuringMachine(PostTuringMachine):
    def __init__(self, playlist_id, sp, program_track_ids, delay=5):
        # Lee la palabra de input desde la descripción de la playlist
        playlist = sp.playlist(playlist_id)
        description = playlist.get("description", "")
        input_word = "".join(
            c for c in description if c.isalnum()
        )  # solo letras y números
        super().__init__(input_word)
        self.sp = sp
        self.program_track_ids = (
            program_track_ids  # lista: track_id por instrucción
        )
        self.delay = delay
        self.playlist_id = playlist_id

    def _write(self, symbol):
        super()._write(symbol)
        # Actualiza la descripción de la playlist con la cinta actual
        new_word = "".join(self.tape)
        try:
            self.sp.playlist_change_details(
                self.playlist_id, description=new_word
            )
        except Exception as e:
            print(f"Error actualizando descripción: {e}")

    def play_instruction(self, instr_idx):
        # Reproduce la canción correspondiente al índice de instrucción
        if 0 <= instr_idx < len(self.program_track_ids):
            track_id = self.program_track_ids[instr_idx]
            if track_id:
                self.sp.start_playback(uris=[f"spotify:track:{track_id}"])
                time.sleep(self.delay)

    def step(self):
        if self.halted or self.pc >= len(self.program):
            self.halted = True
            return
        # Reproduce la canción correspondiente a esta instrucción
        self.play_instruction(self.pc)
        # Ejecuta la instrucción normalmente
        super().step()
