import typer

app = typer.Typer(
    name="Poople Solver",
    help="Find the shortest word ladder path from START_WORD to TARGET_WORD.",
    add_completion=False,
)
