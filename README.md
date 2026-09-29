# Poople Solver

A command-line tool to solve word ladder puzzles.

## About

Poople finds the shortest path between a starting word and a target word by changing one letter at a time. Each intermediate step must also be a valid word.

**Note:** By default, the included dictionary contains only 4-letter words. To use words of different lengths, you must provide a custom JSON dictionary file.

## Features
- BFS pathfinding algorithm.
- Word validation utility.
- Statistics generation.
- Intuitive CLI.

## Installation

This project is built for use with [uv](https://github.com/astral-sh/uv).

### Cloning the repo

1. Clone the repository:
```bash
git clone https://github.com/PEvdDussen/poople-solver.git
cd poople-solver
```

2. Install the tool using `uv`:
```bash
uv tool install . --force
```

### Directly from GitHub

```bash
uv tool install git+https://github.com/PEvdDussen/poople-solver.git@v1.1.3
```

## Usage

### Finding paths
Find the shortest path from "PEEP" to "POOP":
```bash
poople find PEEP
```

### Validating words
Check if a word is in the current dictionary:
```bash
poople valid-word PEEP
```

### Generating statistics
Generate statistics for all words relative to a target:
```bash
poople complete-statistics --target POOP
```

### Advanced Usage
Use a custom dictionary JSON file to support words of different lengths:
```bash
poople find START --target HELLO --file path/to/five_letter_words.json
```

### CLI Options
A full list of commands and options can be found by running:
```bash
poople --help
```

### Command Shorthand
Several commands have hidden, shorthand versions for quicker typing:

| Command | Shorthand | Description |
| :--- | :--- | :--- |
| `find` | `fd` | Finds shortest paths. |
| `complete-statistics` | `cs` | Gathers and exports statistics. |
| `valid-word` | `vw` | Validates word existence. |


## Project Overview
- `src/`: Core logic and dictionary files.

## Contributing
Contributions are welcome!

## License
Apache 2.0
