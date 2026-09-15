# Poople Solver

A command-line tool to solve word ladder puzzles.

## About

Poople finds the shortest path between a starting word and a target word by changing one letter at a time. Each intermediate step must also be a valid word.

**Note:** By default, the included dictionary contains only 4-letter words. To use words of different lengths, you must provide a custom JSON dictionary file.

## Features
- BFS pathfinding algorithm.
- Configurable dictionary (use `-f` for different word lengths).
- Intuitive CLI.

## Installation

This project is built for use with [uv](https://github.com/astral-sh/uv).

1. Clone the repository:
   ```bash
   git clone https://github.com/PEvdDussen/poople-solver.git
   cd poople-solver
   ```

2. Install the tool using `uv`:
   ```bash
   uv tool install .
   ```

## Usage

### Basic Example
Find the shortest path from "PEEP" to "POOP":
```bash
poople PEEP
```

**Output:**
```text
Loading dictionary from: .\src\poople\poople_words.json
Searching path: PEEP -> POOP...
╭─ Found 1 Shortest Path(s) (3 steps) ─╮
│ PEEP -> PREP -> PROP -> POOP         │
╰──────────────────────────────────────╯
```

### Advanced Usage
Use a custom dictionary JSON file to support words of different lengths:
```bash
poople START --target HELLO --file path/to/five_letter_words.json
```

### CLI Options
An explanation of all the functionality of the tool can be found by running
```bash
poople --help
```

**Output**
```text
Usage: poople [OPTIONS] {start_word}                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                               
 Finds the shortest word ladder path from START_WORD to TARGET_WORD.                                                                                                                                                                                           
                                                                                                                                                                                                                                                               
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    start_word      <str>  The starting word for the ladder. [required]                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --target  -t      <str>   The destination word (defaults to POOP). [default: POOP]                           │
│ --file    -f      <path>  Path to the JSON word list file. [default: .\src\poople\poople_words.json]         │
│ --all     -a              Print all shortest paths equivalent in length instead of just the first.           │
│ --help                    Show this message and exit.                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Project Overview
- `src/`: Core logic and dictionary files.

## Contributing
Contributions are welcome!

## License
Apache 2.0
