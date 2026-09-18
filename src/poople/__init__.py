import importlib.resources
import json
import re
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Annotated

import polars as pl
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
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
        return []

    if target_word not in word_set:
        return []

    if len(start_word) != len(target_word):
        return []

    queue = deque([(start_word, [start_word])])
    visited = {start_word}
    shortest_paths = []
    shortest_length = None
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    while queue:
        level_size = len(queue)
        level_visited = set()

        for _ in range(level_size):
            current_word, path = queue.popleft()

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

        visited.update(level_visited)

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


@app.command(name="find")
def find(
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

    if start not in words:
        console.print(
            f"[bold red]Error:[/bold red] Start word '{start}' is not in the dictionary."
        )
        raise typer.Exit(code=1)

    if target not in words:
        console.print(
            f"[bold red]Error:[/bold red] Target word '{target}' is not in the dictionary."
        )
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


@app.command(name="complete-statistics")
def complete_statistics(
    target_word: Annotated[
        str,
        typer.Option("--target", "-t", help="The destination word."),
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
    output_stats: Annotated[
        Path | None,
        typer.Option("--output-stats", "-os", help="Path to output statistics CSV."),
    ] = None,
    output_frequency: Annotated[
        Path | None,
        typer.Option("--output-frequency", "-of", help="Path to output frequency CSV."),
    ] = None,
    last_n: Annotated[
        int,
        typer.Option(
            "--last-number", "-ln", help="Number of last words to track frequency for."
        ),
    ] = 3,
):
    """Runs BFS for every word in the dictionary and gathers statistics."""
    target = target_word.upper()
    timestamp = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime(
        "%Y-%m-%d_%H-%M-%S"
    )
    dict_name = file_path.stem

    console.print(f"[bold blue]Loading dictionary from:[/bold blue] {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        cleaned_words = {
            re.sub(r"[^A-Za-z]", "", word).upper()
            for word in data
            if isinstance(word, str)
        }
        words = sorted({word for word in cleaned_words if word})
    except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
        console.print(f"[bold red]Error loading file:[/bold red] {e}")
        raise typer.Exit(code=1)

    stats_data = []
    frequency_data = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(
            f"[cyan]Running BFS for {len(words)} words...", total=len(words)
        )

        for start_word in words:
            paths = find_shortest_paths(start_word, target, set(words), find_all=True)

            path_len = len(paths[0]) - 1 if paths else 0
            path_count = len(paths)

            word_freqs = {}
            for path in paths:
                for word in path:
                    word_freqs[word] = word_freqs.get(word, 0) + 1

                # Capture Last-N
                last_n_seq = (
                    path[-last_n:]
                    if len(path) >= last_n
                    else ([""] * (last_n - len(path)) + path)
                )
                frequency_data.append(last_n_seq)

            stats_data.append(
                {
                    "StartWord": start_word,
                    "ShortestPathLength": path_len,
                    "NumberOfShortestPaths": path_count,
                    "SolutionFrequency": word_freqs.get(start_word, 0),
                }
            )

            progress.advance(task)

    stats_df = pl.DataFrame(stats_data)

    freq_cols = [f"word -{i}" for i in range(last_n, 0, -1)]
    freq_df = pl.DataFrame(frequency_data, schema=freq_cols)
    freq_final = freq_df.group_by(freq_cols).agg(pl.len().alias("Frequency"))

    stats_out = output_stats or Path(
        f"./word_stats_{target}_{dict_name}_created_{timestamp}.csv"
    )
    freq_out = output_frequency or Path(
        f"./last_{last_n}_frequency_{target}_{dict_name}_created_{timestamp}.csv"
    )

    stats_df.write_csv(stats_out)
    freq_final.write_csv(freq_out)

    console.print(f"[bold green]Statistics saved to:[/bold green] {stats_out}")
    console.print(f"[bold green]Frequency saved to:[/bold green] {freq_out}")


# Aliases
app.command(name="fd", hidden=True)(find)
app.command(name="cs", hidden=True)(complete_statistics)

if __name__ == "__main__":
    app()
