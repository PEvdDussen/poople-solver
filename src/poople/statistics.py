import json
import re
from datetime import datetime
from pathlib import Path
from typing import Annotated

import polars as pl
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from poople.base import app
from poople.finder import DEFAULT_WORD_LIST, find_shortest_paths

console = Console()


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

    stats_df = pl.DataFrame(stats_data).sort("ShortestPathLength", descending=True)

    freq_cols = [f"word -{i}" for i in range(last_n, 0, -1)]
    freq_df = pl.DataFrame(frequency_data, schema=freq_cols)
    freq_final = (
        freq_df.group_by(freq_cols)
        .agg(pl.len().alias("Frequency"))
        .sort("Frequency", descending=True)
    )

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


app.command(name="cs", hidden=True)(complete_statistics)
