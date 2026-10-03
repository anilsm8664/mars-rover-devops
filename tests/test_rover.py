import pytest
from rover import Plateau, Rover, RoverInputError, parse_plateau, parse_rover, process_input


def test_official_example(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text("5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM\n", encoding="utf-8")
    assert process_input(path) == ["1 3 N", "5 1 E"]


@pytest.mark.parametrize(("start", "command", "expected"), [
    ((1, 1, "N"), "L", "1 1 W"),
    ((1, 1, "N"), "R", "1 1 E"),
    ((1, 1, "N"), "M", "1 2 N"),
    ((1, 1, "E"), "M", "2 1 E"),
    ((1, 1, "S"), "M", "1 0 S"),
    ((1, 1, "W"), "M", "0 1 W"),
])
def test_basic_commands(start, command, expected):
    rover = Rover(*start, plateau=Plateau(5, 5))
    rover.execute(command)
    assert rover.position() == expected


def test_turning_wraps_around():
    rover = Rover(1, 1, "W", Plateau(5, 5))
    rover.execute("R")
    assert rover.direction == "N"


@pytest.mark.parametrize("command", ["X", "LXR", "MMZ"])
def test_invalid_command_is_rejected(command):
    rover = Rover(1, 1, "N", Plateau(5, 5))
    with pytest.raises(RoverInputError, match="Invalid command"):
        rover.execute(command)


def test_boundary_move_is_rejected():
    rover = Rover(5, 5, "N", Plateau(5, 5))
    with pytest.raises(RoverInputError, match="leave plateau"):
        rover.execute("M")


@pytest.mark.parametrize("direction", ["X", "Q", ""])
def test_invalid_direction_is_rejected(direction):
    with pytest.raises(RoverInputError, match="Invalid direction"):
        Rover(1, 1, direction, Plateau(5, 5))


def test_rover_outside_plateau_is_rejected():
    with pytest.raises(RoverInputError, match="outside the plateau"):
        Rover(6, 1, "N", Plateau(5, 5))


def test_invalid_plateau_is_rejected():
    with pytest.raises(RoverInputError):
        parse_plateau("5")


def test_negative_plateau_is_rejected():
    with pytest.raises(RoverInputError):
        parse_plateau("-1 5")


def test_invalid_rover_line_is_rejected():
    with pytest.raises(RoverInputError):
        parse_rover("1 2", Plateau(5, 5))


def test_odd_number_of_rover_lines_is_rejected(tmp_path):
    path = tmp_path / "invalid.txt"
    path.write_text("5 5\n1 2 N\n", encoding="utf-8")
    with pytest.raises(RoverInputError, match="position line followed"):
        process_input(path)


def test_empty_commands_are_rejected():
    rover = Rover(1, 1, "N", Plateau(5, 5))
    with pytest.raises(RoverInputError, match="cannot be empty"):
        rover.execute("")


def test_multiple_rovers_are_processed_sequentially(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text("2 2\n0 0 E\nMM\n2 2 S\nMM\n", encoding="utf-8")
    assert process_input(path) == ["2 0 E", "2 0 S"]
