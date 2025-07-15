"""Implementación de una máquina de Turing de una cita determinista."""

LEFT = "L"
RIGHT = "R"


class Tape:
    """Representa una cinta infinita"""

    def __init__(self, word):
        self.word = word
        self.head = 0
        self.state = 0


class TMachine:
    """Representa una máquina de Turing"""

    def __init__(self, word, initial_state, transitions):
        self.tape = Tape(word)
        self.tape.state = initial_state

        self.run(transitions)

    def write_symbol(word, index, new_char):
        return word[:index] + new_char + word[index + 1 :]

    def run(self, transitions):
        for read_symbol, write_symbol, action, state in transitions:
            i = self.tape.head
            if self.tape.word[i] == read_symbol:
                self.tape.word = write_symbol(self.tape.word, i, write_symbol)

            if action == LEFT:
                self.tape.head -= 1
            elif action == RIGHT:
                self.tape.head += 1
