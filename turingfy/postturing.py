class PostTuringMachine:
    def __init__(self, tape):
        self.tape = tape
        self.head = 0
        self.instructions = []
        self.state = "start"

    def add_instruction(self, state, symbol, new_symbol, move, new_state):
        self.instructions.append((state, symbol, new_symbol, move, new_state))

    def step(self):
        for state, symbol, new_symbol, move, new_state in self.instructions:
            if self.state == state and self.tape[self.head] == symbol:
                self.tape[self.head] = new_symbol
                self.head += 1 if move == "R" else -1
                self.state = new_state
                break

    def run(self):
        while self.state != "halt":
            self.step()


# Ejemplo de uso
tape = ["0", "1", "0", "0", "1"]
ptm = PostTuringMachine(tape)

# Agregar instrucciones: (estado actual, símbolo actual, nuevo símbolo, movimiento, nuevo estado)
ptm.add_instruction("start", "0", "1", "R", "start")
ptm.add_instruction("start", "1", "0", "R", "halt")

ptm.run()
print(ptm.tape)
