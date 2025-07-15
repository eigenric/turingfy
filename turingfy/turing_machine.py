class PostTuringMachine:
    """
    Máquina de Turing capaz de ejecutar programas en el lenguaje Post Turing.
    """

    def __init__(self, tape=None):
        # Valida que la cinta no contenga espacios ni '#'
        if tape is not None:
            for c in tape:
                if c.isspace() or c == "#":
                    raise ValueError(
                        "La palabra de entrada no puede contener espacios ni el símbolo '#'"
                    )
        self.tape = list(tape) if tape is not None else []
        self.head = 0
        self.program = []
        self.labels = {}
        self.pc = 0  # Program counter
        self.halted = False
        self.output = []

    def load_program(self, program_lines):
        """
        Carga un programa Post Turing desde una lista de instrucciones sin numeración.
        """
        self.program = [
            line.strip()
            for line in program_lines
            if line.strip() and not line.strip().startswith("#")
        ]
        self.pc = 0
        self.halted = False

    def step(self):
        if self.halted or self.pc >= len(self.program):
            self.halted = True
            return
        # Debug
        print(
            f"PC: {self.pc:2d} | Instr: {self.program[self.pc]:15s} | Head: {self.head:2d} | Tape: {''.join(self.tape)} | Output: {self.output}"
        )
        instr = self.program[self.pc]
        instr_upper = instr.upper().strip()
        tokens = instr.split()
        if not tokens:
            self.pc += 1
            return

        # Instrucciones únicas
        if instr_upper == "START AGAIN":
            self.head = 0
            self.pc += 1
            return
        if instr_upper == "RIGHT TO THE END":
            self.head = len(
                self.tape
            )  # Posiciona después del último símbolo, sobre el '#' implícito
            self.pc += 1
            return

        op = tokens[0].upper()
        # Implementación de instrucciones típicas del lenguaje Post Turing
        if op == "IF":
            symbol = tokens[1]
            if self._read() == symbol:
                self.pc += 1
            else:
                self.pc += 2  # Saltar siguiente instrucción (GOTO)
        elif op == "GOTO":
            target = int(tokens[1])
            self.pc = target
        elif op == "DELETE":
            if 0 <= self.head < len(self.tape):
                self.tape[self.head] = "#"
            self.pc += 1
        elif op == "RIGHT":
            self.head = min(self.head + 1, len(self.tape))
            self.pc += 1
        elif op == "LEFT":
            self.head = max(self.head - 1, 0)
            self.pc += 1
        elif op in ("YES", "YES."):
            self.output.append("YES")
            self.halted = True
        elif op in ("NO", "NO."):
            self.output.append("NO")
            self.halted = True
        else:
            self.pc += 1

    def run(self, max_steps=10000):
        steps = 0
        while not self.halted and steps < max_steps:
            self.step()
            steps += 1
        return self.output

    def _read(self):
        if self.head >= len(self.tape):
            return "#"
        if 0 <= self.head < len(self.tape):
            return self.tape[self.head]
        return "_"

    def _write(self, symbol):
        # Si el símbolo es '_', elimina el carácter actual de la cinta
        if symbol == "_" and 0 <= self.head < len(self.tape):
            self.tape.pop(self.head)
            # Si la cabeza queda fuera tras borrar el último, ajústala
            if self.head > len(self.tape):
                self.head = len(self.tape)
        elif 0 <= self.head < len(self.tape):
            self.tape[self.head] = symbol

    def reset(self, tape=None):
        self.tape = list(tape) if tape is not None else []
        if not self.tape or self.tape[-1] != "#":
            self.tape.append("#")
        self.head = 0
        self.pc = 0
        self.halted = False
        self.output = []
