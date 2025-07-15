import pytest

from turingfy.turing_machine import PostTuringMachine

program = [
    "START AGAIN",  # 0
    "GOTO 2",  # 1
    "IF #",
    "GOTO 29",  # 2-3
    "IF 0",
    "GOTO 9",  # 4-5
    "IF 1",
    "GOTO 17",  # 6-7
    "GOTO 30",  # 8
    "DELETE",  # 9
    "RIGHT TO THE END",  # 10
    "LEFT",  # 11
    "IF #",
    "GOTO 29",  # 12-13
    "IF 0",
    "GOTO 25",  # 14-15
    "GOTO 30",  # 16
    "DELETE",  # 17
    "RIGHT TO THE END",  # 18
    "LEFT",  # 19
    "IF #",
    "GOTO 29",  # 20-21
    "IF 1",
    "GOTO 25",  # 22-23
    "GOTO 30",  # 24
    "DELETE",  # 25
    "START AGAIN",  # 26
    "RIGHT",  # 27
    "GOTO 2",  # 28
    "YES",  # 29
    "NO",  # 30
]


def test_palindrome_odd():
    tape = list("10101")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["YES"]


def test_palindrome_even():
    tape = list("1001")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["YES"]


def test_palindrome_single():
    tape = list("1")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["YES"]


def test_palindrome_empty():
    tape = list("")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["YES"]


def test_not_palindrome_odd():
    tape = list("01101")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["NO"]


def test_not_palindrome_even():
    tape = list("1100")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["NO"]


def test_not_palindrome_two():
    tape = list("01")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["NO"]


def test_not_palindrome_three():
    tape = list("100")
    machine = PostTuringMachine(tape)
    machine.load_program(program)
    output = machine.run()
    assert output == ["NO"]
