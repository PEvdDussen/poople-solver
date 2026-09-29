import json
import re
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from poople.base import app
from poople.finder import DEFAULT_WORD_LIST

console = Console()


@app.command(name="valid-word")
def validate_word(
    word: Annotated[str, typer.Argument(help="The word to validate.")],
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
):
    """Check if a word exists in the dictionary."""
    search_word = re.sub(r"[^A-Za-z]", "", word).upper()

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        cleaned_words = {
            re.sub(r"[^A-Za-z]", "", w).upper()
            for w in data
            if isinstance(w, str)
        }
    except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
        console.print(f"[bold red]Error loading file:[/bold red] {e}")
        raise typer.Exit(code=1)

    if search_word in cleaned_words:
        console.print(f"[bold green]'{search_word}' is a valid word.[/bold green]")
        raise typer.Exit(code=0)
    else:
        console.print(f"[bold red]'{search_word}' is not in the dictionary.[/bold red]")
        raise typer.Exit(code=1)


app.command(name="vw", hidden=True)(validate_word)
