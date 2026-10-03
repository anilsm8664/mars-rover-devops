#!/usr/bin/env python3
"""Mars Rover command-line application."""
from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

LOG = logging.getLogger(__name__)
DIRECTIONS = ("N", "E", "S", "W")
VALID_COMMANDS = frozenset("LRM")


class RoverInputError(ValueError):
    """Raised when rover input is invalid."""


@dataclass
class Plateau:
    max_x: int
    max_y: int

    def contains(self, x: int, y: int) -> bool:
        return 0 <= x <= self.max_x and 0 <= y <= self.max_y


@dataclass
class Rover:
    x: int
    y: int
    direction: str
    plateau: Plateau

    def __post_init__(self) -> None:
        if self.direction not in DIRECTIONS:
            raise RoverInputError(f"Invalid direction: {self.direction}")
        if not self.plateau.contains(self.x, self.y):
            raise RoverInputError(
                f"Rover position ({self.x}, {self.y}) is outside the plateau"
            )

    def turn_left(self) -> None:
        index = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(index - 1) % len(DIRECTIONS)]

    def turn_right(self) -> None:
        index = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(index + 1) % len(DIRECTIONS)]

    def move(self) -> None:
        next_x, next_y = self.x, self.y
        if self.direction == "N":
            next_y += 1
        elif self.direction == "E":
            next_x += 1
        elif self.direction == "S":
            next_y -= 1
        else:
            next_x -= 1

        if not self.plateau.contains(next_x, next_y):
            raise RoverInputError(
                f"Move would leave plateau: ({self.x}, {self.y}) -> ({next_x}, {next_y})"
            )
        self.x, self.y = next_x, next_y

    def execute(self, commands: str) -> None:
        normalized = commands.strip().upper()
        if not normalized:
            raise RoverInputError("Rover command string cannot be empty")
        invalid = sorted(set(normalized) - VALID_COMMANDS)
        if invalid:
            raise RoverInputError(f"Invalid command(s): {', '.join(invalid)}")
        for command in normalized:
            if command == "L":
                self.turn_left()
            elif command == "R":
                self.turn_right()
            else:
                self.move()

    def position(self) -> str:
        return f"{self.x} {self.y} {self.direction}"


def parse_plateau(line: str) -> Plateau:
    parts = line.split()
    if len(parts) != 2:
        raise RoverInputError("Plateau line must contain exactly two coordinates")
    try:
        max_x, max_y = (int(value) for value in parts)
    except ValueError as exc:
        raise RoverInputError("Plateau coordinates must be integers") from exc
    if max_x < 0 or max_y < 0:
        raise RoverInputError("Plateau coordinates cannot be negative")
    return Plateau(max_x, max_y)


def parse_rover(line: str, plateau: Plateau) -> Rover:
    parts = line.split()
    if len(parts) != 3:
        raise RoverInputError("Rover position must contain x, y and direction")
    try:
        x, y = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise RoverInputError("Rover coordinates must be integers") from exc
    return Rover(x, y, parts[2].upper(), plateau)


def process_input(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RoverInputError(f"Unable to read input file: {exc}") from exc
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        raise RoverInputError("Input file is empty")

    plateau = parse_plateau(lines[0])
    rover_lines = lines[1:]
    if len(rover_lines) % 2 != 0:
        raise RoverInputError("Each rover must have a position line followed by commands")

    results: list[str] = []
    for index in range(0, len(rover_lines), 2):
        rover = parse_rover(rover_lines[index], plateau)
        commands = rover_lines[index + 1]
        LOG.info("Processing rover at %s with %d command(s)", rover.position(), len(commands))
        rover.execute(commands)
        results.append(rover.position())
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute NASA Mars Rover navigation instructions.")
    parser.add_argument("input_file", type=Path, help="Path to the rover input file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        for result in process_input(args.input_file):
            print(result)
    except RoverInputError as exc:
        LOG.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
