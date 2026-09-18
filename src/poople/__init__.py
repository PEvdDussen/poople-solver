import importlib.resources
import json
import re
from collections import deque
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

app = typer.Typer(
    name="Poople Solver",
    help="Find the shortest word ladder path from START_WORD to TARGET_WORD.",
    add_completion=False,
)
console = Console()
DEFAULT_WORD_LIST = Path(
    str(importlib.resources.files("poople").joinpath("poople_words.json"))
)


def find_shortest_paths(
    start_word: str, target_word: str, word_set: set[str], find_all: bool = False
) -> list[list[str]]:
    """Runs BFS to find the shortest single-letter transformation path(s)."""
    if start_word not in word_set:
        console.print(
            f"[bold red]Error:[/bold red] Start word '{start_word}' is not in the dictionary."
        )
        return []

    if target_word not in word_set:
        console.print(
            f"[bold red]Error:[/bold red] Target word '{target_word}' is not in the dictionary."
        )
        return []

    if len(start_word) != len(target_word):
        console.print(
            "[bold red]Error:[/bold red] Start and target words must be the same length."
        )
        return []

    queue = deque([(start_word, [start_word])])
    visited = {start_word}
    shortest_paths = []
    shortest_length = None
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    while queue:
        # Number of nodes at the current BFS level
        level_size = len(queue)
        level_visited = set()

        for _ in range(level_size):
            current_word, path = queue.popleft()

            # If we've already found shortest paths and current path is longer, stop
            if shortest_length and len(path) > shortest_length:
                break

            if current_word == target_word:
                shortest_paths.append(path)
                shortest_length = len(path)
                if not find_all:
                    return shortest_paths
                continue

            for i in range(len(current_word)):
                for char in alphabet:
                    if char == current_word[i]:
                        continue

                    neighbor = current_word[:i] + char + current_word[i + 1 :]

                    if neighbor in word_set and neighbor not in visited:
                        level_visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

        # Update global visited set only after processing the entire BFS level
        visited.update(level_visited)

        # If we reached target paths at this level, don't explore deeper levels
        if shortest_paths:
            break

    return shortest_paths


def build_tree(paths: list[list[str]]) -> Tree:
    """Builds a Rich Tree from a list of shortest paths with level-based coloring."""
    palette = ["cyan", "yellow", "green", "blue", "magenta"]
    root_word = paths[0][0]
    root_color = palette[0 % len(palette)]
    tree = Tree(Text(root_word, style=root_color))

    for path in paths:
        current_node = tree
        for i, word in enumerate(path[1:], 1):
            color = palette[i % len(palette)]

            # Check if this word is already a child of the current node
            found = False
            for child in current_node.children:
                # Compare the plain text of the node label
                if isinstance(child.label, Text):
                    if child.label.plain == word:
                        current_node = child
                        found = True
                        break
                elif str(child.label) == word:  # Fallback
                    current_node = child
                    found = True
                    break

            if not found:
                current_node = current_node.add(Text(word, style=color))

    return tree


# @app.callback(invoke_without_command=True)
@app.command()
def main(
    start_word: Annotated[
        str, typer.Argument(help="The starting word for the ladder.")
    ],
    target_word: Annotated[
        str,
        typer.Option("--target", "-t", help="The destination word (defaults to POOP)."),
    ] = "POOP",
    file_path: Annotated[
        Path,
        typer.Option(
            "--file",
            "-f",
            help="Path to the JSON word list file.",
            exists=True,
            readable=True,
        ),
    ] = DEFAULT_WORD_LIST,
    find_all: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="Print all shortest paths equivalent in length instead of just the first.",
        ),
    ] = False,
    graph: Annotated[
        bool,
        typer.Option(
            "--graph",
            "-g",
            help="Output shortest paths as a tree structure.",
        ),
    ] = False,
):
    """Finds the shortest word ladder path from START_WORD to TARGET_WORD."""
    start = start_word.upper()
    target = target_word.upper()

    # If graph is requested, find_all must be True
    if graph:
        find_all = True

    console.print(f"[bold blue]Loading dictionary from:[/bold blue] {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        cleaned_words = {
            re.sub(r"[^A-Za-z]", "", word).upper()
            for word in data
            if isinstance(word, str)
        }
        words = {word for word in cleaned_words if word}
    except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
        console.print(f"[bold red]Error loading file:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold blue]Searching path:[/bold blue] {start} -> {target}...\n")
    paths = find_shortest_paths(start, target, words, find_all=find_all)

    if paths:
        steps = len(paths[0]) - 1
        title_text = f"[bold green]Found {len(paths)} Shortest Path(s) ({steps} steps)[/bold green]"

        if graph:
            console.print(title_text)
            console.print(build_tree(paths))
        else:
            formatted_paths = []
            for path in paths:
                formatted_paths.append(
                    " [bold green]->[/bold green] ".join(
                        [f"[cyan]{word}[/cyan]" for word in path]
                    )
                )

            console.print(
                Panel(
                    "\n".join(formatted_paths),
                    title=title_text,
                    expand=False,
                )
            )
    else:
        console.print(
            f"[bold red]No path found[/bold red] between '{start}' and '{target}'."
        )


if __name__ == "__main__":
    app()
