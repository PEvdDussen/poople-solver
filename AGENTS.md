# AGENTS.md

This document provides an overview of the `Poople_Solver` codebase, intended to assist in navigation, development, and maintenance.

## Project Overview

`Poople_Solver` is a command-line tool designed to solve word ladder puzzles, finding the shortest path between a starting word and a target word by changing one letter at a time. It uses a Breadth-First Search (BFS) algorithm to ensure the shortest path is found.

## Codebase Structure

The project follows a standard Python package structure:

- `src/poople/`: The main package containing the source code.
  - `src/poople/__init__.py`: Contains the core BFS algorithm and CLI implementation.
  - `src/poople/poople_words.json`: The default dictionary file containing a list of 4-letter words.
- `pyproject.toml`: Project configuration and dependencies.
- `uv.lock`: Lockfile for reproducible dependencies, managed by `uv`.

## Interacting with the Tool

### Installation

This project is designed to be installed and managed using [uv](https://github.com/astral-sh/uv).

```bash
uv tool install .
```

### Basic Usage

Find the shortest path from a starting word to the default target "POOP":

```bash
poople START_WORD
```

### Advanced Usage

For custom targets or different dictionaries (e.g., to support different word lengths):

```bash
poople START --target HELLO --file path/to/five_letter_words.json
```

To see all available shortest paths of the same length:

```bash
poople START -a
```

### Help

For a full list of commands and options:

```bash
poople --help
```

## Development and Maintenance

### Prerequisites

- [Python](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv)

### Running/Testing

As this is a tool, you can run it directly from the source during development using `uv run`:

```bash
uv run poople --help
```

### Dictionary Updates

To add or remove words, modify `src/poople/poople_words.json`. Ensure it remains a valid JSON array of strings.
